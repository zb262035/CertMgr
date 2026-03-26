"""OCR Service using PaddleOCR for local certificate recognition.

Optimized version with:
- Image preprocessing (grayscale, contrast enhancement, sharpening)
- PDF DPI increased to 300 for better quality
- Confidence detection and quality assessment
- Post-processing to filter noise
- Graceful degradation when OCR quality is low
"""

import os
import re
from datetime import datetime
from typing import Optional
from paddleocr import PaddleOCR
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# Initialize PaddleOCR (Chinese + English)
# OCR results cached in class to avoid re-initialization
_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = PaddleOCR(lang='ch')
    return _ocr_engine


def preprocess_image(image_path: str) -> str:
    """Preprocess image for better OCR results.

    Steps:
    1. Open image and resize if too small
    2. Convert to grayscale
    3. Enhance contrast
    4. Sharpen image

    Returns:
        Path to preprocessed temporary image
    """
    img = Image.open(image_path)

    # Resize if image is too small (OCR works better on larger images)
    min_size = 800
    if img.width < min_size or img.height < min_size:
        ratio = max(min_size / img.width, min_size / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # Convert to grayscale
    img = img.convert('L')

    # Enhance contrast (1.5x - 2.0x)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)

    # Sharpen image
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)

    # Save preprocessed image
    temp_path = image_path + '.preprocessed.png'
    img.save(temp_path, 'PNG')

    return temp_path


def convert_pdf_to_image(file_path: str, dpi: int = 300) -> str:
    """Convert PDF to image with higher DPI.

    Args:
        file_path: Path to PDF file
        dpi: DPI for conversion (default 300, higher = better quality)

    Returns:
        Path to converted image file
    """
    images = pdf2image.convert_from_path(file_path, dpi=dpi)
    if not images:
        raise ValueError('PDF转换失败 / PDF conversion failed')

    # Use first page
    image_path = file_path + '.tmp.png'
    images[0].save(image_path, 'PNG')

    return image_path


def calculate_text_quality(text_lines: list) -> dict:
    """Calculate OCR quality metrics.

    Returns:
        dict with keys: score (0-100), char_count, line_count,
                       noise_ratio, has_chinese, issues (list)
    """
    if not text_lines:
        return {
            'score': 0,
            'char_count': 0,
            'line_count': 0,
            'noise_ratio': 1.0,
            'has_chinese': False,
            'issues': ['无文字识别 / No text recognized']
        }

    full_text = '\n'.join(text_lines)
    char_count = len(full_text)
    line_count = len(text_lines)

    # Check for Chinese characters
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', full_text))

    # Check for noise patterns (lots of random characters, garbled text)
    # Common noise patterns from watermarked/digital certificates
    noise_patterns = [
        r'[a-z]{5,}[a-z]',  # Long random english strings
        r'\d{10,}',          # Long number sequences
        r'[a-z0-9]{20,}',    # Long alphanumeric strings
    ]

    noise_matches = 0
    for pattern in noise_patterns:
        noise_matches += len(re.findall(pattern, full_text, re.IGNORECASE))

    # Calculate noise ratio
    noise_ratio = noise_matches / max(char_count, 1)

    # Identify issues
    issues = []

    # No Chinese - likely failed
    if not has_chinese and char_count > 10:
        issues.append('未识别到中文字符 / No Chinese characters detected')

    # High noise ratio
    if noise_ratio > 0.1:
        issues.append(f'噪声比例过高 ({noise_ratio:.1%}) / High noise ratio')

    # Very short text for complex image
    if char_count < 10:
        issues.append('识别文字过少 / Too little text recognized')

    # Calculate overall score (0-100)
    score = 100

    # Deduct for issues
    if not has_chinese:
        score -= 50
    score -= noise_ratio * 100
    if len(issues) > 0:
        score -= len(issues) * 10

    # Low text density
    if line_count > 0 and char_count / line_count < 3:
        score -= 20

    score = max(0, min(100, score))

    return {
        'score': score,
        'char_count': char_count,
        'line_count': line_count,
        'noise_ratio': noise_ratio,
        'has_chinese': has_chinese,
        'issues': issues
    }


def clean_text(text_lines: list) -> list:
    """Clean OCR text by removing noise lines.

    Filters out:
    - Lines with mostly random characters
    - Very short meaningless lines
    - Lines that are just numbers
    """
    cleaned = []

    for line in text_lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip lines that are only numbers or very short
        if len(line) <= 2 and (line.isdigit() or line.isalpha()):
            continue

        # Skip lines with too many random-looking characters
        # (e.g., "2025sdjnds" is likely noise)
        if len(line) > 5:
            # Count ratio of alphanumeric to total
            alphanum_count = len(re.findall(r'[a-zA-Z0-9]', line))
            if alphanum_count / len(line) > 0.8 and not re.search(r'[\u4e00-\u9fff]', line):
                # Looks like random alphanumeric, skip if no Chinese
                continue

        # Skip lines that are clearly noise (long strings of random chars)
        if re.match(r'^[a-z0-9]{15,}$', line, re.IGNORECASE):
            continue

        cleaned.append(line)

    return cleaned


# Type detection keywords
TYPE_KEYWORDS = {
    '比赛获奖证书': ['竞赛', '比赛', '获奖', '一等奖', '二等奖', '三等奖', '优秀奖', '冠军', '名次', '获奖证书'],
    '荣誉证书': ['荣誉', '授予', '称号', '荣誉称号', '授予单位'],
    '资格证': ['资格证书', '职业资格', '证书编号', '有效期', '资格'],
    '职业技能等级证书': ['职业技能', '等级证书', '初级工', '中级工', '高级工', '技师', '高级技师'],
}


class OCRService:
    """Service for OCR-based certificate recognition."""

    @classmethod
    def recognize_certificate(cls, file_path: str, file_mime_type: str) -> dict:
        """Recognize certificate from image or PDF file.

        Args:
            file_path: Path to the certificate file
            file_mime_type: MIME type (image/png, image/jpeg, application/pdf)

        Returns:
            dict with keys:
            - success (bool): Whether OCR succeeded
            - text (str): Full recognized text
            - type (str): Certificate type
            - fields (dict): Extracted fields
            - title (str): Extracted title
            - confidence (dict): Quality metrics
            - error (str): Error message if failed
        """
        temp_files = []  # Track temp files for cleanup
        original_path = file_path

        try:
            # Step 1: Convert PDF to image if needed
            if file_mime_type == 'application/pdf':
                try:
                    file_path = convert_pdf_to_image(file_path, dpi=300)
                    temp_files.append(file_path)
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'PDF转换失败 / PDF conversion failed: {str(e)}',
                        'confidence': {'score': 0, 'issues': ['PDF转换失败']}
                    }

            # Step 2: Preprocess image for better OCR
            try:
                preprocessed_path = preprocess_image(file_path)
                temp_files.append(preprocessed_path)
            except Exception as e:
                # Fallback to original if preprocessing fails
                preprocessed_path = file_path

            # Step 3: Run OCR
            try:
                ocr = get_ocr_engine()
                result = ocr.predict(preprocessed_path)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'OCR识别失败 / OCR recognition failed: {str(e)}',
                    'confidence': {'score': 0, 'issues': ['OCR识别失败']}
                }

            # Step 4: Parse OCR result
            text_lines = []
            for res in result:
                if isinstance(res, dict):
                    for text in res.get('rec_texts', []):
                        text_lines.append(text)
                elif isinstance(res, list) and len(res) >= 2:
                    text_lines.append(res[1][0])

            # Step 5: Calculate quality metrics
            quality = calculate_text_quality(text_lines)

            # Step 6: Clean text
            cleaned_lines = clean_text(text_lines)
            full_text = '\n'.join(cleaned_lines)

            # Step 7: If quality is too low, return with warning
            if quality['score'] < 30:
                return {
                    'success': False,
                    'text': full_text,
                    'type': None,
                    'fields': {},
                    'title': None,
                    'confidence': quality,
                    'error': '识别质量过低，请手动输入 / Recognition quality too low, please enter manually'
                }

            # Step 8: Detect certificate type
            cert_type = cls.detect_type(full_text)

            # Step 9: Extract fields using LLM (with fallback to keyword matching)
            fields = {}
            title = None
            llm_used = False

            try:
                from app.services.llm_service import extract_fields_with_llm, check_ollama_status

                # Check if Ollama is available
                ollama_status = check_ollama_status()
                if ollama_status.get("available"):
                    # Use LLM for field extraction
                    llm_result = extract_fields_with_llm(full_text, cert_type)
                    if llm_result.get("success"):
                        fields = llm_result.get("fields", {})
                        title = llm_result.get("title")
                        # Update quality score with LLM extraction confidence
                        if llm_result.get("confidence"):
                            quality = llm_result["confidence"]
                        llm_used = True
            except Exception as e:
                # LLM extraction failed, use fallback
                pass

            # Fallback to keyword matching if LLM not used or failed
            if not fields:
                fields = cls.extract_fields(full_text, cert_type)
                title = cls.extract_title(cleaned_lines, cert_type)

            return {
                'success': True,
                'text': full_text,
                'type': cert_type,
                'fields': fields,
                'title': title,
                'confidence': quality,
                'llm_used': llm_used,
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'OCR处理异常 / OCR processing error: {str(e)}',
                'confidence': {'score': 0, 'issues': [str(e)]}
            }

        finally:
            # Cleanup temp files
            for temp_file in temp_files:
                if temp_file != original_path and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass

    @classmethod
    def detect_type(cls, text: str) -> str:
        """Auto-detect certificate type based on text content.

        Returns one of: 比赛获奖证书, 荣誉证书, 资格证, 职业技能等级证书, or '特殊证书' (special)
        """
        text_lower = text.lower()
        scores = {}

        for cert_type, keywords in TYPE_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            if score > 0:
                scores[cert_type] = score

        if not scores:
            return '特殊证书'  # Special/unrecognized type

        # Return type with highest score
        return max(scores, key=scores.get)

    @classmethod
    def extract_fields(cls, text: str, cert_type: str) -> dict:
        """Extract dynamic fields based on certificate type.

        Returns dict of field_name -> value mappings.
        """
        fields = {}

        if cert_type == '比赛获奖证书':
            fields['competition_name'] = cls.extract_field(text, ['比赛名称', '竞赛名称', '赛事名称'])
            fields['award_level'] = cls.extract_field(text, ['一等奖', '二等奖', '三等奖', '优秀奖', '冠军', '亚军', '季军'])
            fields['award_date'] = cls.extract_date(text)
            fields['organizer'] = cls.extract_field(text, ['主办单位', '组织单位', '主办方', '组织方'])
            fields['certificate_number'] = cls.extract_field(text, ['证书编号', '编号', '证书号'])

        elif cert_type == '荣誉证书':
            fields['honor_title'] = cls.extract_field(text, ['荣誉名称', '称号'])
            fields['grant_date'] = cls.extract_date(text)
            fields['grantor'] = cls.extract_field(text, ['授予单位', '授予机构'])
            fields['reason'] = cls.extract_field(text, ['获得原因', '获奖原因'])

        elif cert_type == '资格证':
            fields['certificate_name'] = cls.extract_field(text, ['证书名称', '资格名称'])
            fields['certificate_number'] = cls.extract_field(text, ['证书编号', '编号'])
            fields['issue_date'] = cls.extract_date(text)
            fields['expiry_date'] = cls.extract_field(text, ['有效期至', '有效期', '过期日期'])
            fields['issuing_authority'] = cls.extract_field(text, ['发证机构', '颁发机构', '发证单位'])

        elif cert_type == '职业技能等级证书':
            fields['skill_name'] = cls.extract_field(text, ['职业技能', '职业名称'])
            fields['skill_level'] = cls.extract_field(text, ['五级/初级工', '四级/中级工', '三级/高级工', '二级/技师', '一级/高级技师'])
            fields['certificate_number'] = cls.extract_field(text, ['证书编号', '编号'])
            fields['issue_date'] = cls.extract_date(text)
            fields['issuing_authority'] = cls.extract_field(text, ['发证机构', '颁发机构', '发证单位'])

        # Remove None values
        return {k: v for k, v in fields.items() if v}

    @classmethod
    def extract_field(cls, text: str, keywords: list) -> Optional[str]:
        """Extract field value by finding keyword and returning subsequent text."""
        for keyword in keywords:
            idx = text.find(keyword)
            if idx != -1:
                # Get text after keyword (up to next newline or 50 chars)
                end_idx = min(idx + len(keyword) + 50, len(text))
                value_text = text[idx + len(keyword):end_idx]
                # Clean up: remove common separators
                value_text = re.sub(r'^[\s:：\-\–\—]+', '', value_text)
                value_text = value_text.strip()
                # Take only first line
                value_text = value_text.split('\n')[0].strip()
                if value_text:
                    return value_text[:100]  # Limit length
        return None

    @classmethod
    def extract_date(cls, text: str) -> Optional[str]:
        """Extract date in various formats (YYYY-MM-DD, YYYY年MM月DD日, etc.)."""
        # Match date patterns
        patterns = [
            r'(\d{4})[年\-](\d{1,2})[月\-](\d{1,2})日?',
            r'(\d{4})[/年](\d{1,2})[/月](\d{1,2})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                year, month, day = match.groups()
                return f'{int(year)}-{int(month):02d}-{int(day):02d}'
        return None

    @classmethod
    def extract_title(cls, text_lines: list, cert_type: str) -> str:
        """Extract certificate title from text lines.

        Heuristic: first line that is 5-50 chars and contains meaningful text.
        """
        for line in text_lines[:5]:  # Check first 5 lines
            line = line.strip()
            if 5 <= len(line) <= 50 and not line.isdigit():
                return line
        # Fallback: first 30 chars of text
        return text_lines[0][:30] if text_lines else f'{cert_type} / {cert_type}'
