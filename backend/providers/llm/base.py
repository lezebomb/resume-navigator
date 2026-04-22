from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class RewriteRequest:
    section_name: str
    original_text: str
    job_description: str


class LLMProvider(Protocol):
    def explain_findings(self, structured_payload: dict) -> str:
        """Convert structured analysis output into a user-facing explanation."""

    def rewrite_section(self, request: RewriteRequest) -> str:
        """Generate a safe section-level rewrite suggestion."""
