from __future__ import annotations

import re

from backend.api.schemas.domain import (
    EvidenceCard,
    InterviewPrepReport,
    InterviewQuestionCard,
    JobDescriptionDocument,
    MatchReport,
    PublicResearchReport,
    ResumeDocument,
)


def build_interview_prep(
    *,
    resume: ResumeDocument,
    jd: JobDescriptionDocument,
    match: MatchReport,
    research: PublicResearchReport | None = None,
) -> InterviewPrepReport:
    role_name = jd.role_title or "this role"
    questions: list[InterviewQuestionCard] = [
        InterviewQuestionCard(
            category="pitch",
            priority="high",
            question="Give me a 60-second introduction tailored to this role.",
            why_asked="Interviewers use this to judge role fit, communication clarity, and whether your story matches the JD from the first minute.",
            answer_focus=[
                "Who you are right now",
                "Which past experiences map most directly to the target role",
                "One concrete result with numbers or business impact",
            ],
        ),
        InterviewQuestionCard(
            category="project",
            priority="high",
            question="Pick the project or experience on your resume that best matches this JD and walk me through it end to end.",
            why_asked="This checks whether the strongest line on the resume is real, well understood, and relevant to the hiring need.",
            answer_focus=[
                "Situation and business context",
                "Your exact role and ownership",
                "Actions, trade-offs, and final outcome",
            ],
        ),
    ]

    targeted_requirement = _pick_target_requirement(match.requirement_evidence)
    if targeted_requirement:
        questions.append(_build_requirement_question(targeted_requirement))

    role_flags = _detect_role_flags(jd)
    matched_skills = {skill.lower() for skill in match.matched_hard_skills}
    missing_skills = {skill.lower() for skill in match.missing_hard_skills}

    if "sql" in missing_skills:
        questions.append(
            InterviewQuestionCard(
                category="gap",
                priority="high",
                question="Your resume does not show strong SQL evidence yet. Tell me about the most complex SQL analysis you have actually done.",
                why_asked="A visible skill gap on the resume often turns into a direct verification question in the interview.",
                answer_focus=[
                    "Business problem behind the query",
                    "Joins, aggregations, or window functions you used",
                    "What decision or result the analysis enabled",
                ],
            )
        )

    if role_flags["supply_chain"]:
        questions.append(
            InterviewQuestionCard(
                category="domain",
                priority="high",
                question="Walk me through a supplier delay, shortage, or planning exception you handled. How did you diagnose it and protect delivery?",
                why_asked="Operations and supply chain interviews frequently test whether you can stabilize execution under pressure, not just describe routine work.",
                answer_focus=[
                    "What signal told you the plan was breaking",
                    "How you coordinated suppliers, internal teams, or data inputs",
                    "What trade-off you made on cost, service level, or lead time",
                ],
            )
        )

    if role_flags["analysis"] or "excel" in matched_skills or "data_analysis" in matched_skills:
        questions.append(
            InterviewQuestionCard(
                category="analysis",
                priority="high",
                question="Pick one metric or dashboard you used regularly. How was it defined, where did the data come from, and what decision did it support?",
                why_asked="Analyst interviews often check whether you understand the business meaning and trust boundaries behind the numbers, not just the final chart.",
                answer_focus=[
                    "How the metric was defined",
                    "What source tables, files, or systems fed it",
                    "How the metric changed a business decision",
                ],
            )
        )
        questions.append(
            InterviewQuestionCard(
                category="analysis",
                priority="medium",
                question="If a core business metric suddenly dropped this week, how would you structure the analysis and narrow down the cause?",
                why_asked="Data and analytical roles are frequently tested on structured problem decomposition under ambiguity.",
                answer_focus=[
                    "How you define and segment the metric",
                    "How you separate data quality from real business change",
                    "What hypotheses you would test first",
                ],
            )
        )

    if "communication" in match.matched_soft_skills or match.missing_requirement_count > 0:
        questions.append(
            InterviewQuestionCard(
                category="collaboration",
                priority="medium",
                question="Describe a cross-functional disagreement and how you got alignment without losing execution speed.",
                why_asked="Hiring teams use this to test collaboration maturity, stakeholder handling, and execution discipline.",
                answer_focus=[
                    "What each side cared about",
                    "How you reframed the problem with evidence",
                    "What agreement or next step you secured",
                ],
            )
        )

    if role_flags["supply_chain"]:
        questions.append(
            InterviewQuestionCard(
                category="domain",
                priority="medium",
                question="Tell me about a time you had to balance cost, timeliness, and operational feasibility in a supply chain or procurement task.",
                why_asked="Supply chain interviews often test whether you can reason through trade-offs instead of optimizing only one metric.",
                answer_focus=[
                    "The competing goals or constraints",
                    "How you prioritized and aligned stakeholders",
                    "What result you achieved and what you would improve next time",
                ],
            )
        )

    if research and research.source_cards:
        questions.append(_build_public_research_question(role_flags))

    questions.append(
        InterviewQuestionCard(
            category="motivation",
            priority="medium",
            question=f"Why this role, and why are you a better fit for {role_name} now than six months ago?",
            why_asked="This helps interviewers see self-awareness, motivation, and whether your trajectory is becoming more aligned with the role.",
            answer_focus=[
                "Why this role fits your current direction",
                "What has changed in your experience recently",
                "What specific value you can create early",
            ],
        )
    )

    questions = _dedupe_questions(questions)[:7]
    return InterviewPrepReport(
        summary="This interview pack prioritizes the questions most likely to surface based on your current resume evidence, visible gaps, and JD requirements.",
        intro_prompt="Practice answering these in spoken language, not written language. Keep each answer concrete, role-specific, and outcome-oriented.",
        questions=questions,
    )


def _detect_role_flags(jd: JobDescriptionDocument) -> dict[str, bool]:
    haystack = " ".join(
        filter(
            None,
            [
                jd.role_title or "",
                jd.industry_hint or "",
                jd.raw_text or "",
                " ".join(jd.keywords),
                " ".join(jd.must_have_items),
            ],
        )
    ).lower()
    return {
        "supply_chain": any(token in haystack for token in ("supply", "procurement", "inventory", "logistics", "采购", "供应链", "库存", "物流", "计划")),
        "analysis": any(token in haystack for token in ("analysis", "analyst", "data", "sql", "dashboard", "metrics", "分析", "数据", "指标", "报表")),
    }


def _pick_target_requirement(cards: list[EvidenceCard]) -> str | None:
    for preferred_status in ("missing", "partial"):
        for card in cards:
            if card.status == preferred_status:
                return _compress_requirement(card.requirement)
    return None


def _compress_requirement(requirement: str) -> str:
    compact = requirement.strip().replace("\n", " ")
    compact = re.sub(r"\s+", " ", compact)
    compact = re.sub(r"^(?:任职要求|requirements?)\s*[:：]?\s*", "", compact, flags=re.IGNORECASE)
    compact = re.sub(r"^[\-\*\u2022\u25cf\u25a0]+\s*", "", compact)
    compact = re.sub(r"^\d+\s*[\.\)\]:：、-]+\s*", "", compact)
    compact = compact.rstrip("；;。.")
    if len(compact) <= 40:
        return compact
    return compact[:40].rstrip(",.;:；。") + "..."


def _build_requirement_question(requirement: str) -> InterviewQuestionCard:
    return InterviewQuestionCard(
        category="proof",
        priority="high",
        question=f"The JD emphasizes {requirement}. Tell me about the strongest example in your experience that proves it.",
        why_asked="Interviewers often convert a visible requirement gap into a direct proof question.",
        answer_focus=[
            "What the task or business goal actually was",
            "What you personally owned and executed",
            "What outcome, metric, or learning came out of it",
        ],
    )


def _build_public_research_question(role_flags: dict[str, bool]) -> InterviewQuestionCard:
    if role_flags["supply_chain"]:
        return InterviewQuestionCard(
            category="research",
            priority="medium",
            question="Public interview write-ups for similar roles often focus on one end-to-end planning or procurement decision. Which decision are you most prepared to defend in detail?",
            why_asked="Public interview write-ups for similar roles repeatedly emphasize ownership, judgment, and trade-off clarity.",
            answer_focus=[
                "What triggered the decision",
                "What options you compared",
                "What business result followed",
            ],
        )
    return InterviewQuestionCard(
        category="research",
        priority="medium",
        question="Public interview write-ups for similar roles often test how you move from vague business goals to a structured analysis plan. What example from your experience best proves that ability?",
        why_asked="Public interview write-ups for similar roles repeatedly emphasize structured thinking, not just tool familiarity.",
        answer_focus=[
            "What the ambiguous goal was",
            "How you turned it into a measurable analysis plan",
            "What recommendation or decision came out of it",
        ],
    )


def _dedupe_questions(questions: list[InterviewQuestionCard]) -> list[InterviewQuestionCard]:
    seen: set[str] = set()
    ordered: list[InterviewQuestionCard] = []
    for item in questions:
        normalized = re.sub(r"\s+", " ", item.question.strip().lower())
        if normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(item)
    return ordered
