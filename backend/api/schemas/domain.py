from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Severity = Literal["info", "warning", "error"]


class AtsFinding(BaseModel):
    code: str
    severity: Severity
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResumeMetrics(BaseModel):
    page_count: int = 0
    word_count: int = 0
    bullet_count: int = 0
    numeric_token_count: int = 0
    date_range_count: int = 0
    action_verb_count: int = 0
    table_count: int = 0
    image_count: int = 0
    text_page_ratio: float = 1.0
    section_count: int = 0


class ResumeSection(BaseModel):
    section_type: str
    heading: str
    content: str
    bullet_count: int = 0
    keywords: list[str] = Field(default_factory=list)


class ResumeDocument(BaseModel):
    filename: str
    file_type: Literal["pdf", "docx"]
    raw_text: str
    sections: list[ResumeSection] = Field(default_factory=list)
    metrics: ResumeMetrics = Field(default_factory=ResumeMetrics)
    inferred_name: str | None = None
    inferred_email: str | None = None
    inferred_phone: str | None = None
    parsing_warnings: list[str] = Field(default_factory=list)


class JobDescriptionDocument(BaseModel):
    raw_text: str
    company_name: str | None = None
    role_title: str | None = None
    location: str | None = None
    industry_hint: str | None = None
    years_experience: str | None = None
    education_requirement: str | None = None
    hard_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    must_have_items: list[str] = Field(default_factory=list)
    preferred_items: list[str] = Field(default_factory=list)


class AtsReport(BaseModel):
    score: int
    findings: list[AtsFinding] = Field(default_factory=list)


class ScoreComponent(BaseModel):
    name: str
    score: int
    weight: float
    reason: str


class MatchReport(BaseModel):
    overall_score: int
    summary: str
    score_label: str = "Needs work"
    components: list[ScoreComponent] = Field(default_factory=list)
    matched_hard_skills: list[str] = Field(default_factory=list)
    missing_hard_skills: list[str] = Field(default_factory=list)
    matched_soft_skills: list[str] = Field(default_factory=list)
    missing_soft_skills: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    strength_signals: list[str] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)
    evidence_highlights: list[str] = Field(default_factory=list)
    priority_actions: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    analysis_id: str | None = None
    created_at: str | None = None
    resume: ResumeDocument
    jd: JobDescriptionDocument
    ats: AtsReport
    match: MatchReport
