from __future__ import annotations

import unittest

from backend.api.schemas.domain import EvidenceCard, JobDescriptionDocument, MatchReport, ResumeDocument, ResumeMetrics, ResumeSection
from backend.services.rewrite.planner import build_rewrite_plan


class RewritePlannerTests(unittest.TestCase):
    def test_rewrite_plan_builds_user_facing_cards(self) -> None:
        resume = ResumeDocument(
            filename="resume.pdf",
            file_type="pdf",
            raw_text="Built dashboards in Excel and helped procurement reporting.",
            sections=[
                ResumeSection(
                    section_type="experience",
                    heading="Experience",
                    content="Built weekly procurement reports and coordinated cross-team updates.",
                ),
                ResumeSection(
                    section_type="projects",
                    heading="Projects",
                    content="Analyzed supplier performance with Excel and presentation summaries.",
                ),
            ],
            metrics=ResumeMetrics(section_count=2),
        )
        jd = JobDescriptionDocument(
            raw_text="Role: Supply Chain Analyst. Requirements: SQL, supplier management, dashboard reporting.",
            role_title="Supply Chain Analyst",
            hard_skills=["sql", "excel"],
            must_have_items=["SQL analysis for reporting"],
        )
        match = MatchReport(
            overall_score=70,
            summary="demo",
            missing_hard_skills=["sql"],
            missing_keywords=["supplier_management"],
            requirement_evidence=[
                EvidenceCard(
                    title="Requirement 1",
                    status="missing",
                    requirement="SQL analysis for reporting",
                    next_step="Add proof.",
                )
            ],
        )

        plan = build_rewrite_plan(resume=resume, jd=jd, match=match)

        self.assertTrue(plan.summary.startswith("These rewrite suggestions focus"))
        self.assertTrue(plan.suggestion_cards)
        self.assertTrue(any("Turn one JD must-have into proof" in card.title for card in plan.suggestion_cards))
        self.assertTrue(any(card.evidence_checklist for card in plan.suggestion_cards))


if __name__ == "__main__":
    unittest.main()
