from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
