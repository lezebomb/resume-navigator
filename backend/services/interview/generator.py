from __future__ import annotations

import re

from backend.api.schemas.domain import (
    EvidenceCard,
    InterviewPrepReport,
    InterviewQuestionCard,
    JobDescriptionDocument,
    MatchReport,
    PublicResearchReport,
    ReferenceLink,
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
    role_flags = _detect_role_flags(jd)
    questions: list[InterviewQuestionCard] = []

    questions.append(
        InterviewQuestionCard(
            category="pitch",
            priority="high",
            question=f"Give me a 60-second introduction tailored to the {role_name} role.",
            why_asked="Interviewers use this to judge role fit, communication clarity, and whether your story matches the JD from the first minute.",
            answer_focus=[
                "Who you are right now",
                "Which past experiences map most directly to the target role",
                "One concrete result with numbers or business impact",
            ],
        )
    )
    questions.append(
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
        )
    )

    targeted_cards = _pick_target_requirement_cards(match.requirement_evidence)
    for card in targeted_cards[:2]:
        questions.append(_build_requirement_question(_compress_requirement(card.requirement), card.status))

    prioritized_skills = _prioritized_skills(match, jd)
    for skill in prioritized_skills[:2]:
        questions.append(_build_skill_question(skill=skill, role_name=role_name, is_gap=skill.lower() in {item.lower() for item in match.missing_hard_skills}))

    questions.extend(_build_role_specific_questions(role_name=role_name, role_flags=role_flags))

    if research and research.source_cards:
        questions.append(_build_public_research_question(role_flags, role_name))

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

    questions = _dedupe_questions(questions)
    questions = _attach_answer_support(questions)
    questions = _attach_reference_links(
        questions=questions,
        jd=jd,
        match=match,
        research=research,
        role_flags=role_flags,
    )[:8]

    reference_count = sum(len(item.related_links) for item in questions)
    return InterviewPrepReport(
        summary="This interview pack prioritizes the questions most likely to surface based on your current resume evidence, visible gaps, JD must-haves, and public interview patterns for similar roles.",
        intro_prompt="Practice answering these in spoken language, not written language. Keep each answer concrete, role-specific, and outcome-oriented.",
        answer_method=[
            "Use a short structure: context, your action, measurable result, and what decision or lesson came out of it.",
            "When the question points to a missing skill, answer honestly with the deepest real example you do have.",
            "When the JD is emphasized, always pull the answer back to that requirement instead of giving a generic story.",
        ],
        reference_summary=(
            f"Attached {reference_count} public reference links from interview-style, community, and role-expectation sources."
            if reference_count
            else ""
        ),
        questions=questions,
    )


def _prioritized_skills(match: MatchReport, jd: JobDescriptionDocument) -> list[str]:
    ordered = [
        *match.missing_hard_skills,
        *jd.hard_skills,
    ]
    seen: set[str] = set()
    result: list[str] = []
    for item in ordered:
        normalized = item.replace("_", " ").strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _build_skill_question(*, skill: str, role_name: str, is_gap: bool) -> InterviewQuestionCard:
    normalized = skill.replace("_", " ").lower()
    priority = "high" if is_gap else "medium"

    if normalized == "sql":
        return InterviewQuestionCard(
            category="skill",
            priority=priority,
            question=f"For the {role_name} role, SQL is a visible requirement. Tell me about the deepest SQL analysis or reporting work you have actually done.",
            why_asked="SQL is often treated as a proof skill: interviewers want to know whether it is resume decoration or a real working tool.",
            answer_focus=[
                "What business problem forced you to write or debug SQL",
                "Which joins, aggregations, or logic you used",
                "What decision, metric, or workflow changed because of that analysis",
            ],
        )

    if normalized == "excel":
        return InterviewQuestionCard(
            category="skill",
            priority=priority,
            question=f"This {role_name} role is likely to use Excel heavily. Tell me about the most decision-critical Excel workflow you owned.",
            why_asked="Hiring teams often use Excel questions to test how close the candidate really is to day-to-day execution and reporting.",
            answer_focus=[
                "What workbook, model, or reporting flow you owned",
                "What formulas, pivots, lookups, or controls mattered most",
                "What decision or efficiency gain the workflow supported",
            ],
        )

    if normalized in {"procurement", "sourcing"}:
        return InterviewQuestionCard(
            category="skill",
            priority=priority,
            question=f"Tell me about a supplier selection, sourcing, or procurement decision that you personally pushed forward for a {role_name}-type problem.",
            why_asked="Procurement-related roles are often tested on judgment, supplier comparison, and cost-risk trade-off clarity.",
            answer_focus=[
                "What the purchasing need or sourcing constraint was",
                "How you compared suppliers, quotes, or negotiation options",
                "What business outcome or risk reduction came from the final choice",
            ],
        )

    if normalized in {"inventory", "inventory planning", "forecasting", "planning"}:
        return InterviewQuestionCard(
            category="skill",
            priority=priority,
            question=f"Walk me through an inventory, forecast, or planning decision that mattered in a {role_name}-type context.",
            why_asked="Planning-heavy roles are usually tested on signal reading, exception handling, and trade-offs under uncertainty.",
            answer_focus=[
                "What signal suggested the plan needed intervention",
                "What data or assumptions you checked first",
                "How you balanced service level, cost, or feasibility",
            ],
        )

    return InterviewQuestionCard(
        category="skill",
        priority=priority,
        question=f"The JD calls out {normalized}. Tell me about the strongest real example in your experience that proves depth in this area.",
        why_asked="Interviewers often convert a named JD skill into a proof question to see whether it is real, recent, and relevant.",
        answer_focus=[
            "What the real business task was",
            "What you personally handled with this skill",
            "What measurable result or decision followed",
        ],
    )


def _build_role_specific_questions(*, role_name: str, role_flags: dict[str, bool]) -> list[InterviewQuestionCard]:
    questions: list[InterviewQuestionCard] = []

    if role_flags["supply_chain"] or role_flags["operations"]:
        questions.append(
            InterviewQuestionCard(
                category="domain",
                priority="high",
                question=f"In a {role_name}-type role, delays and exceptions are common. Walk me through one supplier delay, shortage, or execution exception you handled.",
                why_asked="Operations-facing roles frequently test whether the candidate can stabilize execution under pressure instead of only describing routine work.",
                answer_focus=[
                    "What signal told you the plan was breaking",
                    "How you coordinated suppliers, internal teams, or data inputs",
                    "What trade-off you made on cost, service level, or lead time",
                ],
            )
        )

    if role_flags["analysis"]:
        questions.append(
            InterviewQuestionCard(
                category="analysis",
                priority="high",
                question=f"For a {role_name} role, pick one metric or dashboard you used regularly. How was it defined, where did the data come from, and what decision did it support?",
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
                why_asked="Analytical roles are often tested on structured decomposition, not only tool familiarity.",
                answer_focus=[
                    "How you define and segment the metric",
                    "How you separate data quality from real business change",
                    "What hypotheses you would test first",
                ],
            )
        )

    if role_flags["procurement"]:
        questions.append(
            InterviewQuestionCard(
                category="domain",
                priority="high",
                question=f"Describe a purchasing or vendor negotiation decision you made that involved a real cost-risk trade-off relevant to {role_name}.",
                why_asked="Procurement interviews often go beyond process and test commercial judgment, supplier handling, and risk awareness.",
                answer_focus=[
                    "What commercial target or constraint you were given",
                    "How you evaluated suppliers or negotiation options",
                    "What trade-off you accepted and why",
                ],
            )
        )

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
    return questions


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
        "supply_chain": any(token in haystack for token in ("supply", "inventory", "logistics", "planning", "采购", "供应链", "库存", "物流", "计划")),
        "procurement": any(token in haystack for token in ("procurement", "sourcing", "supplier", "vendor", "采购", "寻源", "供应商")),
        "operations": any(token in haystack for token in ("operations", "fulfillment", "delivery", "执行", "运营", "交付")),
        "analysis": any(token in haystack for token in ("analysis", "analyst", "data", "sql", "dashboard", "metrics", "分析", "数据", "指标", "报表")),
    }


def _pick_target_requirement_cards(cards: list[EvidenceCard]) -> list[EvidenceCard]:
    ordered: list[EvidenceCard] = []
    for preferred_status in ("missing", "partial"):
        for card in cards:
            if card.status == preferred_status:
                ordered.append(card)
    return ordered


def _compress_requirement(requirement: str) -> str:
    compact = requirement.strip().replace("\n", " ")
    compact = re.sub(r"\s+", " ", compact)
    compact = re.sub(r"^(?:任职要求|requirements?)\s*[:：]?\s*", "", compact, flags=re.IGNORECASE)
    compact = re.sub(r"^[\-\*\u2022\u25cf\u25a0]+\s*", "", compact)
    compact = re.sub(r"^\d+\s*[\.\)\]:：、]+\s*", "", compact)
    compact = compact.rstrip("：:。.;；")
    if len(compact) <= 48:
        return compact
    return compact[:48].rstrip(",.;:；。") + "..."


def _build_requirement_question(requirement: str, status: str) -> InterviewQuestionCard:
    priority = "high" if status == "missing" else "medium"
    return InterviewQuestionCard(
        category="proof",
        priority=priority,
        question=f"The JD emphasizes {requirement}. Tell me about the strongest example in your experience that proves it.",
        why_asked="Interviewers often convert a visible JD requirement gap into a direct proof question.",
        answer_focus=[
            "What the task or business goal actually was",
            "What you personally owned and executed",
            "What outcome, metric, or learning came out of it",
        ],
    )


def _build_public_research_question(role_flags: dict[str, bool], role_name: str) -> InterviewQuestionCard:
    if role_flags["supply_chain"] or role_flags["procurement"]:
        return InterviewQuestionCard(
            category="research",
            priority="medium",
            question=f"Public interview write-ups for {role_name}-type roles often focus on one end-to-end planning, sourcing, or execution decision. Which decision are you most prepared to defend in detail?",
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
        question=f"Public interview write-ups for {role_name}-type roles often test how you move from vague business goals to a structured analysis plan. What example from your experience best proves that ability?",
        why_asked="Public interview write-ups for similar roles repeatedly emphasize structured thinking, not just tool familiarity.",
        answer_focus=[
            "What the ambiguous goal was",
            "How you turned it into a measurable analysis plan",
            "What recommendation or decision came out of it",
        ],
    )


def _attach_reference_links(
    *,
    questions: list[InterviewQuestionCard],
    jd: JobDescriptionDocument,
    match: MatchReport,
    research: PublicResearchReport | None,
    role_flags: dict[str, bool],
) -> list[InterviewQuestionCard]:
    if not research or not research.source_cards:
        return questions

    role_tokens = _tokenize(f"{jd.role_title or ''} {' '.join(jd.hard_skills)} {' '.join(jd.must_have_items)}")
    missing_skill_tokens = _tokenize(" ".join(match.missing_hard_skills))
    enriched: list[InterviewQuestionCard] = []

    for question in questions:
        focus_terms = set(role_tokens)
        focus_terms.update(_tokenize(question.question))
        focus_terms.update(_tokenize(question.why_asked))
        if question.category in {"skill", "proof"}:
            focus_terms.update(missing_skill_tokens)
        if role_flags["supply_chain"] and question.category in {"domain", "research"}:
            focus_terms.update({"supplier", "inventory", "planning", "procurement", "logistics"})
        if role_flags["analysis"] and question.category in {"analysis", "research"}:
            focus_terms.update({"sql", "dashboard", "metric", "analysis", "data"})

        preferred_types = _preferred_source_types(question.category)
        related_links = _pick_relevant_links(research.source_cards, focus_terms, preferred_types)
        enriched.append(question.model_copy(update={"related_links": related_links}))
    return enriched


def _attach_answer_support(questions: list[InterviewQuestionCard]) -> list[InterviewQuestionCard]:
    enriched: list[InterviewQuestionCard] = []
    for question in questions:
        enriched.append(
            question.model_copy(
                update={
                    "answer_outline": _build_answer_outline(question),
                    "pitfall_to_avoid": _build_pitfall_to_avoid(question),
                    "practice_prompt": _build_practice_prompt(question),
                }
            )
        )
    return enriched


def _build_answer_outline(question: InterviewQuestionCard) -> list[str]:
    if question.category == "pitch":
        return [
            "Open with who you are now and the role direction you are targeting.",
            "Name the one or two experiences that map most directly to this role.",
            "Close with one measurable result that proves why you are ready now.",
        ]
    if question.category in {"project", "proof", "skill", "domain"}:
        return [
            "Start with the exact business context and why the task mattered.",
            "Make your ownership explicit before describing tools, coordination, or process.",
            "End with the outcome, metric, or business decision that changed because of your work.",
        ]
    if question.category == "analysis":
        return [
            "Define the business question and the metric or signal you were trying to explain.",
            "Walk through your data logic, analysis steps, and how you narrowed the hypotheses.",
            "End with the decision, recommendation, or operational change that followed.",
        ]
    if question.category == "collaboration":
        return [
            "State the disagreement clearly and why it mattered to the business.",
            "Explain how you aligned people using evidence instead of only opinion.",
            "Finish with the agreement reached and what execution result followed.",
        ]
    if question.category == "motivation":
        return [
            "Say why this role fits your current direction right now.",
            "Explain what has changed in your experience that makes you more ready than before.",
            "Close with the value you believe you can create early in the role.",
        ]
    return [
        "Answer with one real example instead of a definition or a generic opinion.",
        "Keep your ownership, action, and result in the same answer.",
        "End by tying the story back to the role requirement behind the question.",
    ]


def _build_pitfall_to_avoid(question: InterviewQuestionCard) -> str:
    if question.category == "pitch":
        return "Do not turn this into a full life story. Keep it role-specific and business-relevant."
    if question.category in {"proof", "skill"}:
        return "Do not answer like a textbook. Use one real, dated example instead of only explaining concepts."
    if question.category == "analysis":
        return "Do not list tools first. Start from the business question and only then explain the analysis."
    if question.category == "collaboration":
        return "Do not frame the story as other people being wrong. Show how you created alignment and kept execution moving."
    if question.category == "motivation":
        return "Do not give a generic passion answer. Tie your motivation back to this role and your recent trajectory."
    return "Do not stay abstract. Give a concrete example with ownership and outcome."


def _build_practice_prompt(question: InterviewQuestionCard) -> str:
    if question.priority == "high":
        return "Practice this answer aloud in 60 to 90 seconds first, then prepare a deeper 2-minute version."
    return "Practice this answer aloud once in under 90 seconds so it sounds natural instead of memorized."


def _preferred_source_types(category: str) -> tuple[str, ...]:
    if category in {"research", "proof", "domain"}:
        return ("interview", "community", "official")
    if category == "skill":
        return ("interview", "official", "career")
    return ("interview", "career", "community")


def _pick_relevant_links(source_cards, focus_terms: set[str], preferred_types: tuple[str, ...], limit: int = 2) -> list[ReferenceLink]:
    scored: list[tuple[int, object]] = []
    for card in source_cards:
        haystack = _tokenize(f"{card.title} {card.snippet} {card.query} {card.source_name}")
        overlap = len(focus_terms.intersection(haystack))
        score = overlap * 3
        if card.source_type in preferred_types:
            score += 5
        score += round(card.credibility_score / 20)
        if score <= 0:
            continue
        scored.append((score, card))

    scored.sort(key=lambda item: (item[0], getattr(item[1], "credibility_score", 0)), reverse=True)
    links: list[ReferenceLink] = []
    seen_urls: set[str] = set()
    for _, card in scored:
        if card.url in seen_urls:
            continue
        seen_urls.add(card.url)
        links.append(
            ReferenceLink(
                title=card.title,
                url=card.url,
                source_name=card.source_name,
                note=card.query,
            )
        )
        if len(links) >= limit:
            break
    return links


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z0-9_+#/.%-]+|[\u4e00-\u9fff]{2,}", text.lower())
    cleaned = {token.replace("_", " ") for token in tokens if len(token.strip()) >= 2}
    return cleaned


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
