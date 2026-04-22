from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from apps.web.i18n import translate_dynamic, translate_stage_name
from apps.web.main import app


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


if __name__ == "__main__":
    unittest.main()
