from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Resume Navigator")
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    data_dir: Path = PROJECT_ROOT / os.getenv("DATA_DIR", "data/runtime")
    upload_dir: Path = PROJECT_ROOT / os.getenv("UPLOAD_DIR", "data/uploads")
    export_dir: Path = PROJECT_ROOT / os.getenv("EXPORT_DIR", "data/exports")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/runtime/resume_navigator.db")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    enable_external_enrichment: bool = os.getenv("ENABLE_EXTERNAL_ENRICHMENT", "false").lower() == "true"
    enable_private_research_connectors: bool = (
        os.getenv("ENABLE_PRIVATE_RESEARCH_CONNECTORS", "false").lower() == "true"
    )
    private_research_connectors: tuple[str, ...] = tuple(
        item.strip()
        for item in os.getenv("PRIVATE_RESEARCH_CONNECTORS", "").split(",")
        if item.strip()
    )

    def ensure_runtime_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
