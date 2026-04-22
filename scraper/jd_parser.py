"""
========================================
模块二：JD 数据解析模块
========================================
对抓取到的 HTML/原始文本进行结构化解析，提取：
  - 公司基础信息（名称、规模、融资阶段/是否上市）
  - 岗位职责描述（清洗为纯文本）
  - 硬性技能要求（软件、工具、证书）
  - 软素质偏好（沟通、协作、抗压等）
========================================
"""

import re
from typing import Optional
from bs4 import BeautifulSoup

# ============================================================
# 硬技能关键词库（经管类岗位常见）
# ============================================================
HARD_SKILL_KEYWORDS = [
    # 办公工具
    "Excel", "PPT", "PowerPoint", "Word", "Visio", "Outlook",
    "WPS", "Google Sheets", "Notion", "飞书", "钉钉",
    # 数据分析
    "Python", "R语言", "SQL", "SPSS", "SAS", "Tableau", "Power BI",
    "MATLAB", "Stata", "EViews", "数据分析", "数据挖掘", "数据建模",
    "数据可视化", "统计分析", "回归分析",
    # 金融工具
    "Wind", "万得", "Bloomberg", "彭博", "iFind", "同花顺",
    "Choice", "东方财富", "Refinitiv", "FactSet", "Capital IQ",
    # 财务/审计
    "SAP", "Oracle", "金蝶", "用友", "财务建模", "估值模型",
    "DCF", "WACC", "三大报表", "合并报表",
    # 证书
    "CFA", "CPA", "ACCA", "FRM", "CMA", "CICPA", "司法考试",
    "证券从业", "基金从业", "银行从业", "期货从业", "会计初级",
    "会计中级", "注册会计师", "税务师", "精算师",
    # 外语
    "英语", "CET-4", "CET-6", "四级", "六级", "雅思", "IELTS",
    "托福", "TOEFL", "GMAT", "GRE", "商务英语", "BEC",
    # 项目管理
    "PMP", "Scrum", "Agile", "敏捷", "JIRA", "Confluence",
    # 设计
    "Photoshop", "PS", "Figma", "Sketch", "Canva", "Axure",
    # 营销
    "SEO", "SEM", "信息流", "新媒体", "小红书", "抖音", "公众号",
    "Google Analytics", "百度统计", "CRM", "Salesforce", "HubSpot",
]

# ============================================================
# 软素质关键词库
# ============================================================
SOFT_SKILL_KEYWORDS = [
    "沟通能力", "沟通协调", "跨部门沟通", "表达能力", "口头表达",
    "书面表达", "文字功底", "写作能力",
    "团队合作", "团队协作", "协作精神", "合作精神",
    "责任心", "责任感", "敬业精神", "主人翁意识",
    "抗压能力", "抗压", "承受压力", "高压环境",
    "学习能力", "快速学习", "学习意愿", "持续学习", "自我驱动",
    "逻辑思维", "分析能力", "逻辑分析", "批判性思维",
    "主动性", "积极主动", "自驱力", "主观能动性",
    "细致认真", "细心", "严谨", "注重细节",
    "领导力", "领导才能", "管理能力",
    "创新", "创造力", "创新思维",
    "执行力", "落地能力", "结果导向",
    "时间管理", "多任务处理", "优先级管理",
    "客户导向", "服务意识", "客户关系",
    "商业嗅觉", "商业敏感度", "市场洞察",
    "诚信", "正直", "职业道德",
]

# ============================================================
# 公司规模/融资阶段匹配
# ============================================================
COMPANY_STAGE_PATTERNS = [
    (r"已上市|上市公司|A股|港股|美股|IPO", "已上市"),
    (r"D轮|E轮|F轮|Pre-IPO", "D轮及以上"),
    (r"C轮|C\+轮", "C轮"),
    (r"B轮|B\+轮", "B轮"),
    (r"A轮|A\+轮|天使轮|种子轮", "早期"),
    (r"独角兽", "独角兽"),
    (r"世界500强|Fortune 500|五百强", "世界500强"),
    (r"国企|央企|国有", "国企/央企"),
    (r"外企|外资|合资", "外企/合资"),
]

COMPANY_SIZE_PATTERNS = [
    (r"10000人以上|万人以上", "10000人以上"),
    (r"1000-9999人|1000\+", "1000-9999人"),
    (r"500-999人", "500-999人"),
    (r"100-499人", "100-499人"),
    (r"20-99人", "20-99人"),
    (r"0-20人|少于20人", "少于20人"),
]


# ============================================================
# 核心解析函数
# ============================================================
def clean_html_to_text(html_content: str) -> str:
    """
    清洗 HTML 为纯文本。

    - 移除所有 HTML 标签
    - 保留有意义的换行（<br>, <p>, <div> → 换行）
    - 去除多余空白
    """
    if not html_content:
        return ""

    try:
        # 将块级元素替换为换行
        text = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
        text = re.sub(r'</(p|div|li|tr|h[1-6])>', '\n', text, flags=re.IGNORECASE)

        # 用 BeautifulSoup 去除所有 HTML 标签
        soup = BeautifulSoup(text, "lxml")
        clean_text = soup.get_text(separator="\n")

        # 合并连续空行，去除首尾空白
        clean_text = re.sub(r'\n\s*\n', '\n', clean_text)
        clean_text = re.sub(r'[ \t]+', ' ', clean_text)
        return clean_text.strip()
    except Exception as e:
        # 容错：如果解析失败，用正则粗暴清洗
        fallback = re.sub(r'<[^>]+>', ' ', html_content)
        return re.sub(r'\s+', ' ', fallback).strip()


def extract_hard_skills(text: str) -> list[str]:
    """从 JD 文本中提取硬性技能要求"""
    found = []
    text_lower = text.lower()
    for skill in HARD_SKILL_KEYWORDS:
        if skill.lower() in text_lower:
            if skill not in found:
                found.append(skill)
    return found


def extract_soft_skills(text: str) -> list[str]:
    """从 JD 文本中提取软素质偏好"""
    found = []
    for skill in SOFT_SKILL_KEYWORDS:
        if skill in text:
            if skill not in found:
                found.append(skill)
    return found


def detect_company_stage(raw_text: str) -> str:
    """从公司描述中推断融资阶段"""
    for pattern, label in COMPANY_STAGE_PATTERNS:
        if re.search(pattern, raw_text):
            return label
    return "未知"


def detect_company_size(raw_text: str) -> str:
    """从公司描述中提取规模"""
    for pattern, label in COMPANY_SIZE_PATTERNS:
        if re.search(pattern, raw_text):
            return label
    return "未知"


def parse_jd_record(raw: dict) -> Optional[dict]:
    """
    解析单条抓取到的 JD 原始数据。

    输入 raw 字段：
        - url, job_title, salary, company_name, company_size
        - jd_html (HTML 原文), tags (标签列表), location

    输出结构化数据：
        - company_info: {name, size, stage, location}
        - job_info: {title, salary, description, tags}
        - skills: {hard_skills, soft_skills}
        - meta: {url, platform, keyword}
    """
    if not raw:
        return None

    try:
        # 清洗 JD HTML → 纯文本
        jd_text = clean_html_to_text(raw.get("jd_html", ""))
        if not jd_text:
            return None

        # 合并所有文本用于技能提取
        all_text = f"{jd_text} {' '.join(raw.get('tags', []))} {raw.get('job_title', '')}"

        # 提取技能
        hard_skills = extract_hard_skills(all_text)
        soft_skills = extract_soft_skills(all_text)

        # 推断公司信息
        company_raw = f"{raw.get('company_name', '')} {raw.get('company_size', '')} {' '.join(raw.get('tags', []))}"
        stage = detect_company_stage(company_raw)
        size = detect_company_size(company_raw) or raw.get("company_size", "未知")

        return {
            "company_info": {
                "name": raw.get("company_name", "").strip(),
                "size": size,
                "stage": stage,
                "location": raw.get("location", "上海").strip(),
            },
            "job_info": {
                "title": raw.get("job_title", "").strip(),
                "salary": raw.get("salary", "").strip(),
                "description": jd_text,
                "tags": raw.get("tags", []),
            },
            "skills": {
                "hard_skills": hard_skills,
                "soft_skills": soft_skills,
            },
            "meta": {
                "url": raw.get("url", ""),
                "platform": raw.get("source_platform", ""),
                "keyword": raw.get("search_keyword", ""),
            },
        }

    except Exception as e:
        print(f"[解析错误] {e}")
        return None


def parse_all(raw_list: list[dict]) -> list[dict]:
    """批量解析所有抓取的原始 JD 数据"""
    parsed = []
    for i, raw in enumerate(raw_list):
        result = parse_jd_record(raw)
        if result:
            parsed.append(result)
        else:
            print(f"[跳过] 第 {i+1} 条数据解析失败或为空")
    print(f"[解析完成] {len(parsed)}/{len(raw_list)} 条成功")
    return parsed
