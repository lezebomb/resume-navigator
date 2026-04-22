"""
========================================
ATS Search Agent v7
========================================
功能:
  1. dynamic_search           - 精准搜索 + 物理过滤
  2. extract_industry_insights - 知识融合提炼
  3. get_job_category          - AI 岗位大类判定
  4. get_similar_companies     - AI 同行业头部企业推断
  5. load_knowledge / save_knowledge - 本地 JSON 知识库
  6. run_research_agent        - 主流程（精准搜索 -> 拓展 -> 融合 -> 归档）

依赖:
  pip install requests duckduckgo-search google-genai
========================================
"""

# ============================================================
# 导入区
# ============================================================
import json
import os
import re
import requests
from google import genai


# ============================================================
# 🌐 全局常量
# ============================================================

SEARCH_DOMAINS = ["nowcoder.com", "xiaohongshu.com", "zhihu.com"]

KNOWLEDGE_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "industry_knowledge.json"
)

# 精准搜索的最低数据充足阈值
MIN_SUFFICIENT_TEXTS = 5


def _extract_core_keywords(job_title: str) -> list:
    """
    从岗位名中提取核心关键词用于物理过滤。
    例如 "供应链管理实习生" -> ["供应链", "管理"]
    """
    noise_words = ["实习生", "实习", "助理", "专员", "管培生", "管培", "储备", "岗位", "工程师", "经理"]
    clean = job_title
    for w in noise_words:
        clean = clean.replace(w, "")
    clean = clean.strip()

    if len(clean) <= 1:
        return [job_title[:2]]

    keywords = []
    if len(clean) <= 4:
        keywords.append(clean)
    else:
        for i in range(0, len(clean) - 1, 2):
            kw = clean[i:i + 2]
            if len(kw) == 2:
                keywords.append(kw)

    return keywords if keywords else [clean]


# ============================================================
# 函数 1: dynamic_search - 精准搜索 + 物理过滤
# ============================================================

def dynamic_search(company_name: str, industry_keywords: str, job_title: str, tavily_api_key: str) -> list:
    """
    搜索特定公司 + 行业 + 岗位 的面经，并物理过滤无关内容。
    """
    core_keywords = _extract_core_keywords(job_title)
    print(f"  🔎 物理过滤核心词: {core_keywords}")

    # 方案 A: Tavily
    if not tavily_api_key or not tavily_api_key.strip():
        print("  ❌ 未提供 Tavily API Key，直接跳过 Tavily 搜索。")
        return []

    key = tavily_api_key.strip()
    try:
        print("  🔑 [Tavily] 使用用户 Key 搜索...")

        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": key,
                "query": f"{company_name} {job_title} 面试经验 招聘要求",
                "search_depth": "basic",
                "max_results": 15,
                "include_domains": SEARCH_DOMAINS,
                "include_raw_content": True,
            },
            timeout=20,
        )

        if resp.status_code == 429:
            print("  ⚠️ [Tavily] 配额耗尽(429)。")
            return []
        if resp.status_code in (401, 403):
            print(f"  ⚠️ [Tavily] 未授权({resp.status_code})。")
            return []

        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])

        texts = []
        filtered_count = 0

        for r in results:
            url = r.get("url", "")
            body = r.get("raw_content") or r.get("content") or ""

            if not body or len(body.strip()) <= 30:
                continue

            # 物理过滤
            body_lower = body.lower()
            has_core = any(kw.lower() in body_lower for kw in core_keywords)

            if not has_core:
                filtered_count += 1
                print(f"    🧹 过滤: {url[:50]}... (不含 {core_keywords})")
                continue

            truncated = body[:4000]
            texts.append(truncated)
            print(f"    ✅ {url[:60]}... ({len(truncated)} 字)")

        if filtered_count > 0:
            print(f"  📉 物理过滤丢弃 {filtered_count} 篇无关内容")

        if texts:
            print(f"  ✅ [Tavily] 成功，获得 {len(texts)} 篇")
            return texts

        print("  ⚠️ [Tavily] 过滤后为 0 篇")
        return []

    except Exception as e:
        print(f"  ⚠️ [Tavily] 异常: {e}")
        return []


# ============================================================
# 函数 2: extract_industry_insights - 知识融合提炼（简化提示词）
# ============================================================

def extract_industry_insights(
    raw_texts: list,
    company_name: str,
    job_title: str,
    old_insights: str,
    user_api_key: str,
) -> str:
    """融合新数据与旧知识，生成针对目标公司的简洁情报。"""

    if not raw_texts and not old_insights:
        return "⚠️ 未获取到有效内容，无法生成行业情报。"

    combined_parts = []
    for idx, text in enumerate(raw_texts):
        combined_parts.append(f"=== 新来源 {idx + 1} ===\n{text}")
    new_data = "\n\n".join(combined_parts)[:12000]

    old_section = f"\n\n=== 本地已有旧知识库 ===\n{old_insights[:5000]}" if old_insights else ""

    system_prompt = f"""你是一位世界 500 强企业的资深招聘专家。
当前诊断的【唯一目标岗位】是：{company_name} 的 {job_title}。

【绝对红线】：
你输出的所有技能和考察点，必须 100% 与【{job_title}】的日常真实工作强相关！如果原文混入了其他岗位的噪音，请直接无视！绝不允许在报告中出现与该岗位无关的技术名词。

请输出 3 个板块（Markdown）：
### 1. 核心硬技能护城河 (5-8个符合{job_title}属性的技能)
### 2. ATS 致命淘汰红线
### 3. 面试高频考察点
"""

    full_content = f"{system_prompt}\n\n---新数据 ({len(raw_texts)} 篇)---\n\n{new_data}{old_section}"

    try:
        client = genai.Client(api_key=user_api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_content,
        )
        insights = response.text
        if insights and len(insights) > 50:
            print(f"  ✅ [Gemini] 成功，{len(insights)} 字符")
            return insights
        return "⚠️ Gemini 返回内容过短，无法生成有效情报。"
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return "⚠️ Gemini 请求受限，请稍后重试。"
        return f"❌ Gemini 请求失败: {e}"


# ============================================================
# 函数 3: get_job_category
# ============================================================

def get_job_category(job_title: str, user_api_key: str) -> str:
    """判定岗位所属大类"""
    prompt = (
        f"你是一个HR。请判断『{job_title}』属于哪个招聘大类。"
        f"只返回大类名称（如研发类、产品类、数据类、运营类、市场类、供应链类、财务类、人力类、职能类等）。"
        f"不要多余字符。"
    )
    try:
        client = genai.Client(api_key=user_api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        cat = response.text.strip()
        return cat if cat and 1 < len(cat) <= 10 else "其他类"
    except Exception:
        return "其他类"


# ============================================================
# 函数 4: get_similar_companies - JSON 结构化输出
# ============================================================

def get_similar_companies(company_name: str, job_title: str, user_api_key: str) -> list:
    """
    当目标公司面经数据不足时，AI 推断同行业/同量级头部企业。

    参数:
        company_name : 公司名称
        job_title    : 岗位名称

    返回:
        list : 5 家同类公司名列表
    """
    prompt = (
        f"用户正在搜索【{company_name}】的【{job_title}】面经。"
        f"请推断其行业属性，并推荐 5 家同行业/同量级的头部企业。"
        f"必须严格只返回一个 JSON 数组，例如：[\"大疆\", \"优必选\", \"追觅\", \"科沃斯\", \"石头科技\"]。"
        f"不要有任何 Markdown 标记或多余文字。"
    )

    try:
        client = genai.Client(api_key=user_api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        cleaned = text.replace("```json", "").replace("```", "").strip()

        try:
            companies = json.loads(cleaned)
        except Exception as e:
            print(f"  ⚠️ [同类推断] JSON 解析失败: {e}")
            return []

        if isinstance(companies, list):
            companies = [c.strip() for c in companies if isinstance(c, str) and c.strip()]
            companies = [c for c in companies if len(c) <= 15]
            return companies[:5]
        print("  ⚠️ [同类推断] 解析结果不是列表")
        return []
    except Exception as e:
        print(f"  ⚠️ [同类推断] 请求失败: {e}")
        return []


# ============================================================
# 函数 5: load_knowledge
# ============================================================

def load_knowledge(company_name: str, job_title: str) -> str:
    """从本地知识库读取已有情报"""
    composite_key = f"{company_name}_{job_title}"
    if not os.path.exists(KNOWLEDGE_DB_PATH):
        return None
    try:
        with open(KNOWLEDGE_DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
        for category, jobs in db.items():
            if isinstance(jobs, dict) and composite_key in jobs:
                record = jobs[composite_key]
                if isinstance(record, dict) and record.get("insights"):
                    return record["insights"]
    except Exception as e:
        print(f"  ⚠️ [知识库] 读取失败: {e}")
    return None


# ============================================================
# 函数 6: save_knowledge
# ============================================================

def save_knowledge(company_name: str, job_title: str, insights: str, category: str):
    """覆盖保存到本地知识库"""
    composite_key = f"{company_name}_{job_title}"
    db_dir = os.path.dirname(KNOWLEDGE_DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    db = {}
    if os.path.exists(KNOWLEDGE_DB_PATH):
        try:
            with open(KNOWLEDGE_DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception:
            db = {}

    if category not in db:
        db[category] = {}

    from datetime import datetime
    db[category][composite_key] = {
        "insights": insights,
        "updated": datetime.now().isoformat(),
    }

    try:
        with open(KNOWLEDGE_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  ⚠️ [知识库] 写入失败: {e}")


# ============================================================
# 函数 7: run_research_agent - 多级降级搜索主流程
# ============================================================

def run_research_agent(
    company_name: str,
    industry_keywords: str,
    job_title: str,
    user_api_key: str,
    tavily_api_key: str,
) -> str:
    """
    一键行业情报研究（多级降级搜索策略）。

    流程:
      1. 读取本地缓存 old_insights。
      2. 调用 dynamic_search 进行第一轮精准搜索。
      3. 强校验：若 len(raw_texts) < 3，调用同类拓展搜索。
      4. 融合后调用 extract_industry_insights 提炼。
    """

    print("\n" + "=" * 60)
    print(f"  📌 行业情报引擎 v7（多级降级搜索）")
    print(f"  🏢 公司: {company_name} | 🧭 行业: {industry_keywords}")
    print(f"  🧑‍💻 岗位: {job_title}")
    gemini_status = "已提供" if user_api_key and user_api_key.strip() else "未提供"
    tavily_status = "已提供" if tavily_api_key and tavily_api_key.strip() else "未提供"
    print(f"  🔑 Tavily: {tavily_status} | Gemini: {gemini_status}")
    print("=" * 60)

    # ---- 步骤 1: 读取旧知识 ----
    print("\n📥 步骤 1/5: 读取本地知识库...")
    old_insights = load_knowledge(company_name, job_title)
    if old_insights:
        print(f"  ✅ 找到旧知识（{len(old_insights)} 字），将与新数据融合")
    else:
        print("  ℹ️ 无旧知识")

    # ---- 步骤 2: 阶段 1 精准搜索 ----
    print(f"\n🔍 步骤 2/5: 阶段 1 — 精准搜索《{company_name} × {job_title}》...")
    raw_texts = dynamic_search(company_name, industry_keywords, job_title, tavily_api_key)
    print(f"\n  📄 阶段 1 结果: {len(raw_texts)} 篇有效正文")

    # ---- 步骤 3: 强校验与拓展搜索 ----
    if len(raw_texts) < 3:
        print("\n🔄 步骤 3/5: 强校验执行中...")
        print("⚠️ 精准数据不足，触发同类拓展搜索...")

        similar_companies = get_similar_companies(company_name, job_title, user_api_key)

        if similar_companies:
            print(f"  🏢 AI 推荐同类企业: {similar_companies}")

            for sc in similar_companies:
                print(f"\n  🔍 拓展搜索: 《{sc} × {job_title}》...")
                extra_texts = dynamic_search(sc, industry_keywords, job_title, tavily_api_key)
                if extra_texts:
                    print(f"    ✅ 获得 {len(extra_texts)} 篇")
                    raw_texts.extend(extra_texts)
                else:
                    print(f"    ℹ️ 未获得有效数据")

                if len(raw_texts) >= 10:
                    print(f"\n  📊 数据量达标 ({len(raw_texts)} >= 10)，停止拓展以防信息过载。")
                    break

            print(f"\n  📄 拓展后总计: {len(raw_texts)} 篇")
        else:
            print("  ⚠️ 未能推断同类企业，使用现有数据继续")
    else:
        print(f"\n✅ 步骤 3/5: 数据充足（{len(raw_texts)} ≥ 3），跳过拓展")

    # 全部为空的保护
    if not raw_texts and not old_insights:
        return "⚠️ 搜索未返回结果，且无本地缓存。请检查 API Key 或稍后重试。"
    if not raw_texts and old_insights:
        print("  ⚠️ 搜索无新数据，返回旧知识")
        return old_insights

    # 🔪 物理清洗：从源头掐断注意力劫持
    if 'similar_companies' in locals() and similar_companies:
        print("  🔪 正在进行物理清洗，将竞品名称替换为目标公司...")
        for i in range(len(raw_texts)):
            for sc in similar_companies:
                if sc and len(sc) > 1:  # 防止空字符或单字误杀
                    raw_texts[i] = raw_texts[i].replace(sc, company_name)

    # ---- 步骤 4: 全量融合提炼 ----
    print(f"\n🧠 步骤 4/5: 全量融合提炼（{len(raw_texts)} 篇 + 旧知识）...")
    insights = extract_industry_insights(
        raw_texts,
        company_name,
        job_title,
        old_insights or "",
        user_api_key,
    )

    if insights.startswith("❌") or insights.startswith("⚠️"):
        return insights

    # ---- 步骤 5: 分类归档 ----
    print("\n📂 步骤 5/5: AI 分类 + 覆盖归档...")
    category = get_job_category(job_title, user_api_key)
    save_knowledge(company_name, job_title, insights, category)
    print(f"  ✅ 已覆盖更新至《{category}》")

    print("\n" + "=" * 60)
    print("  ✅ 行业情报研究完成")
    print("=" * 60)

    return insights


# ============================================================
# 测试入口
# ============================================================

if __name__ == "__main__":
    test_company = "追觅科技"
    test_industry = "智能硬件/机器人独角兽"
    test_job = "供应链管理实习生"

    test_user_key = os.getenv("GEMINI_API_KEY", "").strip()
    test_tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not test_user_key:
        print("❌ 请先设置环境变量 GEMINI_API_KEY")
    else:
        result = run_research_agent(
            test_company,
            test_industry,
            test_job,
            test_user_key,
            test_tavily_key,
        )
        print("\n" + "=" * 60)
        print("  🧾 最终情报")
        print("=" * 60)
        print(result)
