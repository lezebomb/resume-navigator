from __future__ import annotations

from time import perf_counter
from typing import Callable

from backend.api.schemas.domain import AnalysisResult, AnalysisStage
from backend.core.config import settings
from backend.services.analysis.deep_review import run_deep_review
from backend.services.ats.engine import evaluate_ats_readiness
from backend.services.history.store import save_analysis_result
from backend.services.interview.generator import build_interview_prep
from backend.services.jd.parser import parse_job_description
from backend.services.llm.user_copy import maybe_refine_user_copy
from backend.services.matching.engine import evaluate_resume_match, label_confidence
from backend.services.research.public_web_search import run_public_web_research
from backend.services.resume.parser import parse_resume_bytes
from backend.services.rewrite.planner import build_rewrite_plan


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
        research = run_public_web_research(
            jd=jd,
            enabled=True,
            max_results=settings.public_research_max_results,
        )
        _record_stage(
            stages,
            AnalysisStage(
                name="public_research",
                detail=research.summary,
                duration_ms=_duration_ms(started),
            ),
            stage_callback,
        )

    started = perf_counter()
    refined_user_copy = maybe_refine_user_copy(
        role_title=jd.role_title or "",
        structured_payload={
            "overall_score": match.overall_score,
            "score_label": match.score_label,
            "application_recommendation": match.application_recommendation,
            "application_risk_level": match.application_risk_level,
            "recruiter_takeaway": match.recruiter_takeaway,
            "must_fix_now": match.must_fix_now,
            "priority_actions": match.priority_actions,
            "matched_hard_skills": match.matched_hard_skills,
            "missing_hard_skills": match.missing_hard_skills,
            "research_summary": research.summary if research else "",
        },
    )
    if refined_user_copy:
        match.user_copy.update(refined_user_copy)
        _record_stage(
            stages,
            AnalysisStage(
                name="llm_polish",
                detail="Used your connected model to shorten the user-facing summary without changing scores or evidence.",
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
        rewrite=build_rewrite_plan(resume=resume, jd=jd, match=match),
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
