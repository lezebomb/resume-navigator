from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from apps.web.i18n import get_ui, resolve_lang, translate_dynamic, translate_stage_name
from backend.api.routes.analysis import router as analysis_router
from backend.core.config import settings
from backend.core.logging import configure_logging
from backend.services.analysis.jobs import create_analysis_job, get_analysis_job
from backend.services.feedback.store import list_feedback_records, save_feedback
from backend.services.history.store import get_analysis_record, list_analysis_history


configure_logging(settings.log_level)
settings.ensure_runtime_dirs()

WEB_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))
templates.env.globals["translate_dynamic"] = translate_dynamic
templates.env.globals["translate_stage_name"] = translate_stage_name

app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    summary="Deterministic resume diagnosis backend for Resume Navigator.",
)
app.include_router(analysis_router)
app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")


def _shared_context(request: Request) -> dict:
    current_lang = resolve_lang(request.query_params.get("lang"))
    return {
        "app_name": settings.app_name,
        "current_lang": current_lang,
        "ui": get_ui(current_lang),
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    context = _shared_context(request)
    context.update(
        {
            "recent_feedback_count": len(list_feedback_records()),
            "analysis_count": len(list_analysis_history()),
        }
    )
    return templates.TemplateResponse(request, "index.html", context)


@app.post("/analyze/browser", response_class=HTMLResponse)
async def analyze_browser(
    request: Request,
    file: UploadFile = File(...),
    jd_text: str = Form(...),
    analysis_mode: str = Form("standard"),
    enable_public_research: str | None = Form(None),
    lang: str = Form("zh"),
) -> HTMLResponse:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in {".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX resumes are supported.")
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="JD text is required.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    job = create_analysis_job(
        filename=file.filename or f"resume{extension}",
        file_bytes=file_bytes,
        jd_text=jd_text,
        analysis_mode=analysis_mode,
        enable_public_research=enable_public_research is not None,
    )
    return RedirectResponse(url=f"/analyze/jobs/{job.job_id}?lang={resolve_lang(lang)}", status_code=303)


@app.get("/analyze/jobs/{job_id}", response_class=HTMLResponse)
async def analysis_job_page(request: Request, job_id: str) -> HTMLResponse:
    job = get_analysis_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Analysis job not found.")
    context = _shared_context(request)
    context.update({"job": job.to_dict()})
    return templates.TemplateResponse(request, "analysis_job.html", context)


@app.get("/analyze/jobs/{job_id}/status", response_class=JSONResponse)
async def analysis_job_status(job_id: str, lang: str = "zh") -> JSONResponse:
    job = get_analysis_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Analysis job not found.")
    resolved_lang = resolve_lang(lang)
    payload = job.to_dict()
    payload["current_stage_detail"] = translate_dynamic(payload.get("current_stage_detail") or "", resolved_lang)
    payload["stages"] = [
        {
            **stage,
            "display_name": translate_stage_name(stage["name"], resolved_lang),
            "display_detail": translate_dynamic(stage["detail"], resolved_lang),
        }
        for stage in payload["stages"]
    ]
    return JSONResponse(content=payload)


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request) -> HTMLResponse:
    context = _shared_context(request)
    context.update({"records": list_analysis_history()})
    return templates.TemplateResponse(request, "history.html", context)


@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request) -> HTMLResponse:
    context = _shared_context(request)
    context.update({"records": list_feedback_records()})
    return templates.TemplateResponse(request, "feedback.html", context)


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
    lang: str = Form("zh"),
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
    context = _shared_context(request)
    context.update(
        {
            "feedback": feedback,
            "current_lang": resolve_lang(lang),
            "ui": get_ui(resolve_lang(lang)),
        }
    )
    return templates.TemplateResponse(request, "thanks.html", context)


@app.get("/analysis/{analysis_id}", response_class=HTMLResponse)
async def analysis_detail(request: Request, analysis_id: str) -> HTMLResponse:
    result = get_analysis_record(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found.")
    context = _shared_context(request)
    context.update(
        {
            "result": result.model_dump(),
            "analysis_mode": result.analysis_mode,
            "result_view_path": f"/analysis/{analysis_id}",
        }
    )
    return templates.TemplateResponse(request, "result.html", context)


@app.get("/analysis/{analysis_id}/json", response_class=JSONResponse)
async def analysis_json(analysis_id: str) -> JSONResponse:
    result = get_analysis_record(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found.")
    return JSONResponse(content=result.model_dump())
