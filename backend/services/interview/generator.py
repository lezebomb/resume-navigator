from __future__ import annotations

from backend.api.schemas.domain import InterviewPrepReport, InterviewQuestionCard, JobDescriptionDocument, MatchReport, ResumeDocument


def build_interview_prep(
    *,
    resume: ResumeDocument,
    jd: JobDescriptionDocument,
    match: MatchReport,
) -> InterviewPrepReport:
    questions: list[InterviewQuestionCard] = []
    role_name = jd.role_title or "this role"
    matched_skills = set(match.matched_hard_skills)
    missing_skills = set(match.missing_hard_skills)
    lower_role = (jd.role_title or "").lower()
    is_supply_chain = "supply" in lower_role or "采购" in jd.raw_text or "供应链" in jd.raw_text or "procurement" in jd.raw_text.lower()
    is_data_role = "data" in lower_role or "分析" in jd.raw_text or "sql" in jd.raw_text.lower()

    questions.append(
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

    if "excel" in matched_skills or "data_analysis" in matched_skills:
        questions.append(
            InterviewQuestionCard(
                category="tooling",
                priority="high",
                question="Tell me about a time you used Excel or analysis tooling to turn messy data into a clear decision.",
                why_asked="Interviewers want proof that your tool usage connects to business judgment, not just mechanical操作.",
                answer_focus=[
                    "How the data was messy or incomplete",
                    "What framework or analysis steps you used",
                    "What recommendation or operational action followed",
                ],
            )
        )

    if is_supply_chain:
        questions.append(
            InterviewQuestionCard(
                category="domain",
                priority="high",
                question="Tell me about a time you had to balance cost, timeliness, and operational feasibility in a supply chain or procurement task.",
                why_asked="Supply chain interviews often test whether you can reason through trade-offs instead of optimizing only one metric.",
                answer_focus=[
                    "The competing goals or constraints",
                    "How you prioritized and aligned stakeholders",
                    "What result you achieved and what you would improve next time",
                ],
            )
        )

    if is_data_role:
        questions.append(
            InterviewQuestionCard(
                category="analysis",
                priority="high",
                question="If a core business metric suddenly dropped this week, how would you structure the analysis and narrow down the cause?",
                why_asked="Data and analytical roles are frequently tested on structured problem decomposition under ambiguity.",
                answer_focus=[
                    "How you define and segment the metric",
                    "How you separate data quality from real business change",
                    "What hypotheses you would test first",
                ],
            )
        )

    if "communication" in match.matched_soft_skills or "execution" in match.missing_keywords or match.missing_requirement_count > 0:
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

    questions.append(
        InterviewQuestionCard(
            category="uncertainty",
            priority="medium",
            question="Tell me about a time you had incomplete information but still needed to make a recommendation.",
            why_asked="Real jobs rarely provide perfect data, so interviewers look for judgment under uncertainty.",
            answer_focus=[
                "What was unknown or ambiguous",
                "What assumptions you made and how you managed risk",
                "What happened after your recommendation",
            ],
        )
    )

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

    return InterviewPrepReport(
        summary="This interview pack prioritizes the questions most likely to surface based on your current resume evidence, visible gaps, and JD requirements.",
        intro_prompt="Practice answering these in spoken language, not written language. Keep each answer concrete, role-specific, and outcome-oriented.",
        questions=questions[:7],
    )
