from __future__ import annotations

import unittest

from backend.api.schemas.domain import ResumeDocument, ResumeMetrics, ResumeSection
from backend.services.ats.engine import evaluate_ats_readiness


class AtsEngineTests(unittest.TestCase):
    def test_flags_missing_contact_and_timeline_signals(self) -> None:
        resume = ResumeDocument(
            filename="resume.pdf",
            file_type="pdf",
            raw_text="工作经历\n- 负责数据整理",
            sections=[
                ResumeSection(section_type="experience", heading="工作经历", content="- 负责数据整理", bullet_count=1),
            ],
            metrics=ResumeMetrics(
                page_count=1,
                word_count=20,
                bullet_count=1,
                numeric_token_count=0,
                date_range_count=0,
                action_verb_count=1,
                table_count=0,
                image_count=0,
                text_page_ratio=1.0,
                section_count=1,
            ),
            parsing_warnings=[],
        )

        report = evaluate_ats_readiness(resume)
        codes = {finding.code for finding in report.findings}

        self.assertIn("missing_email", codes)
        self.assertIn("missing_phone", codes)
        self.assertIn("timeline_signal_weak", codes)
        self.assertLess(report.score, 100)


if __name__ == "__main__":
    unittest.main()
