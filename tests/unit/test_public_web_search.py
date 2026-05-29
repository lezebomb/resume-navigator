from __future__ import annotations

import unittest

from backend.api.schemas.domain import JobDescriptionDocument, ResearchSourceCard
from backend.services.research.public_web_search import _build_insights, _build_queries


class PublicWebSearchTests(unittest.TestCase):
    def test_query_builder_adds_role_specific_public_research_queries(self) -> None:
        jd = JobDescriptionDocument(
            raw_text="Role: Supply Chain Analyst. Requirements: SQL, supplier negotiation, inventory planning.",
            role_title="Supply Chain Analyst",
            hard_skills=["sql", "excel"],
            must_have_items=["supplier negotiation"],
        )

        queries = _build_queries(jd)

        self.assertTrue(any("github interview questions" in item for item in queries))
        self.assertTrue(any("nowcoder interview experience" in item for item in queries))
        self.assertTrue(any("supplier delay inventory planning interview" in item for item in queries))

    def test_insights_include_source_mix_summary(self) -> None:
        jd = JobDescriptionDocument(raw_text="Role: Data Analyst", role_title="Data Analyst", hard_skills=["sql"])
        cards = [
            ResearchSourceCard(
                title="SQL interview questions",
                url="https://github.com/example/sql",
                source_name="github.com",
                source_type="official",
                snippet="Interview questions and role expectations",
            ),
            ResearchSourceCard(
                title="Nowcoder interview discussion",
                url="https://www.nowcoder.com/discuss/1",
                source_name="nowcoder.com",
                source_type="community",
                snippet="Candidate interview experience",
            ),
        ]

        insights = _build_insights(jd, cards)

        self.assertTrue(any("current public-research mix" in item.lower() for item in insights))


if __name__ == "__main__":
    unittest.main()
