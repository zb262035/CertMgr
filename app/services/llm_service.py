"""LLM Service using Ollama for local AI inference.

Provides structured text extraction for certificate fields using local LLM.
"""

import json
import os
from typing import Optional

import requests

# Ollama API endpoint
OLLAMA_API = "http://localhost:11434/api/generate"

# Default model for certificate field extraction
DEFAULT_MODEL = "qwen3-coder:30b"

# Fallback model (faster for simple tasks)
FALLBACK_MODEL = "deepseek-r1:8b"

# Certificate type schemas for field extraction
CERTIFICATE_SCHEMAS = {
    '比赛获奖证书': {
        'description': '比赛获奖证书，包括竞赛名称、获奖等级、获奖日期、主办单位等',
        'fields': [
            {'name': 'competition_name', 'label': '比赛名称', 'type': 'string', 'required': True},
            {'name': 'award_level', 'label': '获奖等级', 'type': 'select', 'options': ['一等奖', '二等奖', '三等奖', '优秀奖', '冠军', '亚军', '季军'], 'required': True},
            {'name': 'award_date', 'label': '获奖日期', 'type': 'date', 'required': True},
            {'name': 'organizer', 'label': '主办单位', 'type': 'string', 'required': True},
            {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': False},
        ]
    },
    '荣誉证书': {
        'description': '荣誉证书，包括荣誉名称、授予单位、授予日期等',
        'fields': [
            {'name': 'honor_title', 'label': '荣誉名称', 'type': 'string', 'required': True},
            {'name': 'grant_date', 'label': '授予日期', 'type': 'date', 'required': True},
            {'name': 'grantor', 'label': '授予单位', 'type': 'string', 'required': True},
            {'name': 'reason', 'label': '获得原因', 'type': 'text', 'required': False},
        ]
    },
    '资格证': {
        'description': '资格证书，包括证书名称、证书编号、发证日期、有效期、发证机构等',
        'fields': [
            {'name': 'certificate_name', 'label': '证书名称', 'type': 'string', 'required': True},
            {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': True},
            {'name': 'issue_date', 'label': '发证日期', 'type': 'date', 'required': True},
            {'name': 'expiry_date', 'label': '有效期至', 'type': 'date', 'required': False},
            {'name': 'issuing_authority', 'label': '发证机构', 'type': 'string', 'required': True},
        ]
    },
    '职业技能等级证书': {
        'description': '职业技能等级证书，包括职业技能名称、等级、证书编号、发证日期、发证机构等',
        'fields': [
            {'name': 'skill_name', 'label': '职业技能名称', 'type': 'string', 'required': True},
            {'name': 'skill_level', 'label': '等级', 'type': 'select', 'options': ['五级/初级工', '四级/中级工', '三级/高级工', '二级/技师', '一级/高级技师'], 'required': True},
            {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': True},
            {'name': 'issue_date', 'label': '发证日期', 'type': 'date', 'required': True},
            {'name': 'issuing_authority', 'label': '发证机构', 'type': 'string', 'required': True},
        ]
    },
}


def check_ollama_status() -> dict:
    """Check if Ollama service is running.

    Returns:
        dict with status, model_available, etc.
    """
    try:
        response = requests.get("http://localhost:11434", timeout=5)
        if response.status_code == 200:
            return {"status": "online", "available": True}
    except:
        pass

    return {"status": "offline", "available": False}


def extract_fields_with_llm(
    text: str,
    cert_type: str,
    model: str = DEFAULT_MODEL
) -> dict:
    """Extract structured fields from OCR text using LLM.

    Args:
        text: OCR recognized text
        cert_type: Detected certificate type
        model: Ollama model to use

    Returns:
        dict with keys: success, fields, title, confidence, error
    """
    if not text or len(text.strip()) < 10:
        return {
            "success": False,
            "fields": {},
            "title": None,
            "confidence": {"score": 0, "issues": ["文字内容太少"]},
            "error": "文字内容太少"
        }

    # Get schema for certificate type
    schema = CERTIFICATE_SCHEMAS.get(cert_type, CERTIFICATE_SCHEMAS['荣誉证书'])
    schema_json = json.dumps(schema, ensure_ascii=False, indent=2)

    # Build prompt for field extraction
    prompt = f"""你是一个专业的证书信息提取助手。请从下面的证书OCR识别文本中提取信息。

## 证书类型
{cert_type}

## 字段说明
{schema_json}

## OCR识别文本
---
{text}
---

## 任务
1. 提取证书的标题（title）- 一般是证书上最醒目的文字，如"荣誉证书"、"获奖证书"等，或者是获得者姓名+荣誉内容
2. 提取各字段的值，注意：
   - 日期格式统一为 YYYY-MM-DD
   - 获奖等级要从给定选项中选择最匹配的
   - 如果某个字段在文本中找不到，设置为空字符串
3. 评估提取的可信度

## 输出格式（只输出JSON，不要其他内容）
{{
    "title": "提取的标题",
    "fields": {{
        "字段名": "提取的值",
        ...
    }},
    "confidence": {{
        "score": 85,
        "issues": []
    }}
}}

请开始提取："""

    try:
        response = requests.post(
            OLLAMA_API,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent extraction
                    "num_predict": 512,   # Limit response length
                }
            },
            timeout=120  # 2 minutes timeout for large models
        )

        if response.status_code != 200:
            return {
                "success": False,
                "fields": {},
                "title": None,
                "confidence": {"score": 0, "issues": [f"API错误: {response.status_code}"]},
                "error": f"API error: {response.status_code}"
            }

        result = response.json()
        llm_response = result.get("response", "").strip()

        # Parse JSON from LLM response
        # Sometimes LLM wraps JSON in markdown code blocks
        if "```json" in llm_response:
            llm_response = llm_response.split("```json")[1].split("```")[0]
        elif "```" in llm_response:
            llm_response = llm_response.split("```")[1].split("```")[0]

        extracted = json.loads(llm_response)

        return {
            "success": True,
            "fields": extracted.get("fields", {}),
            "title": extracted.get("title"),
            "confidence": extracted.get("confidence", {"score": 80, "issues": []}),
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "fields": {},
            "title": None,
            "confidence": {"score": 0, "issues": ["LLM响应超时"]},
            "error": "LLM timeout"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "fields": {},
            "title": None,
            "confidence": {"score": 0, "issues": [f"JSON解析错误: {str(e)}"]},
            "error": f"JSON parse error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "fields": {},
            "title": None,
            "confidence": {"score": 0, "issues": [str(e)]},
            "error": str(e)
        }


def extract_fields_with_fallback(
    text: str,
    cert_type: str
) -> dict:
    """Extract fields using fallback model if primary fails."""
    # Try with smaller/faster model
    result = extract_fields_with_llm(text, cert_type, FALLBACK_MODEL)
    if result["success"]:
        return result

    # If both models fail, return empty
    return {
        "success": False,
        "fields": {},
        "title": None,
        "confidence": {"score": 0, "issues": ["所有模型都无法处理"]},
        "error": "All models failed"
    }
