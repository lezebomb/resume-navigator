from __future__ import annotations

from backend.api.schemas.domain import AnalysisResult
from backend.services.ats.engine import evaluate_ats_readiness
from backend.services.history.store import save_analysis_result
from backend.services.jd.parser import parse_job_description
from backend.services.matching.engine import evaluate_resume_match
from backend.services.resume.parser import parse_resume_bytes


def analyze_resume_against_jd(filename: str, file_bytes: bytes, jd_text: str, persist: bool = False) -> AnalysisResult:
    resume = parse_resume_bytes(filename=filename, file_bytes=file_bytes)
    jd = parse_job_description(jd_text)
    ats = evaluate_ats_readiness(resume)
    match = evaluate_resume_match(resume=resume, jd=jd, ats=ats)
    result = AnalysisResult(resume=resume, jd=jd, ats=ats, match=match)
    if persist:
        return save_analysis_result(result)
    return result
