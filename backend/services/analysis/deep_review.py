from __future__ import annotations

from dataclasses import dataclass, field

from backend.api.schemas.domain import JobDescriptionDocument, MatchReport, ResumeDocument
from backend.services.shared.skill_taxonomy import HARD_SKILL_TAXONOMY


EXPERIENCE_SECTIONS = {"experience", "projects"}
LIST_ONLY_SECTIONS = {"skills", "certifications"}


@dataclass(slots=True)
class DeepReviewOutcome:
    summary: str
    confidence_delta: int = 0
    confidence_reasons: list[str] = field(default_factory=list)
    risk_signals: list[str] = field(default_factory=list)
    priority_actions: list[str] = field(default_factory=list)


def run_deep_review(
    *,
    resume: ResumeDocument,
    jd: JobDescriptionDocument,
    match: MatchReport,
) -> DeepReviewOutcome:
    _ = jd
    experience_text = _joined_section_text(resume, EXPERIENCE_SECTIONS)
    list_text = _joined_section_text(resume, LIST_ONLY_SECTIONS)
    cards_with_list_only_evidence = 0

    experience_backed_skills = 0
    list_only_skills = 0
    for skill in match.matched_hard_skills:
        if _skill_present(skill, experience_text):
            experience_backed_skills += 1
        elif _skill_present(skill, list_text):
            list_only_skills += 1

    for card in match.requirement_evidence:
        if card.status == "missing" or not card.evidence_lines:
            continue
        evidence_sections = {_line_section_type(resume, line) for line in card.evidence_lines}
        if evidence_sections and evidence_sections.issubset(LIST_ONLY_SECTIONS):
            cards_with_list_only_evidence += 1

    summary = (
        "Deep review checked whether matched skills are backed by experience-context evidence and whether "
        "JD evidence comes from real experience instead of only skill lists. "
        f"Found {experience_backed_skills} skills with experience evidence and {list_only_skills} skills that still look list-only."
    )
    outcome = DeepReviewOutcome(summary=summary)

    if match.matched_hard_skills and list_only_skills >= max(2, len(match.matched_hard_skills) // 2):
        outcome.confidence_delta -= 8
        outcome.confidence_reasons.append(
            "Several matched hard skills are also backed by experience or project context, but some still rely on shallow skill-list evidence."
            if experience_backed_skills
            else "Several matched hard skills only appear in skills or certification sections, not in experience or project evidence."
        )
        outcome.risk_signals.append(
            "Some matched skills are currently easy to question in interviews because they are listed, but not strongly proven in dated experience."
        )
        outcome.priority_actions.append(
            "Move at least one matched hard skill from the skills list into a dated experience or project bullet with scope and outcome context."
        )
    elif experience_backed_skills >= max(2, len(match.matched_hard_skills) // 2):
        outcome.confidence_delta += 4
        outcome.confidence_reasons.append(
            "Deep review found enough experience-context evidence behind the matched skills to support a more confident judgment."
        )

    if cards_with_list_only_evidence:
        outcome.confidence_delta -= 4
        outcome.risk_signals.append(
            "Some JD evidence currently comes from skills-list mentions instead of experience bullets, which weakens credibility in interviews."
        )
        outcome.priority_actions.append(
            "For high-priority JD requirements, add bullets that show action, context, and business outcome instead of tool names alone."
        )

    return outcome


def _joined_section_text(resume: ResumeDocument, section_types: set[str]) -> str:
    return "\n".join(section.content.lower() for section in resume.sections if section.section_type in section_types)


def _line_section_type(resume: ResumeDocument, evidence_line: str) -> str:
    lowered = evidence_line.lower()
    for section in resume.sections:
        if lowered and lowered in section.content.lower():
            return section.section_type
    return "unknown"


def _skill_present(skill: str, text: str) -> bool:
    lowered = skill.lower()
    aliases = HARD_SKILL_TAXONOMY.get(lowered, ())
    return lowered in text or any(alias.lower() in text for alias in aliases)
