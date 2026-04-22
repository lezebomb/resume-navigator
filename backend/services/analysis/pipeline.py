from __future__ import annotations

from time import perf_counter

from backend.api.schemas.domain import AnalysisResult, AnalysisStage
from backend.services.ats.engine import evaluate_ats_readiness
from backend.services.history.store import save_analysis_result
from backend.services.jd.parser import parse_job_description
from backend.services.matching.engine import evaluate_resume_match
from backend.services.resume.parser import parse_resume_bytes


def analyze_resume_against_jd(
    filename: str,
    file_bytes: bytes,
    jd_text: str,
    persist: bool = False,
    analysis_mode: str = "standard",
) -> AnalysisResult:
    stages: list[AnalysisStage] = []

    started = perf_counter()
    resume = parse_resume_bytes(filename=filename, file_bytes=file_bytes)
    stages.append(
        AnalysisStage(
            name="resume_parse",
            detail="Parsed the uploaded resume, extracted text, and segmented sections.",
            duration_ms=_duration_ms(started),
        )
    )

    started = perf_counter()
    jd = parse_job_description(jd_text)
    stages.append(
        AnalysisStage(
            name="jd_parse",
            detail="Structured the JD into role, skills, requirements, and keywords.",
            duration_ms=_duration_ms(started),
        )
    )

    started = perf_counter()
    ats = evaluate_ats_readiness(resume)
    stages.append(
        AnalysisStage(
            name="ats_audit",
            detail="Checked layout safety, extractability, timeline cues, and contact completeness.",
            duration_ms=_duration_ms(started),
        )
    )

    started = perf_counter()
    match = evaluate_resume_match(resume=resume, jd=jd, ats=ats)
    stages.append(
        AnalysisStage(
            name="match_audit",
            detail="Cross-checked hard skills, must-have lines, quantified outcomes, and experience signals.",
            duration_ms=_duration_ms(started),
        )
    )

    if analysis_mode == "deep":
        started = perf_counter()
        stages.append(
            AnalysisStage(
                name="deep_review",
                detail=(
                    f"Built requirement-level evidence cards so the result can be reviewed against specific JD lines. "
                    f"Reviewed {match.total_requirement_count} must-have lines and found evidence for "
                    f"{match.covered_requirement_count + match.partial_requirement_count}. "
                    f"Current confidence is {match.confidence_label}."
                ),
                duration_ms=_duration_ms(started),
            )
        )

    result = AnalysisResult(
        analysis_mode="deep" if analysis_mode == "deep" else "standard",
        stages=stages,
        resume=resume,
        jd=jd,
        ats=ats,
        match=match,
    )
    if persist:
        return save_analysis_result(result)
    return result


def _duration_ms(started: float) -> int:
    return max(1, round((perf_counter() - started) * 1000))
