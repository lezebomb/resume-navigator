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

MOJIBAKE_MARKERS = (
    "锛",
    "銆",
    "鏈",
    "閲",
    "鐩",
    "璇",
    "鍏",
    "娌",
    "闆",
    "缁",
    "浠",
    "鐢",
)


def repair_mojibake(text: str) -> str:
    if not text:
        return text

    try:
        candidate = text.encode("gbk", errors="ignore").decode("utf-8", errors="ignore")
    except Exception:
        return text

    if not candidate:
        return text

    if any(marker in text for marker in MOJIBAKE_MARKERS) and any(hint in candidate for hint in DOMAIN_HINTS):
        return candidate

    original_score = _text_quality_score(text)
    candidate_score = _text_quality_score(candidate)
    if candidate_score >= original_score + 3:
        return candidate
    return text


def _text_quality_score(text: str) -> int:
    score = 0
    score += sum(4 for hint in DOMAIN_HINTS if hint in text)
    score += text.count("：") + text.count("，") + text.count("。")
    score += len(re.findall(r"[A-Za-z0-9@._%+-]", text)) // 30
    score -= sum(text.count(marker) * 2 for marker in MOJIBAKE_MARKERS)
    return score
