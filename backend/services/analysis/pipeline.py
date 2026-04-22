from __future__ import annotations

from time import perf_counter
from typing import Callable

from backend.api.schemas.domain import AnalysisResult, AnalysisStage
from backend.services.analysis.deep_review import run_deep_review
from backend.services.ats.engine import evaluate_ats_readiness
from backend.services.history.store import save_analysis_result
from backend.services.interview.generator import build_interview_prep
from backend.services.jd.parser import parse_job_description
from backend.services.matching.engine import evaluate_resume_match, label_confidence
from backend.services.research.public_web_search import run_public_web_research
from backend.services.resume.parser import parse_resume_bytes


def analyze_resume_against_jd(
    filename: str,
    file_bytes: bytes,
    jd_text: str,
    persist: bool = False,
    analysis_mode: str = "standard",
    enable_public_research: bool = False,
    stage_callback: Callable[[AnalysisStage], None] | None = None,
) -> AnalysisResult:
    stages: list[AnalysisStage] = []

    started = perf_counter()
    resume = parse_resume_bytes(filename=filename, file_bytes=file_bytes)
    _record_stage(
        stages,
        AnalysisStage(
            name="resume_parse",
            detail="Parsed the uploaded resume, extracted text, and segmented sections.",
            duration_ms=_duration_ms(started),
        ),
        stage_callback,
    )

    started = perf_counter()
    jd = parse_job_description(jd_text)
    _record_stage(
        stages,
        AnalysisStage(
            name="jd_parse",
            detail="Structured the JD into role, skills, requirements, and keywords.",
            duration_ms=_duration_ms(started),
        ),
        stage_callback,
    )

    started = perf_counter()
    ats = evaluate_ats_readiness(resume)
    _record_stage(
        stages,
        AnalysisStage(
            name="ats_audit",
            detail="Checked layout safety, extractability, timeline cues, and contact completeness.",
            duration_ms=_duration_ms(started),
        ),
        stage_callback,
    )

    started = perf_counter()
    match = evaluate_resume_match(resume=resume, jd=jd, ats=ats)
    _record_stage(
        stages,
        AnalysisStage(
            name="match_audit",
            detail="Cross-checked hard skills, must-have lines, quantified outcomes, and experience signals.",
            duration_ms=_duration_ms(started),
        ),
        stage_callback,
    )

    if analysis_mode == "deep":
        started = perf_counter()
        deep_review = run_deep_review(resume=resume, jd=jd, match=match)
        if deep_review.confidence_reasons:
            match.confidence_reasons = _dedupe_strings(match.confidence_reasons + deep_review.confidence_reasons)
        if deep_review.risk_signals:
            match.risk_signals = _dedupe_strings(match.risk_signals + deep_review.risk_signals)
        if deep_review.priority_actions:
            match.priority_actions = _dedupe_strings(match.priority_actions + deep_review.priority_actions)
        if deep_review.confidence_delta:
            match.confidence_score = max(0, min(100, match.confidence_score + deep_review.confidence_delta))
            match.confidence_label = label_confidence(match.confidence_score)
        _record_stage(
            stages,
            AnalysisStage(
                name="deep_review",
                detail=deep_review.summary,
                duration_ms=_duration_ms(started),
            ),
            stage_callback,
        )

    research = None
    if enable_public_research:
        started = perf_counter()
        research = run_public_web_research(jd=jd, enabled=True)
        _record_stage(
            stages,
            AnalysisStage(
                name="public_research",
                detail=research.summary,
                duration_ms=_duration_ms(started),
            ),
            stage_callback,
        )

    result = AnalysisResult(
        analysis_mode="deep" if analysis_mode == "deep" else "standard",
        stages=stages,
        resume=resume,
        jd=jd,
        ats=ats,
        match=match,
        research=research,
        interview=build_interview_prep(resume=resume, jd=jd, match=match, research=research),
    )
    if persist:
        return save_analysis_result(result)
    return result


def _duration_ms(started: float) -> int:
    return max(1, round((perf_counter() - started) * 1000))


def _dedupe_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _record_stage(
    stages: list[AnalysisStage],
    stage: AnalysisStage,
    stage_callback: Callable[[AnalysisStage], None] | None,
) -> None:
    stages.append(stage)
    if stage_callback:
        stage_callback(stage)
