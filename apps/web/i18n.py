from __future__ import annotations

import re


SUPPORTED_LANGS = {"zh", "en"}

UI_TRANSLATIONS = {
    "zh": {
        "lang_name": "简体中文",
        "lang_switch_label": "语言",
        "lang_switch_zh": "中文",
        "lang_switch_en": "English",
        "brand": "Resume Navigator",
        "home_title": "把简历诊断做成真正能帮求职者拿到面试机会的产品",
        "home_subtitle": "这版优先解决三个最实际的问题：ATS 能不能读懂你的简历、你的经历是否真的对齐目标 JD、下一步应该先改哪里。我们先把确定性规则和证据链做扎实，再把大模型放到它真正擅长的位置。",
        "home_metric_analysis_count": "本地分析记录",
        "home_metric_feedback_count": "已收集反馈",
        "home_metric_chinese_first": "优先服务中文求职场景",
        "current_build": "当前版本",
        "current_build_title": "这一版已经可以做什么",
        "current_build_copy": "这不是最终 UI，而是给开发验证和早期用户试用准备的产品入口。它已经支持上传真实简历、输入真实 JD、查看评分构成、回看历史结果，并收集用户反馈。",
        "feature_resume_parse_title": "结构化简历解析",
        "feature_resume_parse_copy": "自动识别教育、经历、项目、技能、奖项等 section，并提取联系方式、时间线和量化成果信号。",
        "feature_ats_title": "可解释 ATS 体检",
        "feature_ats_copy": "检查表格、图片、文本提取质量、时间线线索、联系方式和结构完整性。",
        "feature_match_title": "更成熟的 JD 对齐判断",
        "feature_match_copy": "不只看关键词，还看 must-have 覆盖、量化结果、经历信号和证据命中。",
        "feature_feedback_title": "早期试用反馈闭环",
        "feature_feedback_copy": "结果页可直接提交“哪里不准”“哪里最有帮助”“下一步最想要什么功能”。",
        "intake_title": "立即试用诊断链路",
        "intake_subtitle": "上传一份 PDF 或 DOCX 简历，再粘贴目标岗位的 JD 文本。提交后会进入新的分析流程，而不是旧版单体逻辑。",
        "upload_label": "上传简历文件",
        "upload_note": "建议优先使用文本型 PDF 或 DOCX，不要上传纯扫描件。",
        "jd_label": "粘贴目标 JD",
        "jd_note": "尽量保留“岗位、职责、要求、优先条件”等原始信息，便于后续做更准的岗位画像。",
        "jd_placeholder": "例如：岗位：供应链分析师\n公司：某制造业公司\n任职要求：熟悉 Excel、SQL、跨部门协作、采购或供应链相关经验……",
        "analysis_mode_label": "分析模式",
        "analysis_mode_standard": "快速诊断",
        "analysis_mode_standard_note": "更快，适合初筛和日常迭代。",
        "analysis_mode_deep": "深度诊断",
        "analysis_mode_deep_note": "增加要求级证据卡片、判断置信度和分析过程追踪，更适合正式投递前复核。",
        "start_analysis": "开始分析",
        "view_history": "查看历史记录",
        "view_feedback": "查看试用反馈",
        "view_api_docs": "查看 API 文档",
        "growth_title": "开发阶段就该怎么推广",
        "growth_copy": "现在最重要的不是一次性做完所有功能，而是尽快找到真实求职者，拿到“它哪里不准、哪里有帮助”的反馈，再反哺产品。",
        "growth_step_1_title": "先招募 3 到 5 位真实求职者",
        "growth_step_1_copy": "比起泛泛宣传，更重要的是拿到带 JD 的真实简历案例。",
        "growth_step_2_title": "每周发一条开发日志",
        "growth_step_2_copy": "固定输出“这周改了什么、为什么这么改、下周准备验证什么”。",
        "growth_step_3_title": "用案例而不是口号",
        "growth_step_3_copy": "真实前后对比、真实误判修复记录，比“AI 简历神器”更容易获得信任。",
        "growth_step_4_title": "优先收集负反馈",
        "growth_step_4_copy": "“这里不准”“这里没帮助”往往就是产品该优先解决的问题。",
        "footer_note": "当前页面用于演示新的产品骨架。旧版 Streamlit 原型仍然保留，后续能力会继续迁移到新架构。",
        "result_title_suffix": "分析结果",
        "result_panel": "分析结果",
        "export_json": "导出 JSON",
        "continue_analysis": "继续分析",
        "current_assessment": "当前判断",
        "target_role": "目标岗位",
        "analysis_id": "分析编号",
        "created_at": "生成时间",
        "parsed_info": "解析信息",
        "unknown_name": "未识别姓名",
        "ats_readiness": "ATS 兼容度",
        "role_match": "岗位匹配度",
        "judgment_confidence": "判断置信度",
        "conclusion_stability": "结论稳定度",
        "conclusion_stability_copy": "它不是在说你一定能过，而是在说这次自动判断的依据是否足够稳定。",
        "analysis_mode_current": "当前模式",
        "standard_mode_label": "快速诊断",
        "deep_mode_label": "深度诊断",
        "application_call": "投递判断",
        "recruiter_impression": "招聘方第一反应",
        "fix_before_apply": "投递前先补什么",
        "improve_later": "之后再优化",
        "role_snapshot": "岗位画像",
        "role_snapshot_copy": "先看清这份 JD 想招什么人，再决定你的简历应该补什么。",
        "decision_basis": "这次结论主要基于什么",
        "decision_basis_copy": "这里展示的是影响判断的核心依据，而不是内部流水线日志。",
        "application_checklist": "投递前检查清单",
        "application_checklist_copy": "正式投递前把这些过一遍，能明显减少被动解释。",
        "matched_core_skills": "岗位核心技能",
        "must_have_focus": "JD 必选要求",
        "preferred_focus": "加分项",
        "experience_expectation": "经验要求",
        "education_expectation": "学历要求",
        "strengths_for_user": "你已经具备的优势",
        "risks_for_user": "还会被追问的点",
        "evidence_for_user": "简历里已经站得住的证据",
        "resume_snapshot": "简历概况",
        "resume_snapshot_copy": "这是给你自己看的简历摘要，不是开发日志。",
        "interview_answer_method": "回答方法",
        "interview_answer_method_copy": "先把回答结构练顺，再去润色具体措辞。",
        "strength_signals": "优势信号",
        "risk_signals": "风险信号",
        "evidence_highlights": "证据高亮",
        "ats_findings": "ATS 发现项",
        "priority_actions": "优先动作",
        "skill_coverage": "技能覆盖",
        "matched_hard_skills": "已覆盖硬技能",
        "missing_hard_skills": "缺失硬技能",
        "missing_keywords": "JD 缺失关键词",
        "none": "暂无",
        "no_obvious_gap": "无明显缺口",
        "keyword_alignment_good": "关键词对齐良好",
        "structure_profile": "结构与画像",
        "pages": "页数",
        "bullets": "要点数",
        "numeric_signals": "数字信号",
        "timeline_signals": "时间线",
        "action_verbs": "动作词",
        "text_ratio": "文本提取率",
        "score_breakdown": "评分构成",
        "weight": "权重",
        "process_trace": "分析过程",
        "process_copy": "这次结果不是一句拍脑袋的分数，而是经过结构化解析、ATS 审核、JD 对齐、要求级证据复核后得出的。",
        "requirement_evidence": "JD 要求证据卡片",
        "requirement_copy": "每一条 must-have 要求都会对照简历中的具体证据，帮助你判断“到底是没写，还是写得不够明显”。",
        "requirement_summary": "要求覆盖概览",
        "requirement_label": "要求",
        "evidence_lines": "命中的简历证据",
        "next_step": "下一步",
        "interview_handoff": "面试承接",
        "interview_copy": "这些问题不是通用题库，而是根据当前简历证据、缺口和 JD 要求生成的高概率追问。",
        "why_asked": "为什么会被问",
        "answer_focus": "回答重点",
        "priority_high": "高优先级",
        "priority_medium": "中优先级",
        "covered": "已覆盖",
        "partial": "部分覆盖",
        "missing": "未覆盖",
        "submit_feedback": "提交试用反馈",
        "feedback_copy": "如果你觉得哪里判断不准、哪里最有帮助、你下一步最想要什么功能，直接在这里提交。这会直接帮助我们决定下一轮迭代优先级。",
        "overall_rating": "整体体验（1-5）",
        "accuracy_rating": "判断准确度（1-5）",
        "usefulness_rating": "可执行性（1-5）",
        "rating_5": "5 - 很有帮助",
        "rating_4": "4 - 基本有帮助",
        "rating_3": "3 - 一般",
        "rating_2": "2 - 帮助有限",
        "rating_1": "1 - 几乎没帮助",
        "accuracy_5": "5 - 很准",
        "accuracy_4": "4 - 大体准确",
        "accuracy_3": "3 - 一半一半",
        "accuracy_2": "2 - 偏差较多",
        "accuracy_1": "1 - 很不准",
        "usefulness_5": "5 - 直接能改",
        "usefulness_4": "4 - 大部分能用",
        "usefulness_3": "3 - 需要自己再理解",
        "usefulness_2": "2 - 不够具体",
        "usefulness_1": "1 - 几乎没法用",
        "main_problem": "最不准或最不满意的地方",
        "main_problem_placeholder": "例如：把我的采购经历识别得太弱，或者 SQL 缺失判断不合理。",
        "wanted_next": "你下一步最想要的功能",
        "wanted_next_placeholder": "例如：按 JD 改写简历、生成项目 bullet、模拟面试问题、导出优化版 PDF。",
        "contact_optional": "联系方式（可选）",
        "contact_placeholder": "微信 / 邮箱，方便回访",
        "submit": "提交反馈",
        "history_kicker": "历史记录",
        "history_title": "分析历史",
        "history_copy": "这里展示通过新 Web 入口保存下来的分析结果，方便你回看分数变化、分享案例，以及做早期用户访谈。",
        "back_to_upload": "回到上传页",
        "recent_results": "最近分析结果",
        "time": "时间",
        "file": "文件",
        "target_position": "目标岗位",
        "actions": "操作",
        "view_result": "查看结果",
        "view_json": "查看 JSON",
        "no_history": "还没有历史记录。先回上传页跑一次分析，这里就会自动出现内容。",
        "feedback_kicker": "试用反馈",
        "feedback_title": "试用反馈看板",
        "feedback_copy_page": "这里会沉淀所有通过结果页提交的反馈。它不是最终后台，但足够支撑冷启动阶段的产品访谈和优先级判断。",
        "latest_feedback": "最新反馈",
        "linked_analysis": "关联分析",
        "major_problem": "主要问题",
        "next_request": "下一步诉求",
        "contact": "联系方式",
        "no_feedback": "还没有收到反馈。先跑一次分析并在结果页提交反馈，这里就会出现数据。",
        "thanks_kicker": "感谢反馈",
        "thanks_title": "反馈已收到",
        "thanks_copy": "这条反馈已经记录下来，后续我会优先根据“哪里不准、哪里最需要补”继续迭代这个产品。",
        "feedback_id": "反馈编号",
        "continue_after_feedback": "继续分析",
        "view_feedback_list": "查看反馈列表",
        "back_to_result": "返回本次结果",
        "status_error": "错误",
        "status_warning": "警告",
        "status_info": "提示",
        "unknown_role": "未识别岗位",
        "confidence_high": "高可信",
        "confidence_medium": "中等可信",
        "confidence_low": "需人工复核",
    },
    "en": {
        "lang_name": "English",
        "lang_switch_label": "Language",
        "lang_switch_zh": "中文",
        "lang_switch_en": "English",
        "brand": "Resume Navigator",
        "home_title": "Turn resume diagnosis into a product that actually helps job seekers win interviews",
        "home_subtitle": "This version focuses on three practical questions first: can ATS read the resume, does the experience really align with the JD, and what should the candidate fix next. We strengthen deterministic rules and evidence first, then put LLMs only where they truly help.",
        "home_metric_analysis_count": "Local analyses",
        "home_metric_feedback_count": "Feedback collected",
        "home_metric_chinese_first": "Built for Chinese job seekers first",
        "current_build": "Current Build",
        "current_build_title": "What this version already does",
        "current_build_copy": "This is not the final UI. It is a product entrypoint for development validation and early beta trials. It already supports real resume uploads, real JD input, score breakdowns, history, and feedback collection.",
        "feature_resume_parse_title": "Structured resume parsing",
        "feature_resume_parse_copy": "Automatically identifies education, experience, projects, skills, awards, and extracts contacts, timeline cues, and quantified signals.",
        "feature_ats_title": "Explainable ATS audit",
        "feature_ats_copy": "Checks tables, images, extraction quality, timeline cues, contact fields, and structural completeness.",
        "feature_match_title": "More mature JD alignment",
        "feature_match_copy": "Looks beyond keywords to must-have coverage, quantified outcomes, experience signals, and evidence hits.",
        "feature_feedback_title": "Early feedback loop",
        "feature_feedback_copy": "The result page lets users submit what feels wrong, useful, or missing.",
        "intake_title": "Try the analysis flow",
        "intake_subtitle": "Upload a PDF or DOCX resume, then paste the target JD text. Submission goes through the new analysis pipeline instead of the old monolith.",
        "upload_label": "Upload resume",
        "upload_note": "Prefer text-based PDF or DOCX files instead of scanned images.",
        "jd_label": "Paste target JD",
        "jd_note": "Keep original information such as role, responsibilities, requirements, and preferred qualifications whenever possible.",
        "jd_placeholder": "Example: Role: Supply Chain Analyst\nCompany: A manufacturing company\nRequirements: Excel, SQL, cross-functional collaboration, procurement or supply chain experience...",
        "analysis_mode_label": "Analysis mode",
        "analysis_mode_standard": "Quick audit",
        "analysis_mode_standard_note": "Faster. Best for rapid checks and iteration.",
        "analysis_mode_deep": "Deep audit",
        "analysis_mode_deep_note": "Adds requirement-level evidence cards, confidence scoring, and stage tracing for final review before applying.",
        "start_analysis": "Start analysis",
        "view_history": "View history",
        "view_feedback": "View feedback",
        "view_api_docs": "API docs",
        "growth_title": "How to market it during development",
        "growth_copy": "The goal is not to finish every feature first. The goal is to get real job seekers, hear where the system helps or fails, and feed that back into the product quickly.",
        "growth_step_1_title": "Recruit 3 to 5 real job seekers first",
        "growth_step_1_copy": "The priority is getting real resume + JD cases, not broad exposure yet.",
        "growth_step_2_title": "Publish one build log each week",
        "growth_step_2_copy": "Share what changed, why it changed, and what you want to validate next.",
        "growth_step_3_title": "Use cases, not slogans",
        "growth_step_3_copy": "Real before-after examples and fixed misjudgments build trust better than generic AI claims.",
        "growth_step_4_title": "Collect negative feedback first",
        "growth_step_4_copy": "The most valuable insight is usually where users say the system is wrong or not useful.",
        "footer_note": "This page demonstrates the new product foundation. The old Streamlit prototype is still preserved while features continue to move into the new architecture.",
        "result_title_suffix": "Analysis Result",
        "result_panel": "Analysis Result",
        "export_json": "Export JSON",
        "continue_analysis": "Analyze another resume",
        "current_assessment": "Current assessment",
        "target_role": "Target role",
        "analysis_id": "Analysis ID",
        "created_at": "Created at",
        "parsed_info": "Parsed profile",
        "unknown_name": "Name not detected",
        "ats_readiness": "ATS Readiness",
        "role_match": "Role Match",
        "judgment_confidence": "Judgment confidence",
        "conclusion_stability": "Decision stability",
        "conclusion_stability_copy": "This is not a promise of success. It tells you how stable the basis behind this automated judgment is.",
        "analysis_mode_current": "Current mode",
        "standard_mode_label": "Quick audit",
        "deep_mode_label": "Deep audit",
        "application_call": "Application call",
        "recruiter_impression": "Recruiter first impression",
        "fix_before_apply": "Fix before applying",
        "improve_later": "Improve later",
        "role_snapshot": "Role snapshot",
        "role_snapshot_copy": "Understand what this JD is really asking for before deciding what to strengthen in the resume.",
        "decision_basis": "What this conclusion is based on",
        "decision_basis_copy": "This shows the core basis behind the judgment, not internal pipeline logs.",
        "application_checklist": "Pre-application checklist",
        "application_checklist_copy": "Run through these before you send the final version so you spend less time explaining gaps later.",
        "matched_core_skills": "Core role skills",
        "must_have_focus": "JD must-haves",
        "preferred_focus": "Preferred items",
        "experience_expectation": "Experience expectation",
        "education_expectation": "Education expectation",
        "strengths_for_user": "What already works",
        "risks_for_user": "What will still get challenged",
        "evidence_for_user": "Evidence already working for you",
        "resume_snapshot": "Resume snapshot",
        "resume_snapshot_copy": "This is a user-facing resume summary, not a developer log.",
        "interview_answer_method": "How to answer",
        "interview_answer_method_copy": "Practice the structure first, then polish the wording.",
        "strength_signals": "Strength signals",
        "risk_signals": "Risk signals",
        "evidence_highlights": "Evidence highlights",
        "ats_findings": "ATS findings",
        "priority_actions": "Priority actions",
        "skill_coverage": "Skill coverage",
        "matched_hard_skills": "Matched hard skills",
        "missing_hard_skills": "Missing hard skills",
        "missing_keywords": "Missing JD keywords",
        "none": "None",
        "no_obvious_gap": "No obvious gap",
        "keyword_alignment_good": "Keyword alignment looks good",
        "structure_profile": "Structure and profile",
        "pages": "Pages",
        "bullets": "Bullets",
        "numeric_signals": "Numeric signals",
        "timeline_signals": "Timeline markers",
        "action_verbs": "Action verbs",
        "text_ratio": "Text ratio",
        "score_breakdown": "Score breakdown",
        "weight": "Weight",
        "process_trace": "Analysis process",
        "process_copy": "This result is not a one-line guess. It is built through structured parsing, ATS auditing, JD alignment, and requirement-level evidence review.",
        "requirement_evidence": "JD evidence cards",
        "requirement_copy": "Each must-have line is checked against concrete resume evidence so the user can see whether the issue is missing content or weak phrasing.",
        "requirement_summary": "Requirement coverage",
        "requirement_label": "Requirement",
        "evidence_lines": "Matched resume evidence",
        "next_step": "Next step",
        "interview_handoff": "Interview handoff",
        "interview_copy": "These are not generic interview questions. They are prioritized from your current resume evidence, visible gaps, and JD requirements.",
        "why_asked": "Why this gets asked",
        "answer_focus": "Answer focus",
        "priority_high": "High priority",
        "priority_medium": "Medium priority",
        "covered": "Covered",
        "partial": "Partial",
        "missing": "Missing",
        "submit_feedback": "Submit feedback",
        "feedback_copy": "If something feels inaccurate, useful, or still missing, submit it here. This directly helps us prioritize the next iteration.",
        "overall_rating": "Overall experience (1-5)",
        "accuracy_rating": "Accuracy (1-5)",
        "usefulness_rating": "Actionability (1-5)",
        "rating_5": "5 - Very helpful",
        "rating_4": "4 - Mostly helpful",
        "rating_3": "3 - Mixed",
        "rating_2": "2 - Limited value",
        "rating_1": "1 - Hardly useful",
        "accuracy_5": "5 - Very accurate",
        "accuracy_4": "4 - Mostly accurate",
        "accuracy_3": "3 - Mixed",
        "accuracy_2": "2 - Often off",
        "accuracy_1": "1 - Very inaccurate",
        "usefulness_5": "5 - Directly actionable",
        "usefulness_4": "4 - Mostly actionable",
        "usefulness_3": "3 - Needs extra interpretation",
        "usefulness_2": "2 - Not concrete enough",
        "usefulness_1": "1 - Hardly actionable",
        "main_problem": "Least accurate or most unsatisfying part",
        "main_problem_placeholder": "For example: my procurement experience was recognized too weakly, or the SQL gap feels unreasonable.",
        "wanted_next": "What feature do you want next",
        "wanted_next_placeholder": "Example: JD-based rewrite, stronger project bullets, mock interview questions, exportable optimized PDF.",
        "contact_optional": "Contact (optional)",
        "contact_placeholder": "WeChat / email for follow-up",
        "submit": "Submit",
        "history_kicker": "History",
        "history_title": "Analysis History",
        "history_copy": "This page lists the results saved through the new web entrypoint so you can review score changes, share cases, and run early user interviews.",
        "back_to_upload": "Back to upload",
        "recent_results": "Recent analyses",
        "time": "Time",
        "file": "File",
        "target_position": "Target role",
        "actions": "Actions",
        "view_result": "View result",
        "view_json": "View JSON",
        "no_history": "No history yet. Run one analysis from the upload page and entries will appear here automatically.",
        "feedback_kicker": "Beta Feedback",
        "feedback_title": "Beta Feedback Board",
        "feedback_copy_page": "This view stores all feedback submitted from the result page. It is not a full admin console yet, but it is enough to support early interviews and prioritization.",
        "latest_feedback": "Latest feedback",
        "linked_analysis": "Linked analysis",
        "major_problem": "Main issue",
        "next_request": "Next request",
        "contact": "Contact",
        "no_feedback": "No feedback yet. Run an analysis and submit feedback from the result page to populate this board.",
        "thanks_kicker": "Thank You",
        "thanks_title": "Feedback received",
        "thanks_copy": "This feedback is now recorded. Future iterations will prioritize what feels inaccurate and what users need most next.",
        "feedback_id": "Feedback ID",
        "continue_after_feedback": "Analyze again",
        "view_feedback_list": "View feedback list",
        "back_to_result": "Back to this result",
        "status_error": "error",
        "status_warning": "warning",
        "status_info": "info",
        "unknown_role": "Unknown role",
        "confidence_high": "High confidence",
        "confidence_medium": "Medium confidence",
        "confidence_low": "Needs manual review",
    },
}

STAGE_TRANSLATIONS = {
    "resume_parse": {"zh": "简历解析", "en": "Resume parsing"},
    "jd_parse": {"zh": "JD 解析", "en": "JD parsing"},
    "ats_audit": {"zh": "ATS 审核", "en": "ATS audit"},
    "match_audit": {"zh": "匹配审核", "en": "Match audit"},
    "deep_review": {"zh": "深度复核", "en": "Deep review"},
    "public_research": {"zh": "公开资料补充", "en": "Public research"},
}

_DYNAMIC_EXACT = {
    "Strong": {"zh": "强匹配", "en": "Strong"},
    "Promising": {"zh": "有潜力", "en": "Promising"},
    "Needs focus": {"zh": "需重点优化", "en": "Needs focus"},
    "Needs rebuild": {"zh": "需重构表达", "en": "Needs rebuild"},
    "High confidence": {"zh": "高可信", "en": "High confidence"},
    "Medium confidence": {"zh": "中等可信", "en": "Medium confidence"},
    "Needs manual review": {"zh": "需人工复核", "en": "Needs manual review"},
    "Fix core blockers before applying": {"zh": "建议先补齐核心阻塞项，再正式投递", "en": "Fix core blockers before applying"},
    "Ready to apply": {"zh": "可以进入投递", "en": "Ready to apply"},
    "Can apply, but prepare explanations first": {
        "zh": "可以投递，但要先准备好解释口径",
        "en": "Can apply, but prepare explanations first",
    },
    "High application risk": {"zh": "投递风险较高", "en": "High application risk"},
    "Medium application risk": {"zh": "投递风险中等", "en": "Medium application risk"},
    "Lower application risk": {"zh": "投递风险较低", "en": "Lower application risk"},
    "There are ATS-blocking risks that should be fixed before applying.": {
        "zh": "存在 ATS 阻塞风险，建议在投递前先修掉。",
        "en": "There are ATS-blocking risks that should be fixed before applying.",
    },
    "Judgment confidence is still low enough that a human review is recommended before applying.": {
        "zh": "当前自动判断的置信度还不够高，建议投递前先做人工复核。",
        "en": "Judgment confidence is still low enough that a human review is recommended before applying.",
    },
    "Add stronger quantified outcomes so recruiters can see scale and business impact faster.": {
        "zh": "补强量化结果，让招聘方更快看到你的业务规模和影响。",
        "en": "Add stronger quantified outcomes so recruiters can see scale and business impact faster.",
    },
    "Keep cleaning ATS presentation details after the core evidence gaps are fixed.": {
        "zh": "在补齐核心证据之后，再继续优化 ATS 呈现细节。",
        "en": "Keep cleaning ATS presentation details after the core evidence gaps are fixed.",
    },
    "The later improvements are mostly about polishing phrasing and section-level clarity.": {
        "zh": "后续更多是做措辞打磨和版块清晰度优化。",
        "en": "The later improvements are mostly about polishing phrasing and section-level clarity.",
    },
    "A recruiter is likely to see some relevant background, but still ask whether the resume really proves the JD must-haves.": {
        "zh": "招聘方大概率会觉得你有一定相关背景，但仍会追问这份简历是否真的证明了 JD 的核心要求。",
        "en": "A recruiter is likely to see some relevant background, but still ask whether the resume really proves the JD must-haves.",
    },
    "A recruiter may see partial alignment, but will probably probe whether the missing hard skill is a real gap or just underwritten.": {
        "zh": "招聘方可能会看到部分匹配，但也很可能追问那些缺失硬技能到底是真不会，还是只是没写清楚。",
        "en": "A recruiter may see partial alignment, but will probably probe whether the missing hard skill is a real gap or just underwritten.",
    },
    "A recruiter is likely to see a coherent fit quickly, then move into depth and ownership questions.": {
        "zh": "招聘方更可能先快速确认你整体匹配，然后转向深度、ownership 和细节追问。",
        "en": "A recruiter is likely to see a coherent fit quickly, then move into depth and ownership questions.",
    },
    "The resume is readable enough for ATS-style extraction and deterministic checking.": {
        "zh": "这份简历目前的可读性已经足够支持 ATS 风格提取和确定性诊断。",
        "en": "The resume is readable enough for ATS-style extraction and deterministic checking.",
    },
    "ATS readability is not yet stable enough, so some conclusions should be treated cautiously.": {
        "zh": "这份简历的 ATS 可读性还不够稳定，所以部分结论需要更谨慎看待。",
        "en": "ATS readability is not yet stable enough, so some conclusions should be treated cautiously.",
    },
    "The current result is heavily affected by missing proof on the JD must-have lines.": {
        "zh": "这次结论很大程度上受制于 JD 必选要求缺少直接证明。",
        "en": "The current result is heavily affected by missing proof on the JD must-have lines.",
    },
    "The current result benefits from direct evidence on the most important JD lines.": {
        "zh": "这次结论受益于你在关键 JD 要求上已经有了直接证据。",
        "en": "The current result benefits from direct evidence on the most important JD lines.",
    },
    "No obvious hard-skill blocker was detected in the current JD comparison.": {
        "zh": "当前 JD 对比中没有看到特别明显的硬技能阻塞项。",
        "en": "No obvious hard-skill blocker was detected in the current JD comparison.",
    },
    "Before applying, make sure the strongest experience bullet directly answers one JD must-have.": {
        "zh": "投递前先确认你最强的一条经历 bullet 能直接回答至少一条 JD 必选要求。",
        "en": "Before applying, make sure the strongest experience bullet directly answers one JD must-have.",
    },
    "Add at least one quantified outcome so the recruiter can see scope quickly.": {
        "zh": "至少补上一条量化结果，让招聘方更快看到你的业务范围和影响。",
        "en": "Add at least one quantified outcome so the recruiter can see scope quickly.",
    },
    "Keep one quantified result ready, because recruiters often scan for business impact first.": {
        "zh": "保留一条你最有代表性的量化结果，因为招聘方通常会先看业务影响。",
        "en": "Keep one quantified result ready, because recruiters often scan for business impact first.",
    },
    "Do one final skim for natural keyword alignment before exporting the final resume.": {
        "zh": "在导出最终简历前，再做一轮关键词自然对齐检查。",
        "en": "Do one final skim for natural keyword alignment before exporting the final resume.",
    },
    "Use a short structure: context, your action, measurable result, and what decision or lesson came out of it.": {
        "zh": "回答时尽量用短结构：背景、你的动作、量化结果，以及最后带来的决策或经验。",
        "en": "Use a short structure: context, your action, measurable result, and what decision or lesson came out of it.",
    },
    "When the question points to a missing skill, answer honestly with the deepest real example you do have.": {
        "zh": "如果问题指向缺失技能，就诚实地用你最深、最真实的相关例子来回答。",
        "en": "When the question points to a missing skill, answer honestly with the deepest real example you do have.",
    },
    "When the JD is emphasized, always pull the answer back to that requirement instead of giving a generic story.": {
        "zh": "当问题明确对应 JD 要求时，回答要始终拉回那条要求，而不是讲一个泛泛的故事。",
        "en": "When the JD is emphasized, always pull the answer back to that requirement instead of giving a generic story.",
    },
    "The interview is likely to focus on whether your strongest experience really covers the must-have JD lines.": {
        "zh": "面试更可能围绕你的最强经历是否真的覆盖了 JD 的必选要求展开。",
        "en": "The interview is likely to focus on whether your strongest experience really covers the must-have JD lines.",
    },
    "The interview is more likely to test depth, trade-offs, and stakeholder handling than basic fit.": {
        "zh": "面试更可能考你深度、取舍和协同处理，而不是基础匹配度。",
        "en": "The interview is more likely to test depth, trade-offs, and stakeholder handling than basic fit.",
    },
    "Public interview write-ups for similar roles often focus on one end-to-end planning or procurement decision. Which decision are you most prepared to defend in detail?": {
        "zh": "类似岗位的公开面经经常会追问一次完整的计划或采购决策。你最能详细讲清楚、也最经得起追问的是哪一次？",
        "en": "Public interview write-ups for similar roles often focus on one end-to-end planning or procurement decision. Which decision are you most prepared to defend in detail?",
    },
    "Public interview write-ups for similar roles repeatedly emphasize ownership, judgment, and trade-off clarity.": {
        "zh": "类似岗位的公开面经经常会重点考察候选人的真实 ownership、判断力和取舍清晰度。",
        "en": "Public interview write-ups for similar roles repeatedly emphasize ownership, judgment, and trade-off clarity.",
    },
    "What triggered the decision": {"zh": "当时是什么触发了这个决策", "en": "What triggered the decision"},
    "What options you compared": {"zh": "你当时比较了哪些可选方案", "en": "What options you compared"},
    "What business result followed": {"zh": "这个决策最终带来了什么业务结果", "en": "What business result followed"},
    "Public interview write-ups for similar roles often test how you move from vague business goals to a structured analysis plan. What example from your experience best proves that ability?": {
        "zh": "类似岗位的公开面经经常会考察你能否把模糊业务目标拆成结构化分析计划。你哪段经历最能证明这一点？",
        "en": "Public interview write-ups for similar roles often test how you move from vague business goals to a structured analysis plan. What example from your experience best proves that ability?",
    },
    "Public interview write-ups for similar roles repeatedly emphasize structured thinking, not just tool familiarity.": {
        "zh": "类似岗位的公开面经经常更看重结构化思考，而不只是工具熟练度。",
        "en": "Public interview write-ups for similar roles repeatedly emphasize structured thinking, not just tool familiarity.",
    },
    "What the ambiguous goal was": {"zh": "当时那个模糊目标到底是什么", "en": "What the ambiguous goal was"},
    "How you turned it into a measurable analysis plan": {
        "zh": "你是怎么把它拆成可衡量的分析计划的",
        "en": "How you turned it into a measurable analysis plan",
    },
    "What recommendation or decision came out of it": {
        "zh": "最后产出了什么建议或决策",
        "en": "What recommendation or decision came out of it",
    },
    "Public research is supplemental context only and does not directly change the deterministic score.": {
        "zh": "公开资料补充只作为辅助背景，不会直接改写确定性分数。",
        "en": "Public research is supplemental context only and does not directly change the deterministic score.",
    },
    "Treat public interview write-ups as qualitative signals, not as guaranteed truths about one specific company.": {
        "zh": "公开面经更适合作为定性参考，而不是某一家公司的绝对真相。",
        "en": "Treat public interview write-ups as qualitative signals, not as guaranteed truths about one specific company.",
    },
    "Public research is optional and should not block the deterministic analysis flow.": {
        "zh": "公开资料补充是可选层，不应该阻塞确定性分析主流程。",
        "en": "Public research is optional and should not block the deterministic analysis flow.",
    },
    "The deterministic report still works without public-web enrichment.": {
        "zh": "即使没有公开资料补充，确定性分析报告也可以单独成立。",
        "en": "The deterministic report still works without public-web enrichment.",
    },
    "This layer is supplemental context only and should not replace the JD itself.": {
        "zh": "这一层只补充上下文，不应该替代 JD 本身。",
        "en": "This layer is supplemental context only and should not replace the JD itself.",
    },
    "ATS readiness": {"zh": "ATS 兼容度", "en": "ATS readiness"},
    "Hard skill coverage": {"zh": "硬技能覆盖", "en": "Hard skill coverage"},
    "Soft skill coverage": {"zh": "软技能覆盖", "en": "Soft skill coverage"},
    "Keyword coverage": {"zh": "关键词覆盖", "en": "Keyword coverage"},
    "Must-have alignment": {"zh": "核心要求对齐", "en": "Must-have alignment"},
    "Quantification density": {"zh": "量化表达密度", "en": "Quantification density"},
    "Experience signal": {"zh": "经历信号强度", "en": "Experience signal"},
    "ATS structure is already in a relatively safe range.": {
        "zh": "ATS 结构已经处于相对安全区间。",
        "en": "ATS structure is already in a relatively safe range.",
    },
    "The resume already shows a healthy level of quantified outcomes.": {
        "zh": "这份简历已经体现出较好的量化成果表达。",
        "en": "The resume already shows a healthy level of quantified outcomes.",
    },
    "Timeline and ownership signals are clear enough for recruiter scanning.": {
        "zh": "时间线和负责范围信号已经足够清晰，便于招聘方快速浏览。",
        "en": "Timeline and ownership signals are clear enough for recruiter scanning.",
    },
    "There are ATS-level extraction or layout risks that should be fixed first.": {
        "zh": "存在 ATS 级别的提取或排版风险，应该优先修复。",
        "en": "There are ATS-level extraction or layout risks that should be fixed first.",
    },
    "Experience bullets are not yet giving enough timeline or ownership signal.": {
        "zh": "经历要点还没有提供足够的时间线或负责范围信号。",
        "en": "Experience bullets are not yet giving enough timeline or ownership signal.",
    },
    "Several JD keywords are still absent, which can hurt searchability and recruiter skim speed.": {
        "zh": "仍有多项 JD 关键词缺失，这会影响搜索命中和招聘方快速扫读。",
        "en": "Several JD keywords are still absent, which can hurt searchability and recruiter skim speed.",
    },
    "Fix ATS-blocking layout issues before doing any wording optimization.": {
        "zh": "在做措辞优化之前，先修复会阻碍 ATS 的排版问题。",
        "en": "Fix ATS-blocking layout issues before doing any wording optimization.",
    },
    "Rewrite experience bullets so they directly answer more of the JD must-have lines.": {
        "zh": "重写经历要点，让它们更直接地回答 JD 的必选要求。",
        "en": "Rewrite experience bullets so they directly answer more of the JD must-have lines.",
    },
    "Rewrite experience bullets with stronger metrics, scope, and outcomes.": {
        "zh": "重写经历要点，补强指标、范围和结果表达。",
        "en": "Rewrite experience bullets with stronger metrics, scope, and outcomes.",
    },
    "Strengthen timeline and ownership signals by showing dates, role scope, and action-led bullets.": {
        "zh": "通过日期、职责范围和动作导向要点来强化时间线与责任范围信号。",
        "en": "Strengthen timeline and ownership signals by showing dates, role scope, and action-led bullets.",
    },
    "The resume is already structurally strong. Focus next on section-level wording refinement.": {
        "zh": "简历结构已经比较稳，下一步重点放在各 section 的措辞打磨。",
        "en": "The resume is already structurally strong. Focus next on section-level wording refinement.",
    },
    "No major deterministic risk cluster was detected.": {
        "zh": "目前没有发现明显的确定性高风险簇。",
        "en": "No major deterministic risk cluster was detected.",
    },
    "A few baseline signals are present, so the resume can be improved without a full rewrite.": {
        "zh": "已经具备一些基础信号，因此这份简历更适合优化而不是完全重写。",
        "en": "A few baseline signals are present, so the resume can be improved without a full rewrite.",
    },
    "Measures layout safety, extractability, and core resume structure.": {
        "zh": "衡量排版安全性、文本可提取性和简历核心结构。",
        "en": "Measures layout safety, extractability, and core resume structure.",
    },
    "Rewards resumes that show measurable outcomes with numbers, percentages, or scale.": {
        "zh": "奖励使用数字、百分比或规模来体现结果的简历。",
        "en": "Rewards resumes that show measurable outcomes with numbers, percentages, or scale.",
    },
    "Rewards resumes that present timeline, action verbs, and experience/project evidence in a recruiter-friendly way.": {
        "zh": "奖励能以招聘方易读方式呈现时间线、动作词和经历/项目证据的简历。",
        "en": "Rewards resumes that present timeline, action verbs, and experience/project evidence in a recruiter-friendly way.",
    },
    "Resume length is 1 pages. Keeping it within 1-2 pages is usually safer.": {
        "zh": "简历当前为 1 页，控制在 1-2 页通常更安全。",
        "en": "Resume length is 1 pages. Keeping it within 1-2 pages is usually safer.",
    },
    "Table-based layout was detected. Many ATS parsers lose ordering or drop table content.": {
        "zh": "检测到表格排版。很多 ATS 在解析表格时会丢失顺序或内容。",
        "en": "Table-based layout was detected. Many ATS parsers lose ordering or drop table content.",
    },
    "Images or icons were detected. ATS systems often ignore visual content.": {
        "zh": "检测到图片或图标。ATS 往往会忽略这类视觉内容。",
        "en": "Images or icons were detected. ATS systems often ignore visual content.",
    },
    "Text extraction quality looks weak. The file may contain scan-only pages or layout issues.": {
        "zh": "文本提取质量偏弱，文件可能包含扫描页或复杂排版问题。",
        "en": "Text extraction quality looks weak. The file may contain scan-only pages or layout issues.",
    },
    "Some pages extracted less cleanly than others. Multi-column or complex layout may be involved.": {
        "zh": "部分页面提取不够干净，可能涉及多栏或复杂布局。",
        "en": "Some pages extracted less cleanly than others. Multi-column or complex layout may be involved.",
    },
    "Resume content looks short. Important context may be missing for ATS or recruiter review.": {
        "zh": "简历内容偏短，可能缺少 ATS 或招聘方需要的重要上下文。",
        "en": "Resume content looks short. Important context may be missing for ATS or recruiter review.",
    },
    "The resume has very few bullet points. Achievement-oriented bullets usually improve readability.": {
        "zh": "简历中的 bullet 较少。结果导向的 bullet 通常更利于阅读。",
        "en": "The resume has very few bullet points. Achievement-oriented bullets usually improve readability.",
    },
    "Email was not reliably detected. Recruiters and ATS exports need clear contact information.": {
        "zh": "没有可靠识别到邮箱。招聘方和 ATS 导出都需要清晰的联系方式。",
        "en": "Email was not reliably detected. Recruiters and ATS exports need clear contact information.",
    },
    "Phone number was not reliably detected. Add a clean phone line near the top of the resume.": {
        "zh": "没有可靠识别到手机号。建议在简历顶部单独列出清晰的电话信息。",
        "en": "Phone number was not reliably detected. Add a clean phone line near the top of the resume.",
    },
    "The resume structure looks sparse. Clear section boundaries improve both ATS parsing and human scanning.": {
        "zh": "简历结构偏稀疏。更清晰的 section 边界有助于 ATS 和人工浏览。",
        "en": "The resume structure looks sparse. Clear section boundaries improve both ATS parsing and human scanning.",
    },
    "Very few date ranges were detected. Recruiters usually expect visible timeline signals for experience and education.": {
        "zh": "检测到的时间区间很少。招聘方通常希望在经历和教育中看到清晰的时间线信号。",
        "en": "Very few date ranges were detected. Recruiters usually expect visible timeline signals for experience and education.",
    },
    "Experience bullets look light on action verbs. Rewrite bullets to show ownership, actions, and outcomes more clearly.": {
        "zh": "经历 bullet 的动作词偏弱。建议重写为更清晰的责任范围、动作和结果表达。",
        "en": "Experience bullets look light on action verbs. Rewrite bullets to show ownership, actions, and outcomes more clearly.",
    },
    "Education section is missing or not clearly labeled.": {
        "zh": "缺少教育部分，或教育标题不够清晰。",
        "en": "Education section is missing or not clearly labeled.",
    },
    "Work experience or internship section is missing or not clearly labeled.": {
        "zh": "缺少工作/实习经历部分，或标题不够清晰。",
        "en": "Work experience or internship section is missing or not clearly labeled.",
    },
    "Skills section is missing or not clearly labeled.": {
        "zh": "缺少技能部分，或技能标题不够清晰。",
        "en": "Skills section is missing or not clearly labeled.",
    },
    "No major ATS compatibility issues were detected by the deterministic rule engine.": {
        "zh": "确定性规则引擎没有发现明显的 ATS 兼容性问题。",
        "en": "No major ATS compatibility issues were detected by the deterministic rule engine.",
    },
    "Parsed the uploaded resume, extracted text, and segmented sections.": {
        "zh": "解析上传的简历，提取文本并切分结构部分。",
        "en": "Parsed the uploaded resume, extracted text, and segmented sections.",
    },
    "Structured the JD into role, skills, requirements, and keywords.": {
        "zh": "把 JD 结构化为岗位、技能、要求和关键词。",
        "en": "Structured the JD into role, skills, requirements, and keywords.",
    },
    "Checked layout safety, extractability, timeline cues, and contact completeness.": {
        "zh": "检查排版安全性、文本可提取性、时间线线索和联系方式完整性。",
        "en": "Checked layout safety, extractability, timeline cues, and contact completeness.",
    },
    "Cross-checked hard skills, must-have lines, quantified outcomes, and experience signals.": {
        "zh": "交叉核对硬技能、必选要求、量化成果和经历信号。",
        "en": "Cross-checked hard skills, must-have lines, quantified outcomes, and experience signals.",
    },
    "Built requirement-level evidence cards so the result can be reviewed against specific JD lines.": {
        "zh": "生成要求级证据卡片，让结果可以逐条对照 JD 复核。",
        "en": "Built requirement-level evidence cards so the result can be reviewed against specific JD lines.",
    },
    "Resume extraction quality looks stable enough for deterministic review.": {
        "zh": "简历文本提取质量足够稳定，适合进行确定性审核。",
        "en": "Resume extraction quality looks stable enough for deterministic review.",
    },
    "JD contains enough structured requirements to support a meaningful comparison.": {
        "zh": "JD 含有足够多的结构化要求，能支持较有意义的对比。",
        "en": "JD contains enough structured requirements to support a meaningful comparison.",
    },
    "Several matched hard skills only appear in skills or certification sections, not in experience or project evidence.": {
        "zh": "有几项已匹配的硬技能只出现在技能或证书区，还没有在经历或项目证据里真正立住。",
        "en": "Several matched hard skills only appear in skills or certification sections, not in experience or project evidence.",
    },
    "Several matched hard skills are also backed by experience or project context, but some still rely on shallow skill-list evidence.": {
        "zh": "有些已匹配硬技能已经有经历或项目场景支撑，但仍有一部分主要停留在技能清单层面，证据深度还不够。",
        "en": "Several matched hard skills are also backed by experience or project context, but some still rely on shallow skill-list evidence.",
    },
    "Some matched skills are currently easy to question in interviews because they are listed, but not strongly proven in dated experience.": {
        "zh": "有些技能现在更像是“列出来了”，但还没有在带时间线的真实经历里被强力证明，面试里很容易被追问。",
        "en": "Some matched skills are currently easy to question in interviews because they are listed, but not strongly proven in dated experience.",
    },
    "Move at least one matched hard skill from the skills list into a dated experience or project bullet with scope and outcome context.": {
        "zh": "至少把一项已匹配硬技能从技能清单迁移到带日期的经历或项目 bullet 中，并补上范围与结果语境。",
        "en": "Move at least one matched hard skill from the skills list into a dated experience or project bullet with scope and outcome context.",
    },
    "Deep review found enough experience-context evidence behind the matched skills to support a more confident judgment.": {
        "zh": "深度复核发现，这些已匹配技能背后已经有足够多的经历场景证据，可以支撑更高可信度的判断。",
        "en": "Deep review found enough experience-context evidence behind the matched skills to support a more confident judgment.",
    },
    "Some JD evidence currently comes from skills-list mentions instead of experience bullets, which weakens credibility in interviews.": {
        "zh": "有些 JD 证据目前主要来自技能清单，而不是经历 bullet，这会削弱面试里的可信度。",
        "en": "Some JD evidence currently comes from skills-list mentions instead of experience bullets, which weakens credibility in interviews.",
    },
    "For high-priority JD requirements, add bullets that show action, context, and business outcome instead of tool names alone.": {
        "zh": "针对高优先级 JD 要求，补上能够体现动作、场景和业务结果的 bullet，而不是只列工具名。",
        "en": "For high-priority JD requirements, add bullets that show action, context, and business outcome instead of tool names alone.",
    },
    "Some ATS extraction or layout risks reduce the confidence of automated judgment.": {
        "zh": "存在 ATS 提取或排版风险，会降低自动判断的可信度。",
        "en": "Some ATS extraction or layout risks reduce the confidence of automated judgment.",
    },
    "The JD is short or weakly structured, so the comparison has less evidence than ideal.": {
        "zh": "JD 偏短或结构较弱，因此本次对比证据少于理想状态。",
        "en": "The JD is short or weakly structured, so the comparison has less evidence than ideal.",
    },
    "Resume sectioning is sparse, which weakens section-level interpretation.": {
        "zh": "简历 section 划分偏弱，会削弱分段级别的解释能力。",
        "en": "Resume sectioning is sparse, which weakens section-level interpretation.",
    },
    "Keep the evidence but make the accomplishment more specific with scope or metrics.": {
        "zh": "保留这条证据，但建议用范围、指标或结果把表达再写具体一些。",
        "en": "Keep the evidence but make the accomplishment more specific with scope or metrics.",
    },
    "Add a resume bullet that directly proves this JD requirement with a real project, task, or result.": {
        "zh": "补上一条能直接证明该 JD 要求的简历 bullet，用真实项目、任务或结果来支撑。",
        "en": "Add a resume bullet that directly proves this JD requirement with a real project, task, or result.",
    },
    "This interview pack prioritizes the questions most likely to surface based on your current resume evidence, visible gaps, and JD requirements.": {
        "zh": "这组面试问题优先覆盖最可能出现的追问，依据是你当前的简历证据、显性缺口和 JD 要求。",
        "en": "This interview pack prioritizes the questions most likely to surface based on your current resume evidence, visible gaps, and JD requirements.",
    },
    "Practice answering these in spoken language, not written language. Keep each answer concrete, role-specific, and outcome-oriented.": {
        "zh": "练习时请按口语表达来回答，而不是书面腔。每个回答都要具体、贴岗，并且落到结果。",
        "en": "Practice answering these in spoken language, not written language. Keep each answer concrete, role-specific, and outcome-oriented.",
    },
    "Give me a 60-second introduction tailored to this role.": {
        "zh": "请用 60 秒做一个贴合这个岗位的自我介绍。",
        "en": "Give me a 60-second introduction tailored to this role.",
    },
    "Interviewers use this to judge role fit, communication clarity, and whether your story matches the JD from the first minute.": {
        "zh": "面试官会用这个问题快速判断你的岗位匹配度、表达清晰度，以及你的经历故事是否从一开始就对齐 JD。",
        "en": "Interviewers use this to judge role fit, communication clarity, and whether your story matches the JD from the first minute.",
    },
    "Who you are right now": {"zh": "你现在是谁、在找什么方向", "en": "Who you are right now"},
    "Which past experiences map most directly to the target role": {"zh": "过去哪些经历最直接对应这个岗位", "en": "Which past experiences map most directly to the target role"},
    "One concrete result with numbers or business impact": {"zh": "至少给出一个带数字或业务结果的例子", "en": "One concrete result with numbers or business impact"},
    "Pick the project or experience on your resume that best matches this JD and walk me through it end to end.": {
        "zh": "从你的简历里挑一个最贴合这个 JD 的项目或经历，从头到尾讲一遍。",
        "en": "Pick the project or experience on your resume that best matches this JD and walk me through it end to end.",
    },
    "This checks whether the strongest line on the resume is real, well understood, and relevant to the hiring need.": {
        "zh": "这题用来验证你简历上最强的一条经历是否真实、是否讲得清、是否真的贴合招聘需求。",
        "en": "This checks whether the strongest line on the resume is real, well understood, and relevant to the hiring need.",
    },
    "Situation and business context": {"zh": "背景和业务场景", "en": "Situation and business context"},
    "Your exact role and ownership": {"zh": "你的具体职责和负责边界", "en": "Your exact role and ownership"},
    "Actions, trade-offs, and final outcome": {"zh": "你的动作、取舍和最终结果", "en": "Actions, trade-offs, and final outcome"},
    "Your resume does not show strong SQL evidence yet. Tell me about the most complex SQL analysis you have actually done.": {
        "zh": "你的简历里还没有体现出足够强的 SQL 证据。讲讲你实际做过的最复杂的一次 SQL 分析。",
        "en": "Your resume does not show strong SQL evidence yet. Tell me about the most complex SQL analysis you have actually done.",
    },
    "A visible skill gap on the resume often turns into a direct verification question in the interview.": {
        "zh": "简历里显眼的技能缺口，往往会在面试里变成直接核验题。",
        "en": "A visible skill gap on the resume often turns into a direct verification question in the interview.",
    },
    "Business problem behind the query": {"zh": "这条查询背后的业务问题是什么", "en": "Business problem behind the query"},
    "Joins, aggregations, or window functions you used": {"zh": "你实际用了哪些连接、聚合或窗口函数", "en": "Joins, aggregations, or window functions you used"},
    "What decision or result the analysis enabled": {"zh": "这次分析最后支撑了什么决策或结果", "en": "What decision or result the analysis enabled"},
    "Interviewers often convert a visible requirement gap into a direct proof question.": {
        "zh": "面试官经常会把简历里可见的要求缺口，直接变成一条现场核验题。",
        "en": "Interviewers often convert a visible requirement gap into a direct proof question.",
    },
    "What the task or business goal actually was": {"zh": "当时真实的任务或业务目标是什么", "en": "What the task or business goal actually was"},
    "What you personally owned and executed": {"zh": "你个人具体负责并执行了什么", "en": "What you personally owned and executed"},
    "What outcome, metric, or learning came out of it": {"zh": "最后产出了什么结果、指标变化或关键复盘", "en": "What outcome, metric, or learning came out of it"},
    "Tell me about a time you used Excel or analysis tooling to turn messy data into a clear decision.": {
        "zh": "讲一个你用 Excel 或分析工具把脏乱数据变成清晰决策依据的例子。",
        "en": "Tell me about a time you used Excel or analysis tooling to turn messy data into a clear decision.",
    },
    "Interviewers want proof that your tool usage connects to business judgment, not just mechanical操作.": {
        "zh": "面试官想确认你会用工具，但更重要的是这些工具是否真的服务了业务判断，而不是机械操作。",
        "en": "Interviewers want proof that your tool usage connects to business judgment, not just mechanical操作.",
    },
    "How the data was messy or incomplete": {"zh": "数据一开始为什么脏、乱或不完整", "en": "How the data was messy or incomplete"},
    "What framework or analysis steps you used": {"zh": "你用了什么分析框架或步骤", "en": "What framework or analysis steps you used"},
    "What recommendation or operational action followed": {"zh": "最后给出了什么建议或推动了什么动作", "en": "What recommendation or operational action followed"},
    "Walk me through a supplier delay, shortage, or planning exception you handled. How did you diagnose it and protect delivery?": {
        "zh": "讲一个你处理供应商延期、缺料或计划异常的例子。你是怎么定位问题并保住交付的？",
        "en": "Walk me through a supplier delay, shortage, or planning exception you handled. How did you diagnose it and protect delivery?",
    },
    "Operations and supply chain interviews frequently test whether you can stabilize execution under pressure, not just describe routine work.": {
        "zh": "运营和供应链岗位经常会考你能不能在压力下稳住执行，而不只是复述日常工作流程。",
        "en": "Operations and supply chain interviews frequently test whether you can stabilize execution under pressure, not just describe routine work.",
    },
    "What signal told you the plan was breaking": {"zh": "最先让你意识到计划开始失控的信号是什么", "en": "What signal told you the plan was breaking"},
    "How you coordinated suppliers, internal teams, or data inputs": {"zh": "你是怎么协调供应商、内部团队或相关数据输入的", "en": "How you coordinated suppliers, internal teams, or data inputs"},
    "What trade-off you made on cost, service level, or lead time": {"zh": "你在成本、服务水平或交期之间做了什么取舍", "en": "What trade-off you made on cost, service level, or lead time"},
    "Pick one metric or dashboard you used regularly. How was it defined, where did the data come from, and what decision did it support?": {
        "zh": "挑一个你经常使用的指标或看板。它是怎么定义的、数据从哪里来、最后支撑了什么决策？",
        "en": "Pick one metric or dashboard you used regularly. How was it defined, where did the data come from, and what decision did it support?",
    },
    "Analyst interviews often check whether you understand the business meaning and trust boundaries behind the numbers, not just the final chart.": {
        "zh": "分析岗面试常常会追问你是否真的理解数字背后的业务含义和可信边界，而不只是会展示最后那张图。",
        "en": "Analyst interviews often check whether you understand the business meaning and trust boundaries behind the numbers, not just the final chart.",
    },
    "How the metric was defined": {"zh": "这个指标当时是怎么定义的", "en": "How the metric was defined"},
    "What source tables, files, or systems fed it": {"zh": "它依赖了哪些表、文件或业务系统", "en": "What source tables, files, or systems fed it"},
    "How the metric changed a business decision": {"zh": "这个指标最终是怎么影响业务决策的", "en": "How the metric changed a business decision"},
    "Tell me about a time you had to balance cost, timeliness, and operational feasibility in a supply chain or procurement task.": {
        "zh": "讲一个你在供应链或采购任务里同时平衡成本、时效和落地可行性的例子。",
        "en": "Tell me about a time you had to balance cost, timeliness, and operational feasibility in a supply chain or procurement task.",
    },
    "Supply chain interviews often test whether you can reason through trade-offs instead of optimizing only one metric.": {
        "zh": "供应链岗位很常考取舍能力，而不是只会把某一个指标做到最好。",
        "en": "Supply chain interviews often test whether you can reason through trade-offs instead of optimizing only one metric.",
    },
    "The competing goals or constraints": {"zh": "当时互相冲突的目标或约束是什么", "en": "The competing goals or constraints"},
    "How you prioritized and aligned stakeholders": {"zh": "你是怎么排序优先级并对齐相关方的", "en": "How you prioritized and aligned stakeholders"},
    "What result you achieved and what you would improve next time": {"zh": "最后结果如何，以及下次你会怎么做得更好", "en": "What result you achieved and what you would improve next time"},
    "If a core business metric suddenly dropped this week, how would you structure the analysis and narrow down the cause?": {
        "zh": "如果一个核心业务指标这周突然下滑，你会怎么组织分析并逐步缩小原因范围？",
        "en": "If a core business metric suddenly dropped this week, how would you structure the analysis and narrow down the cause?",
    },
    "Data and analytical roles are frequently tested on structured problem decomposition under ambiguity.": {
        "zh": "数据和分析岗位经常会考你在信息不完整时，能不能有结构地拆解问题。",
        "en": "Data and analytical roles are frequently tested on structured problem decomposition under ambiguity.",
    },
    "How you define and segment the metric": {"zh": "你会如何先定义并拆分这个指标", "en": "How you define and segment the metric"},
    "How you separate data quality from real business change": {"zh": "你怎么区分是数据异常还是业务真的变了", "en": "How you separate data quality from real business change"},
    "What hypotheses you would test first": {"zh": "你最先会验证哪些假设", "en": "What hypotheses you would test first"},
    "Describe a cross-functional disagreement and how you got alignment without losing execution speed.": {
        "zh": "讲一个跨部门分歧的例子，以及你如何在不拖慢执行的情况下把大家拉到一致。",
        "en": "Describe a cross-functional disagreement and how you got alignment without losing execution speed.",
    },
    "Hiring teams use this to test collaboration maturity, stakeholder handling, and execution discipline.": {
        "zh": "这题用来判断你的协作成熟度、相关方处理能力和执行纪律。",
        "en": "Hiring teams use this to test collaboration maturity, stakeholder handling, and execution discipline.",
    },
    "What each side cared about": {"zh": "各方分别在意什么", "en": "What each side cared about"},
    "How you reframed the problem with evidence": {"zh": "你如何用证据重构问题定义", "en": "How you reframed the problem with evidence"},
    "What agreement or next step you secured": {"zh": "你最后拿到了什么共识或下一步动作", "en": "What agreement or next step you secured"},
    "Tell me about a time you had incomplete information but still needed to make a recommendation.": {
        "zh": "讲一个信息不完整但你仍然需要给出建议或决策的例子。",
        "en": "Tell me about a time you had incomplete information but still needed to make a recommendation.",
    },
    "Real jobs rarely provide perfect data, so interviewers look for judgment under uncertainty.": {
        "zh": "真实工作里很少有完美数据，所以面试官会专门看你在不确定性下的判断力。",
        "en": "Real jobs rarely provide perfect data, so interviewers look for judgment under uncertainty.",
    },
    "What was unknown or ambiguous": {"zh": "当时有哪些信息是未知或模糊的", "en": "What was unknown or ambiguous"},
    "What assumptions you made and how you managed risk": {"zh": "你做了哪些假设，以及怎么控制风险", "en": "What assumptions you made and how you managed risk"},
    "What happened after your recommendation": {"zh": "你的建议之后发生了什么", "en": "What happened after your recommendation"},
    "Why this role, and why are you a better fit for this role now than six months ago?": {
        "zh": "为什么是这个岗位？为什么你现在比半年前更适合这个岗位？",
        "en": "Why this role, and why are you a better fit for this role now than six months ago?",
    },
    "This helps interviewers see self-awareness, motivation, and whether your trajectory is becoming more aligned with the role.": {
        "zh": "这题帮助面试官看你的自我认知、动机是否真实，以及你的经历轨迹是否正在变得更贴岗。",
        "en": "This helps interviewers see self-awareness, motivation, and whether your trajectory is becoming more aligned with the role.",
    },
    "Why this role fits your current direction": {"zh": "为什么这个岗位符合你当前方向", "en": "Why this role fits your current direction"},
    "What has changed in your experience recently": {"zh": "最近哪些经历让你变得更匹配", "en": "What has changed in your experience recently"},
    "What specific value you can create early": {"zh": "你入职后最早能创造什么具体价值", "en": "What specific value you can create early"},
}

_DYNAMIC_PATTERNS = [
    (
        re.compile(r"The biggest professional gap is still the proof depth for (.+)\."),
        lambda match, lang: (
            f"当前最大的专业缺口仍然是这些能力的证明深度：{match.group(1)}。"
            if lang == "zh"
            else f"The biggest professional gap is still the proof depth for {match.group(1)}."
        ),
    ),
    (
        re.compile(r"Prepare a truthful spoken example for (.+), because the interview is likely to probe it\."),
        lambda match, lang: (
            f"提前准备好关于 {match.group(1)} 的真实口头例子，因为面试大概率会继续追问。"
            if lang == "zh"
            else f"Prepare a truthful spoken example for {match.group(1)}, because the interview is likely to probe it."
        ),
    ),
    (
        re.compile(r"(\d+) must-have JD lines still do not have direct resume proof\."),
        lambda match, lang: (
            f"仍有 {match.group(1)} 条 JD 必选要求缺少直接的简历证明。"
            if lang == "zh"
            else f"{match.group(1)} must-have JD lines still do not have direct resume proof."
        ),
    ),
    (
        re.compile(r"Core hard-skill proof is still missing for: (.+)\."),
        lambda match, lang: (
            f"这些核心硬技能的证明仍然不够：{match.group(1)}。"
            if lang == "zh"
            else f"Core hard-skill proof is still missing for: {match.group(1)}."
        ),
    ),
    (
        re.compile(r"Improve natural keyword alignment for: (.+)\."),
        lambda match, lang: (
            f"可以继续补强这些关键词的自然对齐：{match.group(1)}。"
            if lang == "zh"
            else f"Improve natural keyword alignment for: {match.group(1)}."
        ),
    ),
    (
        re.compile(r"The interview is likely to challenge your proof depth for (.+)\."),
        lambda match, lang: (
            f"面试更可能追问你在 {match.group(1)} 上的真实证明深度。"
            if lang == "zh"
            else f"The interview is likely to challenge your proof depth for {match.group(1)}."
        ),
    ),
    (
        re.compile(r"Collected (\d+) public sources about role expectations, interview experience, and skill requirements\."),
        lambda match, lang: (
            f"补充收集了 {match.group(1)} 个公开来源，用来辅助理解岗位预期、面经风格和技能要求。"
            if lang == "zh"
            else f"Collected {match.group(1)} public sources about role expectations, interview experience, and skill requirements."
        ),
    ),
    (
        re.compile(r"Public research looked at open web sources around the target role: (.+)\."),
        lambda match, lang: (
            f"公开资料补充围绕目标岗位 {match.group(1)} 搜集了相关开放网页来源。"
            if lang == "zh"
            else f"Public research looked at open web sources around the target role: {match.group(1)}."
        ),
    ),
    (
        re.compile(r"(\d+) public sources look like interview-experience or interview-question references\."),
        lambda match, lang: (
            f"其中有 {match.group(1)} 个公开来源更像面经或面试题参考。"
            if lang == "zh"
            else f"{match.group(1)} public sources look like interview-experience or interview-question references."
        ),
    ),
    (
        re.compile(r"(\d+) public sources come from community discussions, which are useful for patterns but still need judgment\."),
        lambda match, lang: (
            f"其中有 {match.group(1)} 个来源来自社区讨论，适合看模式，但仍需要你自己判断。"
            if lang == "zh"
            else f"{match.group(1)} public sources come from community discussions, which are useful for patterns but still need judgment."
        ),
    ),
    (
        re.compile(r"Repeated public signals mention: (.+)\."),
        lambda match, lang: (
            f"多份公开资料里重复出现的技能或主题包括：{match.group(1)}。"
            if lang == "zh"
            else f"Repeated public signals mention: {match.group(1)}."
        ),
    ),
    (
        re.compile(r"Public research was enabled, but web search is unavailable in the current environment\."),
        lambda _match, lang: (
            "已开启公开资料补充，但当前环境暂时无法执行网页搜索。"
            if lang == "zh"
            else "Public research was enabled, but web search is unavailable in the current environment."
        ),
    ),
    (
        re.compile(r"Public research was enabled, but the current environment could not fetch public results\."),
        lambda _match, lang: (
            "已开启公开资料补充，但当前环境暂时无法拉取公开搜索结果。"
            if lang == "zh"
            else "Public research was enabled, but the current environment could not fetch public results."
        ),
    ),
    (
        re.compile(r"Public research was enabled, but no usable public sources were returned\."),
        lambda _match, lang: (
            "已开启公开资料补充，但这次没有拿到可用的公开来源。"
            if lang == "zh"
            else "Public research was enabled, but no usable public sources were returned."
        ),
    ),
    (
        re.compile(r"Hard-skill evidence was detected for (.+)\."),
        lambda match, lang: (
            f"已检测到这些硬技能证据：{match.group(1)}。"
            if lang == "zh"
            else f"Hard-skill evidence was detected for {match.group(1)}."
        ),
    ),
    (
        re.compile(r"Missing hard-skill evidence: (.+)\."),
        lambda match, lang: (
            f"这些硬技能还缺少明确证据：{match.group(1)}。"
            if lang == "zh"
            else f"Missing hard-skill evidence: {match.group(1)}."
        ),
    ),
    (
        re.compile(r"(\d+) must-have JD lines still lack direct resume evidence\."),
        lambda match, lang: (
            f"仍有 {match.group(1)} 条 JD 必选要求缺少直接简历证据。"
            if lang == "zh"
            else f"{match.group(1)} must-have JD lines still lack direct resume evidence."
        ),
    ),
    (
        re.compile(r"Detected (\d+) numeric signals across the resume\."),
        lambda match, lang: (
            f"简历中共检测到 {match.group(1)} 处数字化信号。"
            if lang == "zh"
            else f"Detected {match.group(1)} numeric signals across the resume."
        ),
    ),
    (
        re.compile(r"Detected (\d+) timeline markers and (\d+) action verbs\."),
        lambda match, lang: (
            f"检测到 {match.group(1)} 处时间线标记和 {match.group(2)} 个动作词。"
            if lang == "zh"
            else f"Detected {match.group(1)} timeline markers and {match.group(2)} action verbs."
        ),
    ),
    (
        re.compile(r"Matched (\d+) structured hard skills and (\d+) tracked keywords\."),
        lambda match, lang: (
            f"匹配到 {match.group(1)} 个结构化硬技能和 {match.group(2)} 个跟踪关键词。"
            if lang == "zh"
            else f"Matched {match.group(1)} structured hard skills and {match.group(2)} tracked keywords."
        ),
    ),
    (
        re.compile(r"At least (\d+) must-have JD lines show direct evidence in the resume\."),
        lambda match, lang: (
            f"至少有 {match.group(1)} 条 JD 必选要求在简历中有直接证据。"
            if lang == "zh"
            else f"At least {match.group(1)} must-have JD lines show direct evidence in the resume."
        ),
    ),
    (
        re.compile(r"Add evidence-backed coverage for the missing hard skills: (.+)\."),
        lambda match, lang: (
            f"补上这些缺失硬技能的真实经历证据：{match.group(1)}。"
            if lang == "zh"
            else f"Add evidence-backed coverage for the missing hard skills: {match.group(1)}."
        ),
    ),
    (
        re.compile(r"Improve keyword alignment for: (.+)\."),
        lambda match, lang: (
            f"补强这些关键词的自然对齐：{match.group(1)}。"
            if lang == "zh"
            else f"Improve keyword alignment for: {match.group(1)}."
        ),
    ),
    (
        re.compile(r"Matched (\d+) of (\d+) structured hard skills\."),
        lambda match, lang: (
            f"在 {match.group(2)} 个结构化硬技能中匹配到 {match.group(1)} 个。"
            if lang == "zh"
            else f"Matched {match.group(1)} of {match.group(2)} structured hard skills."
        ),
    ),
    (
        re.compile(r"Matched (\d+) of (\d+) structured soft skills\."),
        lambda match, lang: (
            f"在 {match.group(2)} 个结构化软技能中匹配到 {match.group(1)} 个。"
            if lang == "zh"
            else f"Matched {match.group(1)} of {match.group(2)} structured soft skills."
        ),
    ),
    (
        re.compile(r"Matched (\d+) of (\d+) tracked JD keywords\."),
        lambda match, lang: (
            f"在 {match.group(2)} 个跟踪关键词中匹配到 {match.group(1)} 个。"
            if lang == "zh"
            else f"Matched {match.group(1)} of {match.group(2)} tracked JD keywords."
        ),
    ),
    (
        re.compile(r"Covered (\d+) of (\d+) must-have requirement lines\."),
        lambda match, lang: (
            f"在 {match.group(2)} 条必选要求中覆盖了 {match.group(1)} 条。"
            if lang == "zh"
            else f"Covered {match.group(1)} of {match.group(2)} must-have requirement lines."
        ),
    ),
    (
        re.compile(r"Requirement-level evidence was found for (\d+) of (\d+) must-have JD lines\."),
        lambda match, lang: (
            f"在 {match.group(2)} 条 JD 必选要求中，有 {match.group(1)} 条找到了要求级证据。"
            if lang == "zh"
            else f"Requirement-level evidence was found for {match.group(1)} of {match.group(2)} must-have JD lines."
        ),
    ),
    (
        re.compile(r"The JD emphasizes (.+)\. Tell me about the strongest example in your experience that proves it\."),
        lambda match, lang: (
            f"JD 特别强调 {match.group(1)}。请讲一个你经历里最能证明这项要求的例子。"
            if lang == "zh"
            else f"The JD emphasizes {match.group(1)}. Tell me about the strongest example in your experience that proves it."
        ),
    ),
    (
        re.compile(r"Why this role, and why are you a better fit for (.+) now than six months ago\?"),
        lambda match, lang: (
            f"为什么是这个岗位？为什么你现在比半年前更适合 {match.group(1)}？"
            if lang == "zh"
            else f"Why this role, and why are you a better fit for {match.group(1)} now than six months ago?"
        ),
    ),
    (
        re.compile(
            r"Deep review checked whether matched skills are backed by experience-context evidence and whether "
            r"JD evidence comes from real experience instead of only skill lists\. "
            r"Found (\d+) skills with experience evidence and (\d+) skills that still look list-only\."
        ),
        lambda match, lang: (
            f"深度复核检查了已匹配技能是否真的落在经历场景里，而不是只停留在技能清单。"
            f"本次发现有 {match.group(1)} 项技能具备经历证据，另有 {match.group(2)} 项技能目前仍更像清单式陈列。"
            if lang == "zh"
            else (
                "Deep review checked whether matched skills are backed by experience-context evidence and whether "
                "JD evidence comes from real experience instead of only skill lists. "
                f"Found {match.group(1)} skills with experience evidence and {match.group(2)} skills that still look list-only."
            )
        ),
    ),
    (
        re.compile(
            r"Built requirement-level evidence cards so the result can be reviewed against specific JD lines\. "
            r"Reviewed (\d+) must-have lines and found evidence for (\d+)\. Current confidence is (.+)\."
        ),
        lambda match, lang: (
            f"生成要求级证据卡片以便逐条对照 JD 复核。共审查 {match.group(1)} 条必选要求，"
            f"其中 {match.group(2)} 条找到了证据，当前判断为{translate_dynamic(match.group(3), 'zh')}。"
            if lang == "zh"
            else (
                f"Built requirement-level evidence cards so the result can be reviewed against specific JD lines. "
                f"Reviewed {match.group(1)} must-have lines and found evidence for {match.group(2)}. "
                f"Current confidence is {match.group(3)}."
            )
        ),
    ),
    (
        re.compile(
            r"Overall match is (.+)\. ATS readiness is (\d+)/100, (\d+) hard skills were matched, (\d+) remain uncovered, and (\d+)/(\d+) must-have JD lines were covered\."
        ),
        lambda match, lang: (
            f"整体判断为{translate_dynamic(match.group(1), 'zh')}。ATS 兼容度为 {match.group(2)}/100，"
            f"已匹配 {match.group(3)} 个硬技能，仍缺失 {match.group(4)} 个，"
            f"JD 必选要求覆盖 {match.group(5)}/{match.group(6)}。"
            if lang == "zh"
            else (
                f"Overall match is {match.group(1)}. ATS readiness is {match.group(2)}/100, "
                f"{match.group(3)} hard skills were matched, {match.group(4)} remain uncovered, "
                f"and {match.group(5)}/{match.group(6)} must-have JD lines were covered."
            )
        ),
    ),
]


def resolve_lang(raw_lang: str | None) -> str:
    return raw_lang if raw_lang in SUPPORTED_LANGS else "zh"


def get_ui(lang: str) -> dict[str, str]:
    return UI_TRANSLATIONS[resolve_lang(lang)]


def translate_stage_name(name: str, lang: str) -> str:
    resolved = resolve_lang(lang)
    if name in STAGE_TRANSLATIONS:
        return STAGE_TRANSLATIONS[name][resolved]
    return name.replace("_", " ").title()


def translate_dynamic(text: str, lang: str) -> str:
    resolved = resolve_lang(lang)
    if resolved == "en" or not text:
        return text

    exact = _DYNAMIC_EXACT.get(text)
    if exact:
        return exact[resolved]

    for pattern, builder in _DYNAMIC_PATTERNS:
        match = pattern.fullmatch(text)
        if match:
            return builder(match, resolved)

    return text
