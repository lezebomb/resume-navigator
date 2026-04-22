from __future__ import annotations

import re


DOMAIN_HINTS = (
    "教育背景",
    "教育经历",
    "工作经历",
    "实习经历",
    "项目经历",
    "项目经验",
    "技能",
    "证书",
    "公司",
    "岗位",
    "职位",
    "任职要求",
    "经验",
    "供应链",
    "采购",
    "数据分析",
    "沟通",
    "邮箱",
    "电话",
)

SUSPICIOUS_FRAGMENTS = (
    "锛",
    "銆",
    "鏈",
    "鍜",
    "鍦",
    "鎴",
    "鐨",
    "鏄",
    "浠",
    "闈",
    "閫",
    "绠",
    "鑳",
)


def repair_mojibake(text: str) -> str:
    if not text:
        return text

    current = text
    for _ in range(2):
        try:
            candidate = current.encode("gbk", errors="ignore").decode("utf-8", errors="ignore")
        except Exception:
            return current

        if not candidate or candidate == current:
            return current

        original_score = _text_quality_score(current)
        candidate_score = _text_quality_score(candidate)

        if _looks_suspicious(current) and any(hint in candidate for hint in DOMAIN_HINTS):
            current = candidate
            continue
        if _looks_suspicious(current) and candidate_score >= original_score:
            current = candidate
            continue
        if candidate_score >= original_score + 3:
            current = candidate
            continue
        return current

    return current


def _looks_suspicious(text: str) -> bool:
    return sum(text.count(fragment) for fragment in SUSPICIOUS_FRAGMENTS) >= 2


def _text_quality_score(text: str) -> int:
    score = 0
    score += sum(4 for hint in DOMAIN_HINTS if hint in text)
    score += text.count("：") + text.count("，") + text.count("。")
    score += len(re.findall(r"[A-Za-z0-9@._%+-]", text)) // 30
    score -= sum(text.count(fragment) for fragment in SUSPICIOUS_FRAGMENTS)
    return score
