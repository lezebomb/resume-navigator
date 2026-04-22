from __future__ import annotations

import unittest

from backend.api.schemas.domain import JobDescriptionDocument, MatchReport, ResumeDocument, ResumeMetrics
from backend.services.interview.generator import build_interview_prep


class InterviewGeneratorTests(unittest.TestCase):
    def test_missing_sql_gap_turns_into_interview_question(self) -> None:
        resume = ResumeDocument(
            filename="resume.pdf",
            file_type="pdf",
            raw_text="Excel data analysis communication",
            metrics=ResumeMetrics(section_count=4),
        )
        jd = JobDescriptionDocument(
            raw_text="岗位：供应链分析师，需要 Excel、SQL、跨部门沟通",
            role_title="供应链分析师",
        )
        match = MatchReport(
            overall_score=68,
            summary="demo",
            matched_hard_skills=["excel", "data_analysis"],
            missing_hard_skills=["sql"],
            matched_soft_skills=["communication"],
            missing_keywords=["sql"],
            missing_requirement_count=1,
        )

        report = build_interview_prep(resume=resume, jd=jd, match=match)

        questions = [item.question for item in report.questions]
        self.assertTrue(any("SQL" in question for question in questions))
        self.assertTrue(any("cross-functional" in question for question in questions))


if __name__ == "__main__":
    unittest.main()
