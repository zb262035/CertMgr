"""OCR Service using PaddleOCR for local certificate recognition."""
import os
import re
from datetime import datetime
from typing import Optional
from paddleocr import PaddleOCR
from PIL import Image
import pdf2image

# Initialize PaddleOCR (Chinese + English, use_angle_cls=True for text orientation)
# OCR results cached in class to avoid re-initialization
_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = PaddleOCR(lang='ch', use_textline_orientation=True, show_log=False)
    return _ocr_engine

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
            dict with keys: success (bool), text (str), type (str), fields (dict), error (str)
        """
        try:
            # Convert PDF to images if needed
            if file_mime_type == 'application/pdf':
                images = pdf2image.convert_from_path(file_path, dpi=200)
                if not images:
                    return {'success': False, 'error': 'PDF转换失败 / PDF conversion failed'}
                # Use first page
                image_path = file_path + '.tmp.png'
                images[0].save(image_path, 'PNG')
                file_path = image_path

            # Run OCR
            ocr = get_ocr_engine()
            result = ocr.predict(file_path)

            # Clean up temp file
            if file_path.endswith('.tmp.png'):
                os.remove(file_path)

            # Parse result (new PaddleOCR API returns dict with rec_texts)
            text_lines = []
            for res in result:
                rec_texts = res.get('rec_texts', []) if isinstance(res, dict) else []
                if isinstance(res, dict):
                    for text in res.get('rec_texts', []):
                        text_lines.append(text)
                elif isinstance(res, list) and len(res) >= 2:
                    text_lines.append(res[1][0])  # Old API format

            if not text_lines:
                return {'success': False, 'error': '未能识别出文字 / No text recognized'}

            full_text = '\n'.join(text_lines)

            # Detect certificate type
            cert_type = cls.detect_type(full_text)

            # Extract fields based on type
            fields = cls.extract_fields(full_text, cert_type)

            # Generate title from first significant line
            title = cls.extract_title(text_lines, cert_type)

            return {
                'success': True,
                'text': full_text,
                'type': cert_type,
                'fields': fields,
                'title': title,
            }

        except Exception as e:
            return {'success': False, 'error': f'OCR识别失败 / OCR recognition failed: {str(e)}'}

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
            # Extract competition name (usually first major line)
            fields['competition_name'] = cls.extract_field(text, ['比赛名称', '竞赛名称', '赛事名称'])
            # Extract award level
            fields['award_level'] = cls.extract_field(text, ['一等奖', '二等奖', '三等奖', '优秀奖', '冠军', '亚军', '季军'])
            # Extract date
            fields['award_date'] = cls.extract_date(text)
            # Extract organizer
            fields['organizer'] = cls.extract_field(text, ['主办单位', '组织单位', '主办方', '组织方'])
            # Extract certificate number
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