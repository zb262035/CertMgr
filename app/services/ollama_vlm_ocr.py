"""Ollama VLM OCR Provider for certificate recognition.

Uses local Ollama vision models (glm-ocr, qwen2.5vl) via REST API.
Uses Pillow for cross-platform image preprocessing (works on both macOS and Linux).
"""

import os
import re
import json
import base64
import tempfile
import time
from typing import Optional

from PIL import Image

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


def preprocess_image_pillow(image_path: str, target_width: int = 1024) -> str:
    """Preprocess image using Pillow (cross-platform).

    Resizes image to target_width while preserving aspect ratio.
    Saves as JPEG to a temp file.

    Returns:
        Path to preprocessed image (caller must clean up).
    """
    try:
        with Image.open(image_path) as img:
            orig_w, orig_h = img.size
            if orig_w <= target_width:
                # No need to resize, just convert to JPEG
                out_path = image_path + ".processed.jpg"
                img.convert("RGB").save(out_path, "JPEG", quality=85)
                return out_path

            # Calculate new size maintaining aspect ratio
            ratio = target_width / max(orig_w, orig_h)
            new_size = (int(orig_w * ratio), int(orig_h * ratio))

            # Resize and save
            out_fd, out_path = tempfile.mkstemp(suffix=".jpg")
            os.close(out_fd)
            resized = img.convert("RGB").resize(new_size, Image.Resampling.LANCZOS)
            resized.save(out_path, "JPEG", quality=85)
            return out_path
    except Exception:
        # Fallback: return original path
        return image_path


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
        preprocessed = preprocess_image_pillow(image_path, target_width=1024)
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
