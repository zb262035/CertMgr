"""Ollama VLM OCR Provider for certificate recognition.

Uses local Ollama vision models (glm-ocr, qwen2.5vl) via REST API.
Includes sips-based image preprocessing (macOS built-in, no Pillow needed).
"""

import os
import re
import json
import base64
import subprocess
import tempfile
import time
from typing import Optional

import requests

OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_API_TAGS = "http://localhost:11434/api/tags"

# Model preferences (in order of priority)
DEFAULT_MODELS = ["glm-ocr:latest", "qwen2.5vl:7b"]

PROMPT = (
    "这是一张证书图片，请提取所有文字内容，包括姓名、证书名称、颁发单位、日期等关键信息。"
    "请按图片中的顺序逐行输出文字，不要省略任何内容。"
)


def check_ollama_available() -> bool:
    """Check if Ollama service is running."""
    try:
        r = requests.get("http://localhost:11434", timeout=5)
        return r.status_code == 200
    except:
        return False


def get_available_vlm_model() -> Optional[str]:
    """Return the first available VLM from DEFAULT_MODELS, or None."""
    try:
        r = requests.get(OLLAMA_API_TAGS, timeout=5)
        if r.status_code != 200:
            return None
        models = {m["name"] for m in r.json().get("models", [])}
        for preferred in DEFAULT_MODELS:
            if preferred in models:
                return preferred
            # Also match without :latest suffix
            base = preferred.split(":")[0]
            for m in models:
                if m.startswith(base):
                    return m
        return None
    except:
        return None


def preprocess_image_sips(image_path: str, target_width: int = 1024) -> str:
    """Preprocess image using macOS sips (no Pillow dependency).

    Resizes image to target_width while preserving aspect ratio.
    Saves as JPEG to a temp file.

    Returns:
        Path to preprocessed image (caller must clean up).
    """
    img = _get_image_dimensions(image_path)
    if img is None:
        # Cannot read dimensions, return original
        return image_path

    orig_w, orig_h = img
    if orig_w <= target_width:
        # No need to resize, just convert to JPEG
        out_path = image_path + ".sips.jpg"
        subprocess.run(["sips", "-s", "format", "jpeg", image_path, "--out", out_path], check=False)
        return out_path

    out_fd, out_path = tempfile.mkstemp(suffix=".jpg")
    os.close(out_fd)

    # sips -Z sets the longest edge to given pixels
    result = subprocess.run(
        ["sips", "-Z", str(target_width), image_path, "--out", out_path],
        capture_output=True, check=False
    )
    if result.returncode != 0:
        # Fallback: return original path
        try:
            os.remove(out_path)
        except:
            pass
        return image_path

    return out_path


def _get_image_dimensions(image_path: str) -> Optional[tuple]:
    """Get image dimensions using sips."""
    try:
        result = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", image_path],
            capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            return None
        w = h = None
        for line in result.stdout.splitlines():
            if "pixelWidth" in line:
                w = int(line.split(":")[-1].strip())
            if "pixelHeight" in line:
                h = int(line.split(":")[-1].strip())
        if w and h:
            return (w, h)
        return None
    except:
        return None


def call_ollama_vision(model: str, image_path: str, timeout: int = 120) -> tuple[list[str], dict]:
    """Call Ollama vision model for OCR.

    Args:
        model: Ollama model name (e.g. 'glm-ocr:latest')
        image_path: Path to image file
        timeout: Request timeout in seconds

    Returns:
        (list of text lines, metadata dict with 'model' and 'elapsed')
    """
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    payload = {
        "model": model,
        "prompt": PROMPT,
        "images": [img_b64],
        "stream": False,
    }

    start = time.time()
    response = requests.post(OLLAMA_API, json=payload, timeout=timeout)
    elapsed = time.time() - start

    response.raise_for_status()
    result = response.json()
    text = result.get("response", "").strip()

    # Split into lines, filter empty
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    metadata = {
        "model": model,
        "elapsed": round(elapsed, 2),
        "raw_text_len": len(text),
    }

    return lines, metadata


class OllamaVLMOCR:
    """Ollama Vision Model OCR provider.

    Usage:
        ocr = OllamaVLMOCR()
        if ocr.is_available():
            lines, meta = ocr.recognize("/path/to/cert.jpg")
    """

    def __init__(self, preferred_model: Optional[str] = None):
        self.model = preferred_model
        self._available = None

    def is_available(self) -> bool:
        """Check if Ollama VLM OCR is available."""
        if not check_ollama_available():
            return False
        if self.model:
            return True
        self.model = get_available_vlm_model()
        return self.model is not None

    def recognize(self, image_path: str) -> tuple[list[str], dict]:
        """Run OCR on an image file.

        Args:
            image_path: Path to image or PDF (PDF must be converted first)

        Returns:
            (text_lines, metadata) where metadata includes 'model', 'elapsed', 'error'
        """
        if not self.is_available():
            return [], {"error": "Ollama VLM not available", "model": None, "elapsed": 0}

        # Preprocess
        preprocessed = preprocess_image_sips(image_path, target_width=1024)
        needs_cleanup = preprocessed != image_path

        try:
            lines, meta = call_ollama_vision(self.model, preprocessed)
            meta["preprocessed"] = preprocessed
            return lines, meta
        except requests.exceptions.Timeout:
            return [], {"error": "OCR timeout", "model": self.model, "elapsed": 0}
        except requests.exceptions.HTTPError as e:
            return [], {"error": f"HTTP {e.response.status_code}", "model": self.model, "elapsed": 0}
        except Exception as e:
            return [], {"error": str(e), "model": self.model, "elapsed": 0}
        finally:
            if needs_cleanup:
                try:
                    os.remove(preprocessed)
                except:
                    pass
