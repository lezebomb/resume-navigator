from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from apps.web.i18n import translate_dynamic, translate_stage_name
from apps.web.main import app
from backend.api.schemas.domain import AnalysisResult, AnalysisStage, AtsReport, JobDescriptionDocument, MatchReport, ResumeDocument, ResumeMetrics


class WebAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_home_page_defaults_to_chinese(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("分析模式", response.text)
        self.assertIn("深度诊断", response.text)

    def test_home_page_can_switch_to_english(self) -> None:
        response = self.client.get("/?lang=en")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Analysis mode", response.text)
        self.assertIn("Deep audit", response.text)

    def test_translation_helpers_cover_key_labels(self) -> None:
        self.assertEqual(translate_dynamic("Strong", "zh"), "强匹配")
        self.assertEqual(translate_stage_name("deep_review", "zh"), "深度复核")

    @patch("apps.web.main.analyze_resume_against_jd")
    def test_browser_analysis_renders_result_with_language_links(self, analyze_mock) -> None:
        analyze_mock.return_value = AnalysisResult(
            analysis_id="demo-123",
            analysis_mode="deep",
            stages=[AnalysisStage(name="deep_review", detail="Deep review checked whether matched skills are backed by experience-context evidence and whether JD evidence comes from real experience instead of only skill lists. Found 1 skills with experience evidence and 1 skills that still look list-only.", duration_ms=12)],
            resume=ResumeDocument(
                filename="resume.pdf",
                file_type="pdf",
                raw_text="demo",
                metrics=ResumeMetrics(page_count=1, section_count=4),
            ),
            jd=JobDescriptionDocument(raw_text="Role: Analyst", role_title="Analyst"),
            ats=AtsReport(score=88),
            match=MatchReport(
                overall_score=72,
                summary="Overall match is Promising. ATS readiness is 88/100, 2 hard skills were matched, 1 remain uncovered, and 1/2 must-have JD lines were covered.",
                score_label="Promising",
                confidence_score=79,
                confidence_label="Medium confidence",
                confidence_reasons=["Deep review found enough experience-context evidence behind the matched skills to support a more confident judgment."],
            ),
        )

        response = self.client.post(
            "/analyze/browser",
            data={"jd_text": "Role: Analyst", "analysis_mode": "deep", "lang": "en"},
            files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("/analysis/demo-123?lang=en", response.text)
        self.assertIn("Why this result is more trustworthy", response.text)


if __name__ == "__main__":
    unittest.main()
