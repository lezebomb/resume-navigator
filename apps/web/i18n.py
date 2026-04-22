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
        "analysis_mode_current": "当前模式",
        "standard_mode_label": "快速诊断",
        "deep_mode_label": "深度诊断",
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
        "analysis_mode_current": "Current mode",
        "standard_mode_label": "Quick audit",
        "deep_mode_label": "Deep audit",
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
}

_DYNAMIC_EXACT = {
    "Strong": {"zh": "强匹配", "en": "Strong"},
    "Promising": {"zh": "有潜力", "en": "Promising"},
    "Needs focus": {"zh": "需重点优化", "en": "Needs focus"},
    "Needs rebuild": {"zh": "需重构表达", "en": "Needs rebuild"},
    "High confidence": {"zh": "高可信", "en": "High confidence"},
    "Medium confidence": {"zh": "中等可信", "en": "Medium confidence"},
    "Needs manual review": {"zh": "需人工复核", "en": "Needs manual review"},
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
}

_DYNAMIC_PATTERNS = [
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
