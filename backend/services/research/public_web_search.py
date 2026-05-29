from __future__ import annotations

import re
import warnings
from urllib.parse import urlparse

from backend.api.schemas.domain import JobDescriptionDocument, PublicResearchReport, ResearchSourceCard
from backend.core.config import settings
import requests

warnings.filterwarnings(
    "ignore",
    message=r"This package \(`duckduckgo_search`\) has been renamed to `ddgs`!.*",
    category=RuntimeWarning,
)

try:  # pragma: no cover - import safety for local environments
    from ddgs import DDGS
except Exception:  # pragma: no cover - import safety for local environments
    try:
        from duckduckgo_search import DDGS
    except Exception:
        DDGS = None


INTERVIEW_HINTS = ("interview", "question", "behavioral", "case", "mock", "面经")
COMMUNITY_HINTS = ("nowcoder", "牛客", "csdn", "v2ex", "reddit", "知乎", "juejin")
OFFICIAL_HINTS = ("github.com", "docs.", ".gov", "official")


def run_public_web_research(
    *,
    jd: JobDescriptionDocument,
    enabled: bool,
    max_results: int = 5,
) -> PublicResearchReport:
    queries = _build_queries(jd)
    if not enabled:
        return PublicResearchReport(enabled=False, queries=queries)

    if DDGS is None:
        return PublicResearchReport(
            enabled=True,
            queries=queries,
            summary="Public research was enabled, but web search is unavailable in the current environment.",
            caveats=[
                "Public research is optional and should not block the deterministic analysis flow.",
            ],
        )

    cards: list[ResearchSourceCard] = []
    seen_urls: set[str] = set()
    try:
        for query in queries:
            for row in _search_rows(query=query, max_results=max_results):
                url = (row.get("url") or row.get("href") or "").strip()
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                source_type = _infer_source_type(
                    title=row.get("title") or "",
                    snippet=row.get("content") or row.get("body") or "",
                    url=url,
                )
                cards.append(
                    ResearchSourceCard(
                        title=(row.get("title") or url).strip(),
                        url=url,
                        source_name=_source_name_from_url(url),
                        snippet=_clean_snippet(row.get("content") or row.get("body") or ""),
                        query=query,
                        source_type=source_type,
                        credibility_score=_credibility_score(url=url, source_type=source_type),
                    )
                )
                if len(cards) >= max_results:
                    break
            if len(cards) >= max_results:
                break
    except Exception as exc:  # pragma: no cover - network variability
        return PublicResearchReport(
            enabled=True,
            queries=queries,
            summary="Public research was enabled, but the current environment could not fetch public results.",
            caveats=[
                "The deterministic report still works without public-web enrichment.",
                f"Search error: {exc.__class__.__name__}",
            ],
        )

    if not cards:
        return PublicResearchReport(
            enabled=True,
            queries=queries,
            summary="Public research was enabled, but no usable public sources were returned.",
            caveats=[
                "This layer is supplemental context only and should not replace the JD itself.",
            ],
        )

    cards.sort(key=lambda item: item.credibility_score, reverse=True)
    return PublicResearchReport(
        enabled=True,
        queries=queries,
        summary=f"Collected {len(cards)} public sources about role expectations, interview experience, and skill requirements.",
        insights=_build_insights(jd, cards),
        caveats=[
            "Public research is supplemental context only and does not directly change the deterministic score.",
            "Treat public interview write-ups as qualitative signals, not as guaranteed truths about one specific company.",
        ],
        source_cards=cards,
    )


def _build_queries(jd: JobDescriptionDocument) -> list[str]:
    role = jd.role_title or "target role"
    skills = [skill.replace("_", " ") for skill in jd.hard_skills[:3]]
    must_have = [_compress_requirement(item) for item in jd.must_have_items[:2]]
    role_flags = _detect_role_search_flags(jd)

    queries = [
        f"{role} interview questions",
        f"{role} {' '.join(skills)} skill requirements".strip(),
        f"{role} job requirements resume tips",
        f"{role} github interview questions",
        f"{role} nowcoder interview experience",
    ]
    if must_have:
        queries.append(f"{role} {must_have[0]} interview")
        queries.append(f"{role} {must_have[0]} resume")
    if role_flags["supply_chain"]:
        queries.append(f"{role} supplier delay inventory planning interview")
        queries.append(f"{role} procurement planning github")
    if role_flags["analysis"]:
        queries.append(f"{role} sql dashboard metrics interview")
        queries.append(f"{role} case study metrics root cause analysis")
    if role_flags["procurement"]:
        queries.append(f"{role} sourcing supplier negotiation interview")
        queries.append(f"{role} supplier management resume keywords")
    return _dedupe(queries)


def _search_rows(*, query: str, max_results: int) -> list[dict]:
    if settings.search_provider in {"auto", "tavily"} and settings.tavily_api_key:
        try:
            rows = _search_with_tavily(query=query, max_results=max_results)
            if rows or settings.search_provider == "tavily":
                return rows
        except Exception:
            if settings.search_provider == "tavily":
                raise
    return _search_with_ddgs(query=query, max_results=max_results)


def _search_with_tavily(*, query: str, max_results: int) -> list[dict]:
    response = requests.post(
        "https://api.tavily.com/search",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.tavily_api_key}",
        },
        json={
            "query": query,
            "topic": "general",
            "search_depth": "basic",
            "max_results": max_results,
            "include_raw_content": "text",
            "include_domains": [
                "github.com",
                "nowcoder.com",
                "zhihu.com",
                "juejin.cn",
                "csdn.net",
            ],
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("results", []) or []


def _search_with_ddgs(*, query: str, max_results: int) -> list[dict]:
    if DDGS is None:
        return []
    rows: list[dict] = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        with DDGS(timeout=8) as ddgs:
            for row in ddgs.text(query, max_results=max_results):
                rows.append(row)
    return rows


def _build_insights(jd: JobDescriptionDocument, cards: list[ResearchSourceCard]) -> list[str]:
    insights: list[str] = []
    role = jd.role_title or "the target role"
    interview_cards = [card for card in cards if card.source_type == "interview"]
    community_cards = [card for card in cards if card.source_type == "community"]
    repeated_skills = _find_repeated_skill_mentions(jd, cards)

    insights.append(f"Public research looked at open web sources around the target role: {role}.")
    if interview_cards:
        insights.append(
            f"{len(interview_cards)} public sources look like interview-experience or interview-question references."
        )
    if community_cards:
        insights.append(
            f"{len(community_cards)} public sources come from community discussions, which are useful for patterns but still need judgment."
        )
    if repeated_skills:
        insights.append(f"Repeated public signals mention: {', '.join(repeated_skills[:4])}.")
    strongest_sources = ", ".join(card.source_name for card in cards[:3])
    if strongest_sources:
        insights.append(f"The strongest public references in this batch came from: {strongest_sources}.")
    source_mix = _build_source_mix(cards)
    if source_mix:
        insights.append(source_mix)
    return insights


def _build_source_mix(cards: list[ResearchSourceCard]) -> str:
    counts: dict[str, int] = {}
    for card in cards:
        counts[card.source_type] = counts.get(card.source_type, 0) + 1
    if not counts:
        return ""
    ordered = ", ".join(f"{source_type} x{count}" for source_type, count in sorted(counts.items()))
    return f"The current public-research mix is: {ordered}."


def _detect_role_search_flags(jd: JobDescriptionDocument) -> dict[str, bool]:
    haystack = " ".join(
        filter(
            None,
            [jd.role_title or "", jd.raw_text or "", " ".join(jd.keywords), " ".join(jd.must_have_items)],
        )
    ).lower()
    return {
        "supply_chain": any(
            token in haystack
            for token in ("supply", "inventory", "logistics", "planning", "供应链", "库存", "物流", "计划")
        ),
        "analysis": any(
            token in haystack
            for token in ("analysis", "analyst", "data", "sql", "dashboard", "metrics", "分析", "数据", "指标", "报表")
        ),
        "procurement": any(
            token in haystack
            for token in ("procurement", "supplier", "sourcing", "vendor", "采购", "供应商", "寻源")
        ),
    }


def _compress_requirement(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"^\d+\s*[\.\)\]:：、]+\s*", "", compact)
    compact = re.sub(r"^(?:任职要求|requirements?)\s*[:：]?\s*", "", compact, flags=re.IGNORECASE)
    return compact[:42]


def _find_repeated_skill_mentions(
    jd: JobDescriptionDocument,
    cards: list[ResearchSourceCard],
) -> list[str]:
    haystack = " ".join(filter(None, [card.title + " " + card.snippet for card in cards])).lower()
    repeated: list[str] = []
    for skill in jd.hard_skills:
        normalized = skill.replace("_", " ").lower()
        if normalized in haystack:
            repeated.append(skill.replace("_", " "))
    return repeated


def _infer_source_type(*, title: str, snippet: str, url: str) -> str:
    lowered = " ".join((title, snippet, url)).lower()
    if any(token in lowered for token in INTERVIEW_HINTS):
        return "interview"
    if any(token in lowered for token in COMMUNITY_HINTS):
        return "community"
    if any(token in lowered for token in OFFICIAL_HINTS):
        return "official"
    if "career" in lowered or "resume" in lowered or "job" in lowered:
        return "career"
    return "general"


def _source_name_from_url(url: str) -> str:
    hostname = urlparse(url).hostname or url
    hostname = re.sub(r"^www\.", "", hostname)
    return hostname


def _credibility_score(*, url: str, source_type: str) -> int:
    score_map = {
        "official": 85,
        "career": 74,
        "interview": 68,
        "community": 60,
        "general": 55,
    }
    score = score_map.get(source_type, 55)
    if url.startswith("https://"):
        score += 3
    if "github.com" in url or "docs." in url:
        score += 4
    return min(100, score)


def _clean_snippet(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact[:220]


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        key = item.lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return ordered
