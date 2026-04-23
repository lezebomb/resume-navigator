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
                    title=f"用经历直接回答 JD：{_shorten(card.requirement, 28)}",
                    target_section="experience",
                    reason="把 JD 的必选要求直接改写成经历证明，比只在技能栏列工具更有说服力。",
                    original_excerpt=_pick_section_excerpt(resume, "experience"),
                    rewritten_example=_build_requirement_example(requirement=card.requirement, role_name=role_name),
                    evidence_checklist=[
                        "写清楚场景和业务目标",
                        "写清楚你本人做了什么",
                        "补一个结果、效率提升或业务影响",
                    ],
                    caution="不要编造自己没有做过的工具、项目或结果。",
                )
            )

    if match.missing_hard_skills:
        missing_skill = match.missing_hard_skills[0]
        cards.append(
            RewriteSuggestionCard(
                title=f"把缺失技能写成可追问的经历：{missing_skill}",
                target_section="projects",
                reason="招聘方不会因为你写了一个技能名就相信你，会继续追问你在哪个场景里真正用过它。",
                original_excerpt=_pick_section_excerpt(resume, "projects"),
                rewritten_example=_build_skill_example(skill=missing_skill, role_name=role_name),
                evidence_checklist=[
                    "补充具体任务",
                    "补充使用方式而不是只写工具名",
                    "补充输出结果或决策支持",
                ],
                caution="如果你没有真实用过这个技能，应该如实补学习计划，而不是冒充有项目经验。",
            )
        )

    if match.missing_keywords:
        cards.append(
            RewriteSuggestionCard(
                title="把关键词改成自然出现，而不是堆砌",
                target_section="experience",
                reason="关键词应该落在动作、项目、结果里，而不是独立堆在一行。",
                original_excerpt=_pick_section_excerpt(resume, "experience"),
                rewritten_example=_build_keyword_example(match.missing_keywords[:3]),
                evidence_checklist=[
                    "让关键词和业务动作放在同一句",
                    "尽量配一个量化结果",
                    "避免只在技能栏重复堆词",
                ],
                caution="关键词优化是为了提升可读性，不是为了堆砌热词。",
            )
        )

    if not cards:
        cards.append(
            RewriteSuggestionCard(
                title="继续细化最强经历",
                target_section="experience",
                reason="当前基础匹配已经不错，下一步主要是让最强经历更像真实面试里的高分回答。",
                original_excerpt=_pick_section_excerpt(resume, "experience"),
                rewritten_example=(
                    "负责某核心项目/分析任务，围绕业务目标拆解问题，推动跨部门执行，并在限定周期内交付可量化结果。"
                ),
                evidence_checklist=[
                    "补上背景",
                    "补上动作",
                    "补上结果",
                ],
                caution="优先强化你最强的一到两段经历，不要平均用力。",
            )
        )

    strategy = _build_strategy(match)
    return RewritePlan(
        summary="这些改写建议优先解决“招聘方看不出来你是否真的满足 JD”的问题，再处理措辞优化。",
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
        strategy.append("先把最贴近 JD 的经历改成可直接被招聘方理解和追问的表达。")
    return strategy


def _build_requirement_example(*, requirement: str, role_name: str) -> str:
    compact_requirement = _shorten(requirement, 34)
    return (
        f"围绕 {role_name} 的核心要求“{compact_requirement}”，我在某次真实项目/实习中负责整理业务数据、推进跨团队协同，"
        "输出可执行分析或推进结果，并最终支撑了更快的交付、决策或流程优化。"
    )


def _build_skill_example(*, skill: str, role_name: str) -> str:
    if skill.lower() == "sql":
        return (
            f"在一段与 {role_name} 相关的分析任务中，我使用 SQL 对多来源业务数据进行清洗、关联和汇总，"
            "定位关键异常并输出报表/分析结论，帮助团队更快做出采购、计划或运营判断。"
        )
    return (
        f"在一段与 {role_name} 相关的项目中，我实际使用 {skill} 完成数据处理、分析支持或流程推进，"
        "并把结果落到了具体的业务动作或交付结果上。"
    )


def _build_keyword_example(keywords: list[str]) -> str:
    compact = "、".join(keywords)
    return (
        f"负责与 {compact} 相关的分析/执行任务，围绕业务目标推进问题定位、信息整理和结果输出，"
        "并通过更清晰的数据与沟通支持后续决策。"
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
