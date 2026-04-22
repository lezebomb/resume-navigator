from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.api.schemas.domain import AnalysisResult
from backend.core.config import settings


HISTORY_PATH = settings.data_dir / "analysis_history.json"


def save_analysis_result(result: AnalysisResult) -> AnalysisResult:
    analysis_id = result.analysis_id or uuid4().hex[:12]
    created_at = result.created_at or datetime.now(timezone.utc).isoformat()
    hydrated = result.model_copy(update={"analysis_id": analysis_id, "created_at": created_at})

    records = _load_all_records()
    records.append(hydrated.model_dump())
    _write_records(records)
    return hydrated


def list_analysis_history() -> list[dict]:
    records = _load_all_records()
    summaries: list[dict] = []
    for record in reversed(records):
        summaries.append(
            {
                "analysis_id": record.get("analysis_id"),
                "created_at": record.get("created_at"),
                "filename": record.get("resume", {}).get("filename"),
                "role_title": record.get("jd", {}).get("role_title"),
                "company_name": record.get("jd", {}).get("company_name"),
                "ats_score": record.get("ats", {}).get("score"),
                "match_score": record.get("match", {}).get("overall_score"),
                "summary": record.get("match", {}).get("summary"),
            }
        )
    return summaries


def get_analysis_record(analysis_id: str) -> AnalysisResult | None:
    for record in _load_all_records():
        if record.get("analysis_id") == analysis_id:
            return AnalysisResult.model_validate(record)
    return None


def _load_all_records() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _write_records(records: list[dict]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
