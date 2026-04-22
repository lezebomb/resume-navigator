from __future__ import annotations

from backend.api.schemas.domain import AtsFinding, AtsReport, ResumeDocument


ESSENTIAL_SECTIONS: dict[str, str] = {
    "education": "Education section is missing or not clearly labeled.",
    "experience": "Work experience or internship section is missing or not clearly labeled.",
    "skills": "Skills section is missing or not clearly labeled.",
}


def evaluate_ats_readiness(resume: ResumeDocument) -> AtsReport:
    findings: list[AtsFinding] = []
    score = 100

    metrics = resume.metrics
    present_sections = {section.section_type for section in resume.sections}
    experience_like_sections = {"experience", "projects"} & present_sections

    if metrics.page_count > 2:
        score -= 8
        findings.append(
            AtsFinding(
                code="page_count_high",
                severity="warning",
                message=f"Resume length is {metrics.page_count} pages. Keeping it within 1-2 pages is usually safer.",
                metadata={"page_count": metrics.page_count},
            )
        )

    if metrics.table_count > 0:
        score -= 18
        findings.append(
            AtsFinding(
                code="tables_detected",
                severity="error",
                message="Table-based layout was detected. Many ATS parsers lose ordering or drop table content.",
                metadata={"table_count": metrics.table_count},
            )
        )

    if metrics.image_count > 0:
        score -= 8
        findings.append(
            AtsFinding(
                code="images_detected",
                severity="warning",
                message="Images or icons were detected. ATS systems often ignore visual content.",
                metadata={"image_count": metrics.image_count},
            )
        )

    if metrics.text_page_ratio < 0.8:
        score -= 20
        findings.append(
            AtsFinding(
                code="low_extractability",
                severity="error",
                message="Text extraction quality looks weak. The file may contain scan-only pages or layout issues.",
                metadata={"text_page_ratio": metrics.text_page_ratio},
            )
        )
    elif metrics.text_page_ratio < 1.0:
        score -= 8
        findings.append(
            AtsFinding(
                code="partial_extractability",
                severity="warning",
                message="Some pages extracted less cleanly than others. Multi-column or complex layout may be involved.",
                metadata={"text_page_ratio": metrics.text_page_ratio},
            )
        )

    if metrics.word_count < 120:
        score -= 8
        findings.append(
            AtsFinding(
                code="content_too_short",
                severity="warning",
                message="Resume content looks short. Important context may be missing for ATS or recruiter review.",
                metadata={"word_count": metrics.word_count},
            )
        )

    if metrics.bullet_count < 3:
        score -= 5
        findings.append(
            AtsFinding(
                code="few_bullets",
                severity="warning",
                message="The resume has very few bullet points. Achievement-oriented bullets usually improve readability.",
                metadata={"bullet_count": metrics.bullet_count},
            )
        )

    if not resume.inferred_email:
        score -= 4
        findings.append(
            AtsFinding(
                code="missing_email",
                severity="warning",
                message="Email was not reliably detected. Recruiters and ATS exports need clear contact information.",
            )
        )

    if not resume.inferred_phone:
        score -= 4
        findings.append(
            AtsFinding(
                code="missing_phone",
                severity="warning",
                message="Phone number was not reliably detected. Add a clean phone line near the top of the resume.",
            )
        )

    if metrics.section_count < 3:
        score -= 6
        findings.append(
            AtsFinding(
                code="section_count_low",
                severity="warning",
                message="The resume structure looks sparse. Clear section boundaries improve both ATS parsing and human scanning.",
                metadata={"section_count": metrics.section_count},
            )
        )

    if metrics.date_range_count < 2:
        score -= 6
        findings.append(
            AtsFinding(
                code="timeline_signal_weak",
                severity="warning",
                message="Very few date ranges were detected. Recruiters usually expect visible timeline signals for experience and education.",
                metadata={"date_range_count": metrics.date_range_count},
            )
        )

    if experience_like_sections and metrics.action_verb_count < max(2, metrics.bullet_count):
        score -= 5
        findings.append(
            AtsFinding(
                code="achievement_language_weak",
                severity="warning",
                message="Experience bullets look light on action verbs. Rewrite bullets to show ownership, actions, and outcomes more clearly.",
                metadata={"action_verb_count": metrics.action_verb_count},
            )
        )

    for section_name, message in ESSENTIAL_SECTIONS.items():
        if section_name not in present_sections:
            score -= 8
            findings.append(
                AtsFinding(
                    code=f"missing_{section_name}",
                    severity="warning",
                    message=message,
                )
            )

    for warning_message in resume.parsing_warnings:
        findings.append(
            AtsFinding(
                code="parsing_warning",
                severity="info",
                message=warning_message,
            )
        )

    if not findings:
        findings.append(
            AtsFinding(
                code="ats_clear",
                severity="info",
                message="No major ATS compatibility issues were detected by the deterministic rule engine.",
            )
        )

    return AtsReport(score=max(0, min(100, score)), findings=findings)
