from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.api.schemas.domain import AnalysisResult
from backend.services.analysis.pipeline import analyze_resume_against_jd


router = APIRouter(prefix="/api", tags=["analysis"])

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_resume(
    file: UploadFile = File(...),
    jd_text: str = Form(...),
    analysis_mode: str = Form("standard"),
) -> AnalysisResult:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX resumes are supported.")
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="JD text is required.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        return analyze_resume_against_jd(
            filename=file.filename or f"resume{extension}",
            file_bytes=file_bytes,
            jd_text=jd_text,
            persist=False,
            analysis_mode=analysis_mode,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
