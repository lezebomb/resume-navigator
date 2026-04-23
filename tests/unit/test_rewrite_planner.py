from __future__ import annotations

import unittest

from backend.api.schemas.domain import EvidenceCard, JobDescriptionDocument, MatchReport, ResumeDocument, ResumeMetrics, ResumeSection
from backend.services.rewrite.planner import build_rewrite_plan


class RewritePlannerTests(unittest.TestCase):
    def test_rewrite_plan_prioritizes_requirement_and_skill_gap(self) -> None:
        resume = ResumeDocument(
            filename="resume.pdf",
            file_type="pdf",
            raw_text="Experience: built reports with Excel. Projects: dashboard support.",
            sections=[
                ResumeSection(section_type="experience", heading="Experience", content="Built reports with Excel support."),
                ResumeSection(section_type="projects", heading="Projects", content="Dashboard support for team reviews."),
            ],
            metrics=ResumeMetrics(section_count=2),
        )
        jd = JobDescriptionDocument(
            raw_text="Role: Supply Chain Analyst. Requirement: SQL, Excel, procurement, cross-functional work.",
            role_title="Supply Chain Analyst",
        )
        match = MatchReport(
            overall_score=64,
            summary="demo",
            missing_hard_skills=["sql"],
            missing_keywords=["supply_chain_analyst", "sql"],
            must_fix_now=["1 must-have JD lines still do not have direct resume proof."],
            can_improve_later=["Improve natural keyword alignment for: supply_chain_analyst, sql."],
            requirement_evidence=[
                EvidenceCard(
                    title="Requirement 1",
                    status="missing",
                    requirement="SQL and cross-functional communication",
                    next_step="Add proof.",
                )
            ],
        )

        plan = build_rewrite_plan(resume=resume, jd=jd, match=match)

        self.assertTrue(plan.summary)
        self.assertGreaterEqual(len(plan.suggestion_cards), 2)
        self.assertTrue(any("sql" in card.title.lower() or "sql" in card.rewritten_example.lower() for card in plan.suggestion_cards))
        self.assertTrue(plan.strategy)


if __name__ == "__main__":
    unittest.main()
