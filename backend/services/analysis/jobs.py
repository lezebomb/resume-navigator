from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Literal
from uuid import uuid4

from backend.api.schemas.domain import AnalysisStage
from backend.services.analysis.pipeline import analyze_resume_against_jd


JobStatus = Literal["queued", "running", "completed", "failed"]


@dataclass(slots=True)
class AnalysisJob:
    job_id: str
    filename: str
    analysis_mode: str
    status: JobStatus
    created_at: str
    updated_at: str
    current_stage_name: str | None = None
    current_stage_detail: str | None = None
    stages: list[dict] = field(default_factory=list)
    result_analysis_id: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "filename": self.filename,
            "analysis_mode": self.analysis_mode,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "current_stage_name": self.current_stage_name,
            "current_stage_detail": self.current_stage_detail,
            "stages": list(self.stages),
            "result_analysis_id": self.result_analysis_id,
            "error_message": self.error_message,
        }


_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="resume-analysis")
_jobs: dict[str, AnalysisJob] = {}
_lock = Lock()


def create_analysis_job(*, filename: str, file_bytes: bytes, jd_text: str, analysis_mode: str) -> AnalysisJob:
    now = _utc_now()
    job = AnalysisJob(
        job_id=uuid4().hex[:12],
        filename=filename,
        analysis_mode="deep" if analysis_mode == "deep" else "standard",
        status="queued",
        created_at=now,
        updated_at=now,
    )
    with _lock:
        _jobs[job.job_id] = job

    _executor.submit(_run_job, job.job_id, filename, file_bytes, jd_text, job.analysis_mode)
    return job


def get_analysis_job(job_id: str) -> AnalysisJob | None:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        return AnalysisJob(**job.to_dict())


def _run_job(job_id: str, filename: str, file_bytes: bytes, jd_text: str, analysis_mode: str) -> None:
    _set_job_status(job_id, "running")
    try:
        result = analyze_resume_against_jd(
            filename=filename,
            file_bytes=file_bytes,
            jd_text=jd_text,
            persist=True,
            analysis_mode=analysis_mode,
            stage_callback=lambda stage: _append_stage(job_id, stage),
        )
        _mark_job_completed(job_id, result.analysis_id)
    except Exception as exc:
        _mark_job_failed(job_id, str(exc) or exc.__class__.__name__)


def _append_stage(job_id: str, stage: AnalysisStage) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        job.current_stage_name = stage.name
        job.current_stage_detail = stage.detail
        job.updated_at = _utc_now()
        job.stages.append(stage.model_dump())


def _set_job_status(job_id: str, status: JobStatus) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        job.status = status
        job.updated_at = _utc_now()


def _mark_job_completed(job_id: str, analysis_id: str | None) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        job.status = "completed"
        job.result_analysis_id = analysis_id
        job.updated_at = _utc_now()


def _mark_job_failed(job_id: str, message: str) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        job.status = "failed"
        job.error_message = message
        job.updated_at = _utc_now()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
