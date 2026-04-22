from __future__ import annotations

import re

from backend.api.schemas.domain import AtsReport, EvidenceCard, JobDescriptionDocument, MatchReport, ResumeDocument, ScoreComponent
from backend.services.shared.skill_taxonomy import HARD_SKILL_TAXONOMY, SOFT_SKILL_TAXONOMY, match_taxonomy


WEIGHTS = {
    "ats": 0.18,
    "hard_skills": 0.20,
    "soft_skills": 0.07,
    "keywords": 0.12,
    "must_have": 0.18,
    "quantification": 0.10,
    "experience_signal": 0.15,
}
TOKEN_RE = re.compile(r"[A-Za-z0-9_+#/.%-]+|[\u4e00-\u9fff]{2,}")


def evaluate_resume_match(
    resume: ResumeDocument,
    jd: JobDescriptionDocument,
    ats: AtsReport,
) -> MatchReport:
    resume_text = resume.raw_text.lower()
    resume_hard_skills = match_taxonomy(resume.raw_text, HARD_SKILL_TAXONOMY)
    resume_soft_skills = match_taxonomy(resume.raw_text, SOFT_SKILL_TAXONOMY)

    matched_hard_skills = [skill for skill in jd.hard_skills if skill in resume_hard_skills]
    missing_hard_skills = [skill for skill in jd.hard_skills if skill not in resume_hard_skills]
    matched_soft_skills = [skill for skill in jd.soft_skills if skill in resume_soft_skills]
    missing_soft_skills = [skill for skill in jd.soft_skills if skill not in resume_soft_skills]
    matched_keywords = [keyword for keyword in jd.keywords if _keyword_present(keyword, resume_text)]
    missing_keywords = [keyword for keyword in jd.keywords if not _keyword_present(keyword, resume_text)]

    requirement_evidence = _build_requirement_evidence(resume=resume, jd=jd)
    covered_requirement_count = sum(1 for card in requirement_evidence if card.status == "covered")
    partial_requirement_count = sum(1 for card in requirement_evidence if card.status == "partial")
    missing_requirement_count = sum(1 for card in requirement_evidence if card.status == "missing")
    total_requirement_count = len(requirement_evidence)
    evidence_requirement_count = covered_requirement_count + partial_requirement_count

    hard_skill_score = _coverage_score(len(matched_hard_skills), len(jd.hard_skills), neutral_when_empty=75)
    soft_skill_score = _coverage_score(len(matched_soft_skills), len(jd.soft_skills), neutral_when_empty=70)
    keyword_score = _coverage_score(len(matched_keywords), len(jd.keywords), neutral_when_empty=70)
    quantification_score = _quantification_score(resume)
    must_have_score = _requirement_alignment_score_from_cards(requirement_evidence)
    experience_signal_score = _experience_signal_score(resume)

    components = [
        ScoreComponent(
            name="ATS readiness",
            score=ats.score,
            weight=WEIGHTS["ats"],
            reason="Measures layout safety, extractability, and core resume structure.",
        ),
        ScoreComponent(
            name="Hard skill coverage",
            score=hard_skill_score,
            weight=WEIGHTS["hard_skills"],
            reason=f"Matched {len(matched_hard_skills)} of {len(jd.hard_skills)} structured hard skills.",
        ),
        ScoreComponent(
            name="Soft skill coverage",
            score=soft_skill_score,
            weight=WEIGHTS["soft_skills"],
            reason=f"Matched {len(matched_soft_skills)} of {len(jd.soft_skills)} structured soft skills.",
        ),
        ScoreComponent(
            name="Keyword coverage",
            score=keyword_score,
            weight=WEIGHTS["keywords"],
            reason=f"Matched {len(matched_keywords)} of {len(jd.keywords)} tracked JD keywords.",
        ),
        ScoreComponent(
            name="Must-have alignment",
            score=must_have_score,
            weight=WEIGHTS["must_have"],
            reason=f"Covered {evidence_requirement_count} of {total_requirement_count} must-have requirement lines.",
        ),
        ScoreComponent(
            name="Quantification density",
            score=quantification_score,
            weight=WEIGHTS["quantification"],
            reason="Rewards resumes that show measurable outcomes with numbers, percentages, or scale.",
        ),
        ScoreComponent(
            name="Experience signal",
            score=experience_signal_score,
            weight=WEIGHTS["experience_signal"],
            reason="Rewards resumes that present timeline, action verbs, and experience/project evidence in a recruiter-friendly way.",
        ),
    ]

    weighted_score = round(sum(component.score * component.weight for component in components))
    score_label = _score_label(weighted_score)
    confidence_score, confidence_reasons = _build_confidence_review(
        resume=resume,
        jd=jd,
        ats=ats,
        matched_keywords=matched_keywords,
        matched_hard_skills=matched_hard_skills,
        covered_requirement_count=covered_requirement_count,
        partial_requirement_count=partial_requirement_count,
        total_requirement_count=total_requirement_count,
    )
    confidence_label = _confidence_label(confidence_score)
    strength_signals = _build_strength_signals(
        ats=ats,
        matched_hard_skills=matched_hard_skills,
        quantification_score=quantification_score,
        experience_signal_score=experience_signal_score,
    )
    risk_signals = _build_risk_signals(
        ats=ats,
        missing_hard_skills=missing_hard_skills,
        missing_keywords=missing_keywords,
        missing_requirements=missing_requirement_count,
        experience_signal_score=experience_signal_score,
    )
    evidence_highlights = _build_evidence_highlights(
        resume=resume,
        matched_hard_skills=matched_hard_skills,
        matched_keywords=matched_keywords,
        matched_requirements=evidence_requirement_count,
        total_requirements=total_requirement_count,
    )
    priority_actions = _build_priority_actions(
        ats=ats,
        missing_hard_skills=missing_hard_skills,
        missing_keywords=missing_keywords,
        quantification_score=quantification_score,
        missing_requirements=missing_requirement_count,
        experience_signal_score=experience_signal_score,
    )
    summary = _build_summary(
        overall_score=weighted_score,
        score_label=score_label,
        matched_hard_skills=matched_hard_skills,
        missing_hard_skills=missing_hard_skills,
        ats_score=ats.score,
        matched_requirements=evidence_requirement_count,
        total_requirements=total_requirement_count,
    )

    return MatchReport(
        overall_score=max(0, min(100, weighted_score)),
        summary=summary,
        score_label=score_label,
        confidence_score=confidence_score,
        confidence_label=confidence_label,
        components=components,
        matched_hard_skills=matched_hard_skills,
        missing_hard_skills=missing_hard_skills,
        matched_soft_skills=matched_soft_skills,
        missing_soft_skills=missing_soft_skills,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        covered_requirement_count=covered_requirement_count,
        partial_requirement_count=partial_requirement_count,
        missing_requirement_count=missing_requirement_count,
        total_requirement_count=total_requirement_count,
        strength_signals=strength_signals,
        risk_signals=risk_signals,
        evidence_highlights=evidence_highlights,
        confidence_reasons=confidence_reasons,
        requirement_evidence=requirement_evidence,
        priority_actions=priority_actions,
    )


def _coverage_score(matched: int, total: int, neutral_when_empty: int) -> int:
    if total == 0:
        return neutral_when_empty
    return round((matched / total) * 100)


def _quantification_score(resume: ResumeDocument) -> int:
    bullets = max(1, resume.metrics.bullet_count)
    density = resume.metrics.numeric_token_count / bullets
    if density >= 1.5:
        return 95
    if density >= 1.0:
        return 85
    if density >= 0.6:
        return 72
    if density >= 0.3:
        return 58
    return 40


def _experience_signal_score(resume: ResumeDocument) -> int:
    present_sections = {section.section_type for section in resume.sections}
    section_points = 30 if "experience" in present_sections else 0
    section_points += 20 if "projects" in present_sections else 0
    timeline_points = min(20, resume.metrics.date_range_count * 5)
    bullet_points = min(15, resume.metrics.bullet_count * 3)
    action_points = min(15, resume.metrics.action_verb_count * 2)
    return min(100, section_points + timeline_points + bullet_points + action_points)


def _requirement_alignment_score_from_cards(cards: list[EvidenceCard]) -> int:
    if not cards:
        return 72
    weighted_hits = sum(1.0 if card.status == "covered" else 0.6 if card.status == "partial" else 0.0 for card in cards)
    return round((weighted_hits / len(cards)) * 100)


def _build_priority_actions(
    *,
    ats: AtsReport,
    missing_hard_skills: list[str],
    missing_keywords: list[str],
    quantification_score: int,
    missing_requirements: int,
    experience_signal_score: int,
) -> list[str]:
    actions: list[str] = []
    high_risk_findings = [finding for finding in ats.findings if finding.severity == "error"]
    if high_risk_findings:
        actions.append("Fix ATS-blocking layout issues before doing any wording optimization.")
    if missing_requirements > 0:
        actions.append("Rewrite experience bullets so they directly answer more of the JD must-have lines.")
    if missing_hard_skills:
        actions.append(f"Add evidence-backed coverage for the missing hard skills: {', '.join(missing_hard_skills[:5])}.")
    if missing_keywords:
        actions.append(f"Improve keyword alignment for: {', '.join(missing_keywords[:5])}.")
    if quantification_score < 70:
        actions.append("Rewrite experience bullets with stronger metrics, scope, and outcomes.")
    if experience_signal_score < 65:
        actions.append("Strengthen timeline and ownership signals by showing dates, role scope, and action-led bullets.")
    if not actions:
        actions.append("The resume is already structurally strong. Focus next on section-level wording refinement.")
    return actions


def _build_summary(
    *,
    overall_score: int,
    score_label: str,
    matched_hard_skills: list[str],
    missing_hard_skills: list[str],
    ats_score: int,
    matched_requirements: int,
    total_requirements: int,
) -> str:
    _ = overall_score
    return (
        f"Overall match is {score_label}. ATS readiness is {ats_score}/100, "
        f"{len(matched_hard_skills)} hard skills were matched, "
        f"{len(missing_hard_skills)} remain uncovered, and "
        f"{matched_requirements}/{total_requirements or 0} must-have JD lines were covered."
    )


def _build_strength_signals(
    *,
    ats: AtsReport,
    matched_hard_skills: list[str],
    quantification_score: int,
    experience_signal_score: int,
) -> list[str]:
    strengths: list[str] = []
    if ats.score >= 85:
        strengths.append("ATS structure is already in a relatively safe range.")
    if matched_hard_skills:
        strengths.append(f"Hard-skill evidence was detected for {', '.join(matched_hard_skills[:5])}.")
    if quantification_score >= 80:
        strengths.append("The resume already shows a healthy level of quantified outcomes.")
    if experience_signal_score >= 75:
        strengths.append("Timeline and ownership signals are clear enough for recruiter scanning.")
    return strengths or ["A few baseline signals are present, so the resume can be improved without a full rewrite."]


def _build_risk_signals(
    *,
    ats: AtsReport,
    missing_hard_skills: list[str],
    missing_keywords: list[str],
    missing_requirements: int,
    experience_signal_score: int,
) -> list[str]:
    risks: list[str] = []
    high_risk_findings = [finding for finding in ats.findings if finding.severity == "error"]
    if high_risk_findings:
        risks.append("There are ATS-level extraction or layout risks that should be fixed first.")
    if missing_requirements > 0:
        risks.append(f"{missing_requirements} must-have JD lines still lack direct resume evidence.")
    if missing_hard_skills:
        risks.append(f"Missing hard-skill evidence: {', '.join(missing_hard_skills[:5])}.")
    if experience_signal_score < 65:
        risks.append("Experience bullets are not yet giving enough timeline or ownership signal.")
    if missing_keywords and len(missing_keywords) >= 3:
        risks.append("Several JD keywords are still absent, which can hurt searchability and recruiter skim speed.")
    return risks or ["No major deterministic risk cluster was detected."]


def _build_evidence_highlights(
    *,
    resume: ResumeDocument,
    matched_hard_skills: list[str],
    matched_keywords: list[str],
    matched_requirements: int,
    total_requirements: int,
) -> list[str]:
    highlights = [
        f"Detected {resume.metrics.numeric_token_count} numeric signals across the resume.",
        f"Detected {resume.metrics.date_range_count} timeline markers and {resume.metrics.action_verb_count} action verbs.",
        f"Matched {len(matched_hard_skills)} structured hard skills and {len(matched_keywords)} tracked keywords.",
    ]
    if total_requirements:
        highlights.append(
            f"Requirement-level evidence was found for {matched_requirements} of {total_requirements} must-have JD lines."
        )
    return highlights


def _build_confidence_review(
    *,
    resume: ResumeDocument,
    jd: JobDescriptionDocument,
    ats: AtsReport,
    matched_keywords: list[str],
    matched_hard_skills: list[str],
    covered_requirement_count: int,
    partial_requirement_count: int,
    total_requirement_count: int,
) -> tuple[int, list[str]]:
    score = 42
    reasons: list[str] = []
    high_risk_findings = [finding for finding in ats.findings if finding.severity == "error"]

    if ats.score >= 85 and resume.metrics.text_page_ratio >= 0.9:
        score += 16
        reasons.append("Resume extraction quality looks stable enough for deterministic review.")
    elif ats.score >= 70 and resume.metrics.text_page_ratio >= 0.8:
        score += 8

    if total_requirement_count >= 3 or len(jd.hard_skills) >= 3 or len(jd.keywords) >= 6:
        score += 14
        reasons.append("JD contains enough structured requirements to support a meaningful comparison.")
    elif total_requirement_count or jd.hard_skills:
        score += 7
    else:
        score -= 8
        reasons.append("The JD is short or weakly structured, so the comparison has less evidence than ideal.")

    if total_requirement_count:
        evidence_ratio = (covered_requirement_count + partial_requirement_count * 0.6) / total_requirement_count
        score += round(evidence_ratio * 18)
        reasons.append(
            f"Requirement-level evidence was found for {covered_requirement_count + partial_requirement_count} of {total_requirement_count} must-have JD lines."
        )
    elif matched_hard_skills or matched_keywords:
        score += 6

    if resume.metrics.section_count >= 4:
        score += 8
    elif resume.metrics.section_count < 3:
        score -= 8
        reasons.append("Resume sectioning is sparse, which weakens section-level interpretation.")

    if resume.metrics.numeric_token_count >= 4:
        score += 4

    if high_risk_findings:
        score -= 14
        reasons.append("Some ATS extraction or layout risks reduce the confidence of automated judgment.")

    if resume.metrics.word_count < 120:
        score -= 4

    return max(0, min(100, score)), reasons


def _score_label(score: int) -> str:
    if score >= 85:
        return "Strong"
    if score >= 70:
        return "Promising"
    if score >= 55:
        return "Needs focus"
    return "Needs rebuild"


def _confidence_label(score: int) -> str:
    if score >= 80:
        return "High confidence"
    if score >= 60:
        return "Medium confidence"
    return "Needs manual review"


def label_confidence(score: int) -> str:
    return _confidence_label(score)


def _extract_requirement_tokens(line: str) -> list[str]:
    stopwords = {
        "负责",
        "熟悉",
        "掌握",
        "能够",
        "优先",
        "要求",
        "具备",
        "以及",
        "相关",
        "工作",
        "经验",
        "能力",
        "以上",
        "至少",
        "良好",
        "候选人",
        "岗位",
        "职位",
        "have",
        "must",
        "required",
        "preferred",
        "nice",
        "to",
    }
    tokens = [token.lower() for token in TOKEN_RE.findall(line)]
    return [token for token in tokens if token not in stopwords and len(token) >= 2][:8]


def _keyword_present(keyword: str, resume_text: str) -> bool:
    lowered = keyword.lower()
    if lowered in HARD_SKILL_TAXONOMY:
        return any(alias.lower() in resume_text for alias in HARD_SKILL_TAXONOMY[lowered] + (lowered,))
    if lowered in SOFT_SKILL_TAXONOMY:
        return any(alias.lower() in resume_text for alias in SOFT_SKILL_TAXONOMY[lowered] + (lowered,))
    return lowered in resume_text


def _build_requirement_evidence(resume: ResumeDocument, jd: JobDescriptionDocument) -> list[EvidenceCard]:
    if not jd.must_have_items:
        return []

    resume_lines = [line.strip() for line in resume.raw_text.splitlines() if line.strip()]
    cards: list[EvidenceCard] = []

    for index, requirement in enumerate(jd.must_have_items, start=1):
        tokens = _extract_requirement_tokens(requirement)
        matched_lines: list[str] = []

        for line in resume_lines:
            lower_line = line.lower()
            hits = sum(1 for token in tokens if token in lower_line or _token_alias_hit(token, lower_line))
            if hits >= max(1, min(2, len(tokens))):
                matched_lines.append(line)
            if len(matched_lines) >= 2:
                break

        if matched_lines:
            status = "covered" if len(matched_lines) >= 2 or len(tokens) <= 2 else "partial"
            next_step = "Keep the evidence but make the accomplishment more specific with scope or metrics."
        else:
            status = "missing"
            next_step = "Add a resume bullet that directly proves this JD requirement with a real project, task, or result."

        cards.append(
            EvidenceCard(
                title=f"Requirement {index}",
                status=status,
                requirement=requirement,
                evidence_lines=matched_lines,
                next_step=next_step,
            )
        )

    return cards


def _token_alias_hit(token: str, resume_line: str) -> bool:
    if token in HARD_SKILL_TAXONOMY:
        return any(alias.lower() in resume_line for alias in HARD_SKILL_TAXONOMY[token])
    if token in SOFT_SKILL_TAXONOMY:
        return any(alias.lower() in resume_line for alias in SOFT_SKILL_TAXONOMY[token])
    return False
