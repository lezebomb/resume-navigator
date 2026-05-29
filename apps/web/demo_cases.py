from __future__ import annotations


def list_demo_cases(lang: str) -> list[dict]:
    cases = [
        {
            "slug": "supply-chain-proof-gap",
            "title": {
                "zh": "供应链方向：经历相关，但 JD 证明不够深",
                "en": "Supply chain: relevant background, but the JD proof is still shallow",
            },
            "target_role": {
                "zh": "供应链分析师 / 采购分析师",
                "en": "Supply Chain Analyst / Procurement Analyst",
            },
            "problem": {
                "zh": "简历里写了 Excel、供应链和采购，但很多内容还停留在“列出来”，没有变成能经得起追问的经历证明。",
                "en": "The resume mentions Excel, supply chain, and procurement, but too much of it is still listed instead of being proven through dated experience.",
            },
            "tool_output": {
                "zh": "工具会先告诉你：现在不是完全不能投，但招聘方大概率会继续追问这些技能到底做过多深。",
                "en": "The tool would first say: you may still apply, but the recruiter is likely to probe how deeply you have actually used these skills.",
            },
            "top_actions": {
                "zh": [
                    "把最接近 JD 的一段经历重写成“场景 + 你的动作 + 结果”",
                    "把技能栏里的 SQL 或分析能力迁移到真实经历 bullet 里",
                    "补一条能体现业务结果或效率提升的量化结果",
                ],
                "en": [
                    "Rewrite the most relevant experience into context, action, and result.",
                    "Move skills such as SQL or analysis from the skill list into real experience bullets.",
                    "Add one quantified result that shows business impact or efficiency gain.",
                ],
            },
            "interview_risk": {
                "zh": "面试大概率会问：你说自己会 SQL / 分析，那你真正做过的最复杂场景是什么？",
                "en": "A likely interview challenge is: you say you know SQL or analysis, so what is the deepest real scenario where you actually used it?",
            },
            "why_useful": {
                "zh": "这类情况非常常见，尤其出现在应届生、实习转正和转岗求职者身上。",
                "en": "This is a very common case, especially for early-career candidates, interns, and people changing direction.",
            },
        },
        {
            "slug": "analyst-keyword-but-no-proof",
            "title": {
                "zh": "数据分析方向：关键词不少，但招聘方还是不放心",
                "en": "Data analysis: plenty of keywords, but the recruiter still does not feel convinced",
            },
            "target_role": {
                "zh": "数据分析师 / 商业分析师",
                "en": "Data Analyst / Business Analyst",
            },
            "problem": {
                "zh": "简历里出现了 dashboard、metrics、analysis 等词，但没有把这些词和具体业务问题、数据逻辑、决策结果绑在一起。",
                "en": "The resume contains terms like dashboard, metrics, and analysis, but they are not tied tightly enough to a concrete business problem, data logic, and decision outcome.",
            },
            "tool_output": {
                "zh": "工具会先告诉你：关键词对齐不差，但真正影响面试表现的，是这些词背后有没有站得住的案例。",
                "en": "The tool would first say: keyword alignment is not the main issue here; the bigger issue is whether the stories behind those keywords can survive interview follow-up.",
            },
            "top_actions": {
                "zh": [
                    "挑一个你最熟的指标或报表，补上定义、数据来源和它支持了什么决策",
                    "把‘负责分析’改成你到底分析了什么问题、怎么做、最后怎么影响结果",
                    "准备一个 60 到 90 秒能讲清楚的案例，而不是只准备工具名",
                ],
                "en": [
                    "Pick one metric or dashboard and add its definition, data source, and supported decision.",
                    "Replace vague phrases like responsible for analysis with the problem, the method, and the outcome.",
                    "Prepare one 60- to 90-second case you can explain clearly instead of only naming tools.",
                ],
            },
            "interview_risk": {
                "zh": "面试大概率会问：这个指标你是怎么定义的、数据从哪里来、最后支持了什么业务动作？",
                "en": "A likely interview challenge is: how did you define that metric, where did the data come from, and what business action did it support?",
            },
            "why_useful": {
                "zh": "这类情况特别适合解释“为什么简历不是缺词，而是缺证明”。",
                "en": "This case is useful because it shows why the real problem is often missing proof rather than missing keywords.",
            },
        },
        {
            "slug": "operations-collaboration-sounds-generic",
            "title": {
                "zh": "运营/供应链协同：确实做过，但写法太泛",
                "en": "Operations or supply-chain collaboration: real experience, but written too vaguely",
            },
            "target_role": {
                "zh": "供应链运营 / 计划 / 采购协同",
                "en": "Supply chain operations / planning / procurement coordination",
            },
            "problem": {
                "zh": "简历里写了跨部门沟通、协调执行、推动项目，但没有写清冲突点、判断过程和最后结果，所以到面试很容易被继续追问。",
                "en": "The resume mentions cross-functional communication, coordination, and execution, but it does not explain the conflict, judgment, or final result, so interviews keep pushing deeper.",
            },
            "tool_output": {
                "zh": "工具会先告诉你：这类经历不是没价值，而是还没有被写成能体现判断力和推动力的证据。",
                "en": "The tool would first say: the experience itself has value, but it is not yet written as proof of judgment and execution.",
            },
            "top_actions": {
                "zh": [
                    "把一段“协调过什么”改成“为什么会出现冲突、你怎么推进、结果如何”",
                    "补上一个真实取舍，例如成本、时效、库存或交付之间你如何平衡",
                    "准备一个 90 秒内能讲清楚的协同案例，避免只说自己负责沟通",
                ],
                "en": [
                    "Turn one coordination bullet into a story of conflict, action, and result.",
                    "Add one real trade-off such as cost, speed, inventory, or delivery.",
                    "Prepare one collaboration case you can explain in under 90 seconds instead of only saying you communicated well.",
                ],
            },
            "interview_risk": {
                "zh": "高概率会被问：当采购、计划和业务目标冲突时，你具体怎么推动达成一致？",
                "en": "A likely challenge is: when procurement, planning, and business goals conflicted, how exactly did you drive alignment?",
            },
            "why_useful": {
                "zh": "很多求职者真正的短板不是没做过协同，而是协同经历没有写出判断、推进和结果。",
                "en": "Many candidates do have collaboration experience. The weaker part is failing to show judgment, momentum, and outcome.",
            },
        },
    ]

    resolved: list[dict] = []
    for case in cases:
        resolved.append(
            {
                "slug": case["slug"],
                "title": case["title"][lang],
                "target_role": case["target_role"][lang],
                "problem": case["problem"][lang],
                "tool_output": case["tool_output"][lang],
                "top_actions": case["top_actions"][lang],
                "interview_risk": case["interview_risk"][lang],
                "why_useful": case["why_useful"][lang],
            }
        )
    return resolved
