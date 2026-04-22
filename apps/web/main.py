from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.api.routes.analysis import router as analysis_router
from backend.core.config import settings
from backend.core.logging import configure_logging
from backend.services.analysis.pipeline import analyze_resume_against_jd
from backend.services.feedback.store import list_feedback_records, save_feedback
from backend.services.history.store import get_analysis_record, list_analysis_history


configure_logging(settings.log_level)
settings.ensure_runtime_dirs()

WEB_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    summary="Deterministic resume diagnosis backend for Resume Navigator.",
)
app.include_router(analysis_router)
app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "app_name": settings.app_name,
            "recent_feedback_count": len(list_feedback_records()),
            "analysis_count": len(list_analysis_history()),
        },
    )


@app.post("/analyze/browser", response_class=HTMLResponse)
async def analyze_browser(
    request: Request,
    file: UploadFile = File(...),
    jd_text: str = Form(...),
) -> HTMLResponse:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in {".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX resumes are supported.")
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="JD text is required.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    result = analyze_resume_against_jd(
        filename=file.filename or f"resume{extension}",
        file_bytes=file_bytes,
        jd_text=jd_text,
        persist=True,
    )
    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "app_name": settings.app_name,
            "result": result.model_dump(),
        },
    )


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "history.html",
        {
            "app_name": settings.app_name,
            "records": list_analysis_history(),
        },
    )


@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "feedback.html",
        {
            "app_name": settings.app_name,
            "records": list_feedback_records(),
        },
    )


@app.post("/feedback/browser", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    analysis_id: str = Form(""),
    overall_rating: int = Form(...),
    accuracy_rating: int = Form(...),
    usefulness_rating: int = Form(...),
    main_problem: str = Form(""),
    wanted_next: str = Form(""),
    contact: str = Form(""),
) -> HTMLResponse:
    feedback = save_feedback(
        {
            "analysis_id": analysis_id.strip() or None,
            "overall_rating": overall_rating,
            "accuracy_rating": accuracy_rating,
            "usefulness_rating": usefulness_rating,
            "main_problem": main_problem.strip(),
            "wanted_next": wanted_next.strip(),
            "contact": contact.strip(),
        }
    )
    return templates.TemplateResponse(
        request,
        "thanks.html",
        {
            "app_name": settings.app_name,
            "feedback": feedback,
        },
    )


@app.get("/analysis/{analysis_id}", response_class=HTMLResponse)
async def analysis_detail(request: Request, analysis_id: str) -> HTMLResponse:
    result = get_analysis_record(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found.")
    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "app_name": settings.app_name,
            "result": result.model_dump(),
        },
    )


@app.get("/analysis/{analysis_id}/json", response_class=JSONResponse)
async def analysis_json(analysis_id: str) -> JSONResponse:
    result = get_analysis_record(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found.")
    return JSONResponse(content=result.model_dump())
