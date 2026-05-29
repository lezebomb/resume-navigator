from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from apps.web.demo_cases import list_demo_cases
from apps.web.i18n import get_ui, resolve_lang, translate_dynamic, translate_stage_name
from backend.api.routes.analysis import router as analysis_router
from backend.core.config import settings
from backend.core.logging import configure_logging
from backend.services.analysis.jobs import create_analysis_job, get_analysis_job
from backend.services.feedback.store import list_feedback_records, save_feedback
from backend.services.history.store import can_view_analysis_record, get_analysis_record, list_analysis_history


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
    show_owner_console = _is_owner_request(request)
    return {
        "app_name": settings.app_name,
        "current_lang": current_lang,
        "ui": get_ui(current_lang),
        "show_owner_console": show_owner_console,
        "admin_query_suffix": _admin_query_suffix(request),
    }


def _is_owner_request(request: Request) -> bool:
    if settings.app_env == "development":
        return True
    if not settings.owner_admin_token:
        return False
    supplied = (
        request.query_params.get("admin_token")
        or request.headers.get("X-Admin-Token")
        or request.cookies.get("resume_admin_token")
        or ""
    )
    return supplied == settings.owner_admin_token


def _require_owner_request(request: Request) -> None:
    if not _is_owner_request(request):
        raise HTTPException(status_code=403, detail="Owner-only data view.")


def _admin_query_suffix(request: Request) -> str:
    if not _is_owner_request(request):
        return ""
    token = request.query_params.get("admin_token") or ""
    return f"&admin_token={token}" if token else ""


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    context = _shared_context(request)
    show_owner_console = context["show_owner_console"]
    context.update(
        {
            "recent_feedback_count": len(list_feedback_records()) if show_owner_console else 0,
            "analysis_count": len(list_analysis_history()) if show_owner_console else 0,
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
    _require_owner_request(request)
    context = _shared_context(request)
    context.update({"records": list_analysis_history()})
    return templates.TemplateResponse(request, "history.html", context)


@app.get("/cases", response_class=HTMLResponse)
async def cases_page(request: Request) -> HTMLResponse:
    context = _shared_context(request)
    context.update({"cases": list_demo_cases(context["current_lang"])})
    return templates.TemplateResponse(request, "cases.html", context)


@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request) -> HTMLResponse:
    _require_owner_request(request)
    context = _shared_context(request)
    context.update({"records": list_feedback_records()})
    return templates.TemplateResponse(request, "feedback.html", context)


@app.post("/feedback/browser", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    analysis_id: str = Form(""),
    analysis_access_token: str = Form(""),
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
            "analysis_access_token": analysis_access_token.strip() or None,
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
    if settings.app_env != "development" and not _is_owner_request(request):
        if not can_view_analysis_record(result, request.query_params.get("view_key")):
            raise HTTPException(status_code=403, detail="Analysis result access denied.")
    context = _shared_context(request)
    analysis_brief_text = _build_analysis_brief_text(result.model_dump(), context["current_lang"])
    interview_practice_text = _build_interview_practice_text(result.model_dump(), context["current_lang"])
    context.update(
        {
            "result": result.model_dump(),
            "analysis_mode": result.analysis_mode,
            "result_view_path": f"/analysis/{analysis_id}",
            "result_query_suffix": f"&view_key={result.access_token}{context['admin_query_suffix']}" if result.access_token else context["admin_query_suffix"],
            "analysis_brief_text": analysis_brief_text,
            "interview_practice_text": interview_practice_text,
        }
    )
    return templates.TemplateResponse(request, "result.html", context)


@app.get("/analysis/{analysis_id}/json", response_class=JSONResponse)
async def analysis_json(request: Request, analysis_id: str) -> JSONResponse:
    result = get_analysis_record(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found.")
    if settings.app_env != "development" and not _is_owner_request(request):
        if not can_view_analysis_record(result, request.query_params.get("view_key")):
            raise HTTPException(status_code=403, detail="Analysis result access denied.")
    return JSONResponse(content=result.model_dump())


def _build_analysis_brief_text(result: dict, lang: str) -> str:
    match = result.get("match", {})
    jd = result.get("jd", {})
    user_copy = match.get("user_copy") or {}
    lines = [
        f"{_label(lang, 'Target role', '目标岗位')}: {jd.get('role_title') or _label(lang, 'Unknown role', '未识别岗位')}",
        f"{_label(lang, 'Current call', '当前判断')}: {user_copy.get(f'headline_{resolve_lang(lang)}') or translate_dynamic(match.get('application_recommendation') or '', lang)}",
        f"{_label(lang, 'Risk level', '投递风险')}: {translate_dynamic(match.get('application_risk_level') or '', lang)}",
        f"{_label(lang, 'Recruiter first reaction', '招聘方第一反应')}: {user_copy.get(f'recruiter_{resolve_lang(lang)}') or translate_dynamic(match.get('recruiter_takeaway') or '', lang)}",
        "",
        _label(lang, 'Fix before applying:', '投递前先补：'),
    ]
    for item in match.get("must_fix_now") or []:
        lines.append(f"- {translate_dynamic(item, lang)}")
    if match.get("can_improve_later"):
        lines.append("")
        lines.append(_label(lang, 'Improve later:', '之后再优化：'))
        for item in match.get("can_improve_later") or []:
            lines.append(f"- {translate_dynamic(item, lang)}")
    return "\n".join(lines)


def _build_interview_practice_text(result: dict, lang: str) -> str:
    interview = result.get("interview") or {}
    if not interview:
        return ""
    lines = [
        _label(lang, 'Interview practice sheet', '面试练习卡'),
        translate_dynamic(interview.get("intro_prompt") or "", lang),
        "",
    ]
    for index, question in enumerate(interview.get("questions") or [], start=1):
        lines.append(f"{index}. {translate_dynamic(question.get('question') or '', lang)}")
        why_asked = question.get("why_asked") or ""
        if why_asked:
            lines.append(f"   {_label(lang, 'Why asked', '为什么会问')}: {translate_dynamic(why_asked, lang)}")
        answer_outline = question.get("answer_outline") or []
        if answer_outline:
            lines.append(f"   {_label(lang, 'Answer outline', '回答骨架')}:")
            for step in answer_outline:
                lines.append(f"   - {translate_dynamic(step, lang)}")
        pitfall = question.get("pitfall_to_avoid") or ""
        if pitfall:
            lines.append(f"   {_label(lang, 'Pitfall', '最容易答偏')}: {translate_dynamic(pitfall, lang)}")
        practice_prompt = question.get("practice_prompt") or ""
        if practice_prompt:
            lines.append(f"   {_label(lang, 'Practice prompt', '练习提示')}: {translate_dynamic(practice_prompt, lang)}")
        lines.append("")
    return "\n".join(lines).strip()


def _label(lang: str, en: str, zh: str) -> str:
    return zh if resolve_lang(lang) == "zh" else en
