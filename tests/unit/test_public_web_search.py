from __future__ import annotations

import unittest
from unittest.mock import patch

from backend.api.schemas.domain import JobDescriptionDocument
from backend.services.research.public_web_search import run_public_web_research


class _FakeDDGS:
    def __init__(self, timeout: int = 8) -> None:
        self.timeout = timeout

    def __enter__(self) -> "_FakeDDGS":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def text(self, query: str, max_results: int = 5):
        if "interview" in query.lower():
            return [
                {
                    "title": "Supply Chain Analyst interview questions",
                    "href": "https://example.com/interview",
                    "body": "Interview guide focused on SQL, planning, and supply chain trade-offs.",
                }
            ]
        return [
            {
                "title": "Supply Chain Analyst role guide",
                "href": "https://example.com/career",
                "body": "Role overview mentions excel, sql, and supplier coordination.",
            }
        ]


class PublicWebSearchTests(unittest.TestCase):
    def test_disabled_public_research_returns_empty_report(self) -> None:
        jd = JobDescriptionDocument(raw_text="Role: Analyst", role_title="Analyst")

        report = run_public_web_research(jd=jd, enabled=False)

        self.assertFalse(report.enabled)
        self.assertFalse(report.source_cards)
        self.assertTrue(report.queries)

    @patch("backend.services.research.public_web_search.DDGS", _FakeDDGS)
    def test_public_research_collects_sources_and_insights(self) -> None:
        jd = JobDescriptionDocument(
            raw_text="Role: Supply Chain Analyst. Requirements: Excel, SQL, procurement.",
            role_title="Supply Chain Analyst",
            hard_skills=["excel", "sql", "procurement"],
        )

        report = run_public_web_research(jd=jd, enabled=True, max_results=3)

        self.assertTrue(report.enabled)
        self.assertGreaterEqual(len(report.source_cards), 2)
        self.assertIn("Collected", report.summary)
        self.assertTrue(any(card.source_type == "interview" for card in report.source_cards))
        self.assertTrue(any("Repeated public signals mention" in item for item in report.insights))


if __name__ == "__main__":
    unittest.main()
