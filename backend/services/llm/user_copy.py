from __future__ import annotations

import json
import re
from typing import Any

from backend.core.config import settings

try:  # pragma: no cover - optional dependency wiring
    from google import genai
except Exception:  # pragma: no cover
    genai = None

try:  # pragma: no cover - optional dependency wiring
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


def maybe_refine_user_copy(
    *,
    role_title: str,
    structured_payload: dict[str, Any],
) -> dict[str, str]:
    if not settings.enable_optional_llm:
        return {}

    prompt = _build_prompt(role_title=role_title, structured_payload=structured_payload)

    try:
        if settings.google_api_key and genai is not None:
            client = genai.Client(api_key=settings.google_api_key)
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
            )
            return _extract_payload(getattr(response, "text", "") or "")

        if settings.openai_api_key and OpenAI is not None:
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.responses.create(
                model=settings.openai_model,
                input=prompt,
            )
            text = getattr(response, "output_text", "") or ""
            return _extract_payload(text)
    except Exception:
        return {}

    return {}


def _build_prompt(*, role_title: str, structured_payload: dict[str, Any]) -> str:
    payload = json.dumps(structured_payload, ensure_ascii=False)
    return f"""
You are refining product copy for a resume diagnosis app.

Target role: {role_title or "target role"}

Rules:
1. Do not change any numeric score.
2. Do not invent missing skills, achievements, or facts.
3. Rewrite only the short user-facing copy.
4. Keep each line short, human, and product-ready.
5. Avoid consultant language, filler, and long explanations.
6. Return valid JSON only.

Return this exact schema:
{{
  "headline_zh": "...",
  "headline_en": "...",
  "recruiter_zh": "...",
  "recruiter_en": "...",
  "next_move_zh": "...",
  "next_move_en": "..."
}}

Structured input:
{payload}
""".strip()


def _extract_payload(text: str) -> dict[str, str]:
    if not text:
        return {}
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {}
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}

    allowed = {
        "headline_zh",
        "headline_en",
        "recruiter_zh",
        "recruiter_en",
        "next_move_zh",
        "next_move_en",
    }
    cleaned: dict[str, str] = {}
    for key, value in data.items():
        if key in allowed and isinstance(value, str) and value.strip():
            cleaned[key] = value.strip()
    return cleaned
