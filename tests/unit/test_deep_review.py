from __future__ import annotations

import unittest

from backend.api.schemas.domain import EvidenceCard, MatchReport, ResumeDocument, ResumeMetrics, ResumeSection
from backend.services.analysis.deep_review import run_deep_review
from backend.api.schemas.domain import JobDescriptionDocument


class DeepReviewTests(unittest.TestCase):
    def test_deep_review_flags_skill_list_only_evidence(self) -> None:
        resume = ResumeDocument(
            filename="resume.pdf",
            file_type="pdf",
            raw_text="Skills\nSQL\nPython\n\nExperience\nSupported reporting",
            sections=[
                ResumeSection(section_type="skills", heading="Skills", content="SQL\nPython", bullet_count=0),
                ResumeSection(section_type="experience", heading="Experience", content="Supported reporting and weekly updates.", bullet_count=1),
            ],
            metrics=ResumeMetrics(section_count=2),
        )
        jd = JobDescriptionDocument(
            raw_text="Role: Data Analyst. Requirements: SQL, Python.",
            role_title="Data Analyst",
        )
        match = MatchReport(
            overall_score=65,
            summary="demo",
            matched_hard_skills=["sql", "python"],
            requirement_evidence=[
                EvidenceCard(
                    title="Requirement 1",
                    status="partial",
                    requirement="SQL",
                    evidence_lines=["SQL"],
                    next_step="Add proof.",
                )
            ],
        )

        outcome = run_deep_review(resume=resume, jd=jd, match=match)

        self.assertLess(outcome.confidence_delta, 0)
        self.assertTrue(any("skills" in item.lower() for item in outcome.risk_signals))
        self.assertTrue(any("dated experience or project bullet" in item.lower() for item in outcome.priority_actions))


if __name__ == "__main__":
    unittest.main()
