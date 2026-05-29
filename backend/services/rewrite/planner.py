from __future__ import annotations

from backend.api.schemas.domain import (
    JobDescriptionDocument,
    MatchReport,
    ResumeDocument,
    RewritePlan,
    RewriteSuggestionCard,
)


def build_rewrite_plan(
    *,
    resume: ResumeDocument,
    jd: JobDescriptionDocument,
    match: MatchReport,
) -> RewritePlan:
    role_name = jd.role_title or "target role"
    cards: list[RewriteSuggestionCard] = []

    if match.requirement_evidence:
        for card in match.requirement_evidence[:2]:
            cards.append(
                RewriteSuggestionCard(
                    title=f"Turn one JD must-have into proof: {_shorten(card.requirement, 32)}",
                    target_section="experience",
                    reason="Resume bullets are stronger when they answer a JD line directly instead of only naming a tool or task.",
                    original_excerpt=_pick_section_excerpt(resume, "experience"),
                    rewritten_example=_build_requirement_example(requirement=card.requirement, role_name=role_name),
                    evidence_checklist=[
                        "Name the real business context and goal.",
                        "Make your own action and ownership explicit.",
                        "Add one measurable result, efficiency gain, or business impact.",
                    ],
                    caution="Do not invent tools, projects, or results that you did not actually own.",
                )
            )

    if match.missing_hard_skills:
        missing_skill = match.missing_hard_skills[0]
        cards.append(
            RewriteSuggestionCard(
                title=f"Turn a missing skill into experience proof: {missing_skill}",
                target_section="projects",
                reason="Hiring teams do not trust a skill name by itself. They trust a real scenario that shows how you used it.",
                original_excerpt=_pick_section_excerpt(resume, "projects"),
                rewritten_example=_build_skill_example(skill=missing_skill, role_name=role_name),
                evidence_checklist=[
                    "Add the real task or analysis problem.",
                    "Explain how you actually used the skill, not just that you know it.",
                    "Close with the output, decision, or result created from that work.",
                ],
                caution="If you do not have real evidence for this skill yet, say so honestly and focus on adjacent proof instead of pretending.",
            )
        )

    if match.missing_keywords:
        cards.append(
            RewriteSuggestionCard(
                title="Make the missing keywords appear naturally",
                target_section="experience",
                reason="Keywords work best when they are attached to real business action, not stacked in a separate list.",
                original_excerpt=_pick_section_excerpt(resume, "experience"),
                rewritten_example=_build_keyword_example(match.missing_keywords[:3]),
                evidence_checklist=[
                    "Keep the keyword in the same sentence as the business action.",
                    "Pair the line with one clear outcome if possible.",
                    "Avoid repeating the same words in a detached skills block only.",
                ],
                caution="Keyword optimization should improve clarity, not turn the resume into a list of hot terms.",
            )
        )

    if not cards:
        cards.append(
            RewriteSuggestionCard(
                title="Sharpen the strongest experience first",
                target_section="experience",
                reason="The base match is already decent, so the next gain usually comes from making one or two strong experiences easier to trust and easier to retell in interviews.",
                original_excerpt=_pick_section_excerpt(resume, "experience"),
                rewritten_example=(
                    "Owned a core analysis or execution task tied to a real business goal, aligned the right stakeholders, "
                    "and delivered a measurable outcome within a clear timeline."
                ),
                evidence_checklist=[
                    "Add the context.",
                    "Add your action.",
                    "Add the result.",
                ],
                caution="Improve the strongest one or two stories first instead of spreading attention evenly across every section.",
            )
        )

    strategy = _build_strategy(match)
    return RewritePlan(
        summary="These rewrite suggestions focus on the places where the recruiter is most likely to think the resume still does not prove the JD strongly enough.",
        strategy=strategy,
        suggestion_cards=cards[:4],
    )


def _build_strategy(match: MatchReport) -> list[str]:
    strategy: list[str] = []
    if match.must_fix_now:
        strategy.extend(match.must_fix_now[:2])
    if match.can_improve_later:
        strategy.append(match.can_improve_later[0])
    if not strategy:
        strategy.append("Rewrite the experience that is closest to the JD so it is easier to trust and easier to retell.")
    return strategy


def _build_requirement_example(*, requirement: str, role_name: str) -> str:
    compact_requirement = _shorten(requirement, 34)
    return (
        f"For a {role_name}-relevant task tied to “{compact_requirement},” I organized the needed inputs, "
        "coordinated execution across the right people, and delivered a result that improved speed, clarity, or business decision quality."
    )


def _build_skill_example(*, skill: str, role_name: str) -> str:
    if skill.lower() == "sql":
        return (
            f"In a {role_name}-relevant analysis task, I used SQL to clean, join, and summarize business data, "
            "surface the key exception or trend, and turn that analysis into a report or decision input for the team."
        )
    return (
        f"In a {role_name}-relevant project, I used {skill} to complete a real analysis, process, or execution task, "
        "then turned the output into a concrete business action or delivery result."
    )


def _build_keyword_example(keywords: list[str]) -> str:
    compact = ", ".join(keywords)
    return (
        f"Owned work related to {compact}, tied the task to a clear business goal, and translated the analysis or execution into a concrete next step."
    )


def _pick_section_excerpt(resume: ResumeDocument, section_type: str) -> str:
    for section in resume.sections:
        if section.section_type == section_type and section.content.strip():
            return _shorten(section.content.strip().replace("\n", " "), 120)
    if resume.sections:
        return _shorten(resume.sections[0].content.strip().replace("\n", " "), 120)
    return ""


def _shorten(text: str, limit: int) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "..."
