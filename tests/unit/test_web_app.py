from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from apps.web.i18n import translate_dynamic, translate_stage_name
from apps.web.main import app
from backend.api.schemas.domain import AnalysisResult, AtsReport, JobDescriptionDocument, MatchReport, ResumeDocument, ResumeMetrics, ResumeSection


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
        self.assertIn("Do not start with the score", response.text)
        self.assertIn("What you get immediately", response.text)
        self.assertNotIn("Build note", response.text)
        self.assertNotIn("API docs", response.text)

    def test_translation_helpers_cover_key_labels(self) -> None:
        self.assertEqual(translate_dynamic("Strong", "zh"), "强匹配")
        self.assertEqual(translate_stage_name("deep_review", "zh"), "深度复核")

    @patch("apps.web.main.create_analysis_job")
    def test_browser_analysis_redirects_to_job_page(self, create_job_mock) -> None:
        create_job_mock.return_value = type("FakeJob", (), {"job_id": "job-123"})()

        response = self.client.post(
            "/analyze/browser",
            data={"jd_text": "Role: Analyst", "analysis_mode": "deep", "lang": "en"},
            files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/analyze/jobs/job-123?lang=en")

    @patch("apps.web.main.create_analysis_job")
    def test_browser_analysis_can_enable_public_research(self, create_job_mock) -> None:
        create_job_mock.return_value = type("FakeJob", (), {"job_id": "job-456"})()

        response = self.client.post(
            "/analyze/browser",
            data={
                "jd_text": "Role: Analyst",
                "analysis_mode": "deep",
                "lang": "zh",
                "enable_public_research": "on",
            },
            files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertTrue(create_job_mock.call_args.kwargs["enable_public_research"])

    @patch("apps.web.main.get_analysis_job")
    def test_job_status_can_return_translated_stage_copy(self, get_job_mock) -> None:
        get_job_mock.return_value = type(
            "FakeJob",
            (),
            {
                "to_dict": lambda self: {
                    "job_id": "job-123",
                    "filename": "resume.pdf",
                    "analysis_mode": "deep",
                    "status": "running",
                    "created_at": "2026-04-22T00:00:00+00:00",
                    "updated_at": "2026-04-22T00:00:01+00:00",
                    "current_stage_name": "deep_review",
                    "current_stage_detail": "Deep review checked whether matched skills are backed by experience-context evidence and whether JD evidence comes from real experience instead of only skill lists. Found 1 skills with experience evidence and 1 skills that still look list-only.",
                    "stages": [
                        {
                            "name": "deep_review",
                            "detail": "Deep review checked whether matched skills are backed by experience-context evidence and whether JD evidence comes from real experience instead of only skill lists. Found 1 skills with experience evidence and 1 skills that still look list-only.",
                            "duration_ms": 12,
                        }
                    ],
                    "result_analysis_id": None,
                    "error_message": None,
                }
            },
        )()

        response = self.client.get("/analyze/jobs/job-123/status?lang=zh")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["stages"][0]["display_name"], "深度复核")
        self.assertIn("深度复核检查了已匹配技能", payload["stages"][0]["display_detail"])


    @patch("apps.web.main.get_analysis_record")
    def test_result_page_is_user_facing_and_hides_developer_disclosure(self, get_record_mock) -> None:
        get_record_mock.return_value = AnalysisResult(
            analysis_id="demo-1",
            analysis_mode="deep",
            resume=ResumeDocument(
                filename="resume.pdf",
                file_type="pdf",
                raw_text="demo",
                sections=[ResumeSection(section_type="experience", heading="Experience", content="Led reporting workflow.")],
                metrics=ResumeMetrics(page_count=1, bullet_count=3, numeric_token_count=2, date_range_count=2, action_verb_count=3),
            ),
            jd=JobDescriptionDocument(
                raw_text="Role: Analyst",
                role_title="Data Analyst",
                hard_skills=["sql", "excel"],
                must_have_items=["SQL analysis", "dashboard ownership"],
            ),
            ats=AtsReport(score=86, findings=[]),
            match=MatchReport(
                overall_score=78,
                summary="Overall match is promising.",
                score_label="Promising",
                application_recommendation="Can apply, but prepare explanations first",
                application_risk_level="Medium application risk",
                recruiter_takeaway="A recruiter is likely to see some relevant background, but still ask whether the resume really proves the JD must-haves.",
                interview_risk_summary="The interview is likely to focus on whether your strongest experience really covers the must-have JD lines.",
                confidence_score=80,
                confidence_label="High confidence",
                diagnosis_basis=[
                    "The resume is readable enough for ATS-style extraction and deterministic checking.",
                    "The current result is heavily affected by missing proof on the JD must-have lines.",
                ],
                application_checklist=[
                    "Before applying, make sure the strongest experience bullet directly answers one JD must-have."
                ],
                must_fix_now=["Rewrite experience bullets so they directly answer more of the JD must-have lines."],
                can_improve_later=["Add stronger quantified outcomes so recruiters can see scale and business impact faster."],
                matched_hard_skills=["excel"],
                missing_hard_skills=["sql"],
                missing_keywords=["dashboard"],
                confidence_reasons=[
                    "Resume extraction quality looks stable enough for deterministic review.",
                    "JD contains enough structured requirements to support a meaningful comparison.",
                ],
                priority_actions=["Rewrite experience bullets so they directly answer more of the JD must-have lines."],
            ),
        )

        response = self.client.get("/analysis/demo-1?lang=en")

        self.assertEqual(response.status_code, 200)
        self.assertIn("What this conclusion is based on", response.text)
        self.assertIn("Pre-application checklist", response.text)
        self.assertNotIn("Developer disclosure", response.text)
        self.assertNotIn("Analysis process", response.text)


if __name__ == "__main__":
    unittest.main()
