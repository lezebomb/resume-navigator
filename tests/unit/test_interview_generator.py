from __future__ import annotations

import unittest

from backend.api.schemas.domain import EvidenceCard, JobDescriptionDocument, MatchReport, ResumeDocument, ResumeMetrics, ResumeSection
from backend.services.interview.generator import _compress_requirement, build_interview_prep


class InterviewGeneratorTests(unittest.TestCase):
    def test_supply_chain_and_gap_questions_are_prioritized(self) -> None:
        resume = ResumeDocument(
            filename="resume.pdf",
            file_type="pdf",
            raw_text="Excel analysis communication supply chain",
            sections=[
                ResumeSection(section_type="experience", heading="Experience", content="Coordinated supply plan with Excel dashboards."),
                ResumeSection(section_type="skills", heading="Skills", content="Excel, communication"),
            ],
            metrics=ResumeMetrics(section_count=4),
        )
        jd = JobDescriptionDocument(
            raw_text="Role: Supply Chain Analyst. Requirements: Excel, SQL, cross-functional communication, inventory planning.",
            role_title="Supply Chain Analyst",
            must_have_items=["SQL", "cross-functional communication"],
            keywords=["sql", "inventory"],
        )
        match = MatchReport(
            overall_score=68,
            summary="demo",
            matched_hard_skills=["excel"],
            missing_hard_skills=["sql"],
            matched_soft_skills=["communication"],
            missing_keywords=["sql"],
            missing_requirement_count=1,
            requirement_evidence=[
                EvidenceCard(
                    title="Requirement 1",
                    status="missing",
                    requirement="SQL and cross-functional communication",
                    next_step="Add proof.",
                )
            ],
        )

        report = build_interview_prep(resume=resume, jd=jd, match=match)

        questions = [item.question for item in report.questions]
        self.assertTrue(any("SQL" in question for question in questions))
        self.assertTrue(any("supplier delay" in question.lower() for question in questions))
        self.assertTrue(any("The JD emphasizes" in question for question in questions))

    def test_analysis_roles_include_metric_definition_question(self) -> None:
        resume = ResumeDocument(
            filename="resume.pdf",
            file_type="pdf",
            raw_text="Built dashboards and analysis workflows",
            metrics=ResumeMetrics(section_count=4),
        )
        jd = JobDescriptionDocument(
            raw_text="Role: Data Analyst. Requirements: SQL, dashboards, metrics, stakeholder communication.",
            role_title="Data Analyst",
            keywords=["dashboard", "metrics"],
        )
        match = MatchReport(
            overall_score=74,
            summary="demo",
            matched_hard_skills=["excel", "data_analysis"],
        )

        report = build_interview_prep(resume=resume, jd=jd, match=match)

        questions = [item.question for item in report.questions]
        self.assertTrue(any("metric or dashboard" in question.lower() for question in questions))

    def test_requirement_compression_removes_leading_numbering(self) -> None:
        self.assertEqual(_compress_requirement("2. 熟悉 Excel、SQL，能够进行数据分析和报表搭建；"), "熟悉 Excel、SQL，能够进行数据分析和报表搭建")


if __name__ == "__main__":
    unittest.main()
