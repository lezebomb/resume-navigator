from __future__ import annotations


HARD_SKILL_TAXONOMY: dict[str, tuple[str, ...]] = {
    "python": ("python",),
    "sql": ("sql", "mysql", "postgresql", "sqlite", "sql server"),
    "excel": ("excel", "vlookup", "pivot table", "power query", "数据透视表"),
    "power_bi": ("power bi",),
    "tableau": ("tableau",),
    "pandas": ("pandas",),
    "numpy": ("numpy",),
    "machine_learning": ("machine learning", "机器学习"),
    "statistics": ("statistics", "statistical analysis", "统计分析"),
    "financial_modeling": ("financial modeling", "估值模型", "财务建模", "dcf"),
    "sap": ("sap",),
    "oracle": ("oracle",),
    "erp": ("erp",),
    "jira": ("jira",),
    "figma": ("figma",),
    "axure": ("axure",),
    "photoshop": ("photoshop", "ps"),
    "seo": ("seo",),
    "sem": ("sem",),
    "crm": ("crm", "salesforce", "hubspot"),
    "project_management": ("pmp", "scrum", "agile", "项目管理", "敏捷"),
    "data_analysis": ("data analysis", "数据分析"),
    "supply_chain": ("supply chain", "供应链", "供应链管理"),
    "procurement": ("procurement", "采购", "采购管理", "寻源"),
    "inventory_management": ("inventory management", "库存管理", "补货"),
    "forecasting": ("forecasting", "demand planning", "需求预测"),
    "logistics": ("logistics", "物流", "运输管理"),
}


SOFT_SKILL_TAXONOMY: dict[str, tuple[str, ...]] = {
    "communication": ("communication", "沟通", "表达"),
    "teamwork": ("teamwork", "team player", "团队合作", "协作"),
    "ownership": ("ownership", "责任心", "主人翁"),
    "learning": ("learning", "学习能力", "快速学习"),
    "problem_solving": ("problem solving", "分析能力", "逻辑思维", "解决问题"),
    "leadership": ("leadership", "领导力", "带队"),
    "execution": ("execution", "执行力", "落地能力"),
    "adaptability": ("adaptability", "抗压", "适应"),
}


def match_taxonomy(text: str, taxonomy: dict[str, tuple[str, ...]]) -> list[str]:
    lowered = text.lower()
    matches: list[str] = []
    for canonical_name, aliases in taxonomy.items():
        if any(alias.lower() in lowered for alias in aliases):
            matches.append(canonical_name)
    return matches
