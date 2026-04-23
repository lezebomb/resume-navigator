from __future__ import annotations

import unittest

from backend.api.schemas.domain import AtsReport, ResumeDocument, ResumeMetrics, ResumeSection
from backend.services.jd.parser import parse_job_description
from backend.services.matching.engine import evaluate_resume_match


class MatchingEngineTests(unittest.TestCase):
    def test_missing_hard_skills_are_reported(self) -> None:
        resume = ResumeDocument(
            filename="resume.docx",
            file_type="docx",
            raw_text="""
            张三
            13812345678
            zhangsan@example.com
            技能
            Python SQL Excel
            工作经历
            2023.01-2024.12 数据分析实习生
            - Built reporting dashboards that reduced manual reporting time by 35%
            - 主导周报自动化改造，提升团队交付效率
            教育背景
            本科
            """,
            sections=[
                ResumeSection(section_type="skills", heading="技能", content="Python SQL Excel", bullet_count=0),
                ResumeSection(
                    section_type="experience",
                    heading="工作经历",
                    content=(
                        "2023.01-2024.12 数据分析实习生\n"
                        "- Built reporting dashboards that reduced manual reporting time by 35%\n"
                        "- 主导周报自动化改造，提升团队交付效率"
                    ),
                    bullet_count=2,
                ),
                ResumeSection(section_type="education", heading="教育背景", content="本科", bullet_count=0),
            ],
            metrics=ResumeMetrics(
                page_count=1,
                word_count=90,
                bullet_count=2,
                numeric_token_count=2,
                date_range_count=2,
                action_verb_count=3,
                table_count=0,
                image_count=0,
                text_page_ratio=1.0,
                section_count=3,
            ),
        )
        jd = parse_job_description(
            """
            岗位：数据分析师
            任职要求：
            1. 熟悉 Python、SQL、Excel、Power BI
            2. 具备良好的沟通与跨部门协作能力
            3. 负责业务报表分析与自动化建设
            """
        )
        ats = AtsReport(score=88, findings=[])

        report = evaluate_resume_match(resume=resume, jd=jd, ats=ats)

        self.assertIn("python", report.matched_hard_skills)
        self.assertIn("power_bi", report.missing_hard_skills)
        self.assertGreaterEqual(report.overall_score, 0)
        self.assertLessEqual(report.overall_score, 100)
        self.assertGreater(report.confidence_score, 0)
        self.assertTrue(report.strength_signals)
        self.assertTrue(report.priority_actions)
        self.assertTrue(report.application_recommendation)
        self.assertTrue(report.recruiter_takeaway)
        self.assertTrue(report.diagnosis_basis)
        self.assertTrue(report.application_checklist)
        self.assertTrue(report.must_fix_now or report.can_improve_later)


if __name__ == "__main__":
    unittest.main()
