from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from backend.core.config import settings


FEEDBACK_PATH = settings.data_dir / "feedback_log.json"


def save_feedback(payload: dict) -> dict:
    record = {
        "feedback_id": uuid4().hex[:12],
        "created_at": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    records = _load_feedback_records()
    records.append(record)
    _write_feedback_records(records)
    return record


def list_feedback_records() -> list[dict]:
    return list(reversed(_load_feedback_records()))


def _load_feedback_records() -> list[dict]:
    if not FEEDBACK_PATH.exists():
        return []
    try:
        return json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _write_feedback_records(records: list[dict]) -> None:
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
