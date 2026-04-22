from __future__ import annotations

import re

from backend.api.schemas.domain import JobDescriptionDocument
from backend.services.shared.skill_taxonomy import HARD_SKILL_TAXONOMY, SOFT_SKILL_TAXONOMY, match_taxonomy
from backend.services.shared.text_normalization import repair_mojibake


EDUCATION_PATTERNS = ("博士", "硕士", "本科", "大专", "college", "bachelor", "master", "phd")
INDUSTRY_HINTS = (
    "互联网",
    "电商",
    "金融",
    "制造",
    "快消",
    "咨询",
    "教育",
    "医疗",
    "新能源",
    "汽车",
    "供应链",
)
PREFERRED_MARKERS = ("优先", "plus", "加分", "preferred", "nice to have")
MUST_HAVE_MARKERS = ("要求", "must", "required", "熟悉", "掌握", "精通", "能够", "需要", "负责")
ROLE_LINE_MARKERS = ("职位", "岗位", "job title", "role", "应聘", "招聘")
TOKEN_RE = re.compile(r"[A-Za-z0-9_+#/.%-]+|[\u4e00-\u9fff]{2,}")
KEYWORD_STOPWORDS = {
    "负责",
    "熟悉",
    "掌握",
    "能够",
    "优先",
    "要求",
    "具备",
    "以及",
    "相关",
    "工作",
    "经验",
    "能力",
    "以上",
    "至少",
    "良好",
    "岗位",
    "职位",
    "任职要求",
    "have",
    "must",
    "required",
    "preferred",
    "nice",
    "to",
}


def parse_job_description(raw_text: str) -> JobDescriptionDocument:
    normalized_text = repair_mojibake(_normalize_text(raw_text))
    lines = [line.strip(" -•●▪") for line in normalized_text.splitlines() if line.strip()]

    role_title = _extract_role_title(lines)
    company_name = _extract_company_name(lines)
    location = _extract_location(normalized_text)
    years_experience = _extract_years_experience(normalized_text)
    education_requirement = _extract_education_requirement(normalized_text)
    industry_hint = _extract_industry_hint(normalized_text)
    hard_skills = match_taxonomy(normalized_text, HARD_SKILL_TAXONOMY)
    soft_skills = match_taxonomy(normalized_text, SOFT_SKILL_TAXONOMY)
    must_have_items, preferred_items = _split_requirement_lines(lines)
    keywords = _build_keywords(role_title, hard_skills, soft_skills, must_have_items)

    return JobDescriptionDocument(
        raw_text=normalized_text,
        company_name=company_name,
        role_title=role_title,
        location=location,
        industry_hint=industry_hint,
        years_experience=years_experience,
        education_requirement=education_requirement,
        hard_skills=hard_skills,
        soft_skills=soft_skills,
        keywords=keywords,
        must_have_items=must_have_items,
        preferred_items=preferred_items,
    )


def _normalize_text(raw_text: str) -> str:
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_role_title(lines: list[str]) -> str | None:
    for line in lines[:6]:
        lowered = line.lower()
        if any(marker in lowered for marker in ROLE_LINE_MARKERS):
            return _clean_label_value(line)
    for line in lines[:4]:
        if len(line) <= 40:
            return line
    return None


def _extract_company_name(lines: list[str]) -> str | None:
    company_patterns = (
        re.compile(r"(?:公司|company)[:：]?\s*(.+)", re.IGNORECASE),
        re.compile(r"(.+?)(?:招聘|诚聘|招募)"),
    )
    for line in lines[:8]:
        for pattern in company_patterns:
            match = pattern.search(line)
            if match:
                return match.group(1).strip()
    return None


def _extract_location(text: str) -> str | None:
    location_match = re.search(
        r"(?:工作地点|地点|location)[:：]?\s*([A-Za-z\u4e00-\u9fff·/-]{2,20})",
        text,
        re.IGNORECASE,
    )
    return location_match.group(1).strip() if location_match else None


def _extract_years_experience(text: str) -> str | None:
    match = re.search(
        r"(\d+(?:\s*[-~至到]\s*\d+)?)\s*年(?:以上)?(?:[\u4e00-\u9fffA-Za-z]{0,12})?经验",
        text,
        re.IGNORECASE,
    )
    return match.group(1).replace(" ", "") if match else None


def _extract_education_requirement(text: str) -> str | None:
    lowered = text.lower()
    for marker in EDUCATION_PATTERNS:
        if marker.lower() in lowered:
            return marker
    return None


def _extract_industry_hint(text: str) -> str | None:
    for hint in INDUSTRY_HINTS:
        if hint in text:
            return hint
    return None


def _split_requirement_lines(lines: list[str]) -> tuple[list[str], list[str]]:
    must_have_items: list[str] = []
    preferred_items: list[str] = []
    for line in lines:
        lowered = line.lower()
        if len(line) < 6:
            continue
        if any(marker in lowered for marker in PREFERRED_MARKERS):
            preferred_items.append(line)
        elif any(marker in lowered for marker in MUST_HAVE_MARKERS):
            must_have_items.append(line)
    return _dedupe(must_have_items), _dedupe(preferred_items)


def _build_keywords(
    role_title: str | None,
    hard_skills: list[str],
    soft_skills: list[str],
    must_have_items: list[str],
) -> list[str]:
    keywords: list[str] = []
    if role_title:
        keywords.extend(_clean_keyword_tokens(role_title))
    keywords.extend(hard_skills)
    keywords.extend(soft_skills)
    for line in must_have_items[:5]:
        keywords.extend(_clean_keyword_tokens(line))
    return _dedupe(keywords)[:20]


def _clean_label_value(line: str) -> str:
    return re.sub(r"^(?:职位|岗位|job title|role)[:：]?\s*", "", line, flags=re.IGNORECASE).strip()


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return ordered


def _clean_keyword_tokens(text: str) -> list[str]:
    tokens = [token.lower() for token in TOKEN_RE.findall(text)]
    cleaned: list[str] = []
    for token in tokens:
        normalized = token.strip("._-")
        if token in KEYWORD_STOPWORDS:
            continue
        if not normalized:
            continue
        if normalized.isdigit():
            continue
        if len(token) < 2:
            continue
        if re.fullmatch(r"[\u4e00-\u9fff]+", token) and len(token) > 8:
            continue
        cleaned.append(token)
    return cleaned
