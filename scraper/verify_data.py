"""
========================================
数据验证与质量检测工具
========================================
功能：
  1. 验证主应用的 AI 诊断准确性（用典型简历+JD 做基准测试）
  2. 验证爬取数据的完整性和质量
  3. 生成验证报告
========================================
"""

import json
import os
import sys

# 把项目根目录加入 path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)


# ============================================================
# 1. AI 诊断准确性验证（基准测试）
# ============================================================

# 测试用例：已知正确答案的简历+JD对
BENCHMARK_CASES = [
    {
        "name": "高匹配度案例（金融分析）",
        "resume": """
姓名：张三
学历：上海交通大学 金融学硕士（2024-2026）
技能：Python、SQL、Wind、Excel、财务建模、DCF估值
经历：
1. 中金公司 投资银行部 实习生（2025.01-2025.06）
   - 主导3个IPO项目的财务尽职调查，分析超过500页财务报表
   - 使用Python+Wind搭建行业对标分析模型，覆盖50+上市公司
   - 撰写投资价值分析报告12份，获部门优秀实习生称号
2. 德勤会计师事务所 审计实习生（2024.07-2024.12）
   - 参与4家上市公司年度审计，负责应收账款和存货科目
   - 使用Excel建立风险评估矩阵，发现2处重大错报
证书：CFA Level I 通过、CPA 在考、证券从业资格
英语：IELTS 7.5、BEC高级
""",
        "jd": """
岗位：投资银行分析师实习生 | 中信证券上海
要求：
1. 国内外知名高校金融、经济、会计类硕士在读
2. 熟练使用Wind、Bloomberg等金融数据库
3. 精通Excel和PowerPoint，了解财务建模
4. 具备CFA/CPA等专业资格优先
5. 英语流利，可用英文撰写报告
6. 有投行、券商或四大实习经验优先
7. 较强的逻辑分析能力和沟通表达能力
8. 能保证每周4天以上到岗，实习期不少于3个月
""",
        "expected_score_range": (82, 98),
        "expected_matched_skills": ["Python", "Wind", "Excel", "财务建模", "CFA", "CPA"],
        "expected_missing_skills": ["Bloomberg", "PowerPoint"],
        "description": "简历高度匹配JD，应得到高分",
    },
    {
        "name": "低匹配度案例（跨专业）",
        "resume": """
姓名：李四
学历：某大学 中文系本科（2021-2025）
技能：写作、摄影、Photoshop
经历：
1. 校报记者（2022-2024）
   - 采写新闻稿件30余篇
   - 负责校报排版设计
2. 学生会宣传部长
   - 策划校园文化活动5场
英语：CET-4 500分
""",
        "jd": """
岗位：量化研究实习生 | 某量化基金上海
要求：
1. 数学、统计、计算机、物理等理工科硕士优先
2. 精通Python/C++，有机器学习项目经验
3. 熟悉统计模型、时间序列分析
4. 有量化交易或因子研究经验优先
5. 通过CFA/FRM优先
""",
        "expected_score_range": (15, 45),
        "expected_matched_skills": [],
        "expected_missing_skills": ["Python", "C++", "机器学习"],
        "description": "中文系本科 vs 量化岗位，完全不匹配，应得低分",
    },
    {
        "name": "中等匹配度案例（市场营销）",
        "resume": """
姓名：王五
学历：复旦大学 工商管理硕士（2024-2026）
技能：Excel、PPT、SPSS、新媒体运营、小红书
经历：
1. 某快消品牌 市场部实习生（2025.03-2025.06）
   - 协助策划3次线上营销活动，累计曝光量120万
   - 运营品牌小红书账号，3个月涨粉8000+
   - 使用SPSS分析消费者调研数据，输出2份洞察报告
2. 学校商业策划大赛 一等奖（2024）
英语：CET-6 560分
""",
        "jd": """
岗位：品牌策略实习生 | 宝洁上海
要求：
1. 市场营销、工商管理、传媒等相关专业硕士
2. 熟练使用Excel进行数据分析
3. 了解数字营销和社交媒体运营（小红书、抖音等）
4. 具备消费者洞察和市场趋势分析能力
5. 英语流利（书面和口语）
6. 有FMCG或4A广告公司实习经验优先
7. 出色的PPT制作和演示汇报能力
""",
        "expected_score_range": (65, 85),
        "expected_matched_skills": ["Excel", "PPT", "小红书", "SPSS"],
        "expected_missing_skills": ["抖音"],
        "description": "有相关经验但非完全匹配，应得中高分",
    },
]


def run_ai_benchmark(api_key: str):
    """执行 AI 诊断基准测试"""
    from utils.ai_analyzer import analyze_resume

    print("\n" + "=" * 60)
    print("  AI 诊断准确性基准测试")
    print("=" * 60)

    results = []
    passed = 0
    total = len(BENCHMARK_CASES)

    for i, case in enumerate(BENCHMARK_CASES):
        print(f"\n▶ 测试 {i+1}/{total}: {case['name']}")
        print(f"  说明: {case['description']}")

        result = analyze_resume(case["resume"], case["jd"], "", api_key)

        if not result["success"]:
            print(f"  ❌ AI 调用失败: {result.get('error')}")
            results.append({"case": case["name"], "status": "FAIL", "reason": "API调用失败"})
            continue

        data = result["data"]
        score = data.get("overall_score", 0)
        lo, hi = case["expected_score_range"]

        # 验证分数范围
        score_ok = lo <= score <= hi
        print(f"  AI 评分: {score} | 期望范围: {lo}~{hi} | {'✅ 通过' if score_ok else '❌ 偏差过大'}")

        # 验证技能匹配
        matched = data.get("hard_skills", {}).get("matched", [])
        missing = data.get("hard_skills", {}).get("missing", [])

        expected_matched = case["expected_matched_skills"]
        match_hits = sum(1 for s in expected_matched if any(s.lower() in m.lower() for m in matched))
        match_rate = match_hits / max(len(expected_matched), 1)
        print(f"  技能匹配率: {match_hits}/{len(expected_matched)} ({match_rate:.0%})")

        case_passed = score_ok and match_rate >= 0.5
        if case_passed:
            passed += 1

        results.append({
            "case": case["name"],
            "status": "PASS" if case_passed else "WARN",
            "score": score,
            "expected_range": f"{lo}-{hi}",
            "match_rate": f"{match_rate:.0%}",
        })

    # 总结
    print("\n" + "=" * 60)
    print(f"  基准测试结果: {passed}/{total} 通过")
    print("=" * 60)
    for r in results:
        emoji = "✅" if r["status"] == "PASS" else "⚠️" if r["status"] == "WARN" else "❌"
        print(f"  {emoji} {r['case']}: {r.get('score', 'N/A')} (期望{r.get('expected_range', '?')}) 匹配率{r.get('match_rate', '?')}")

    return {"passed": passed, "total": total, "details": results}


# ============================================================
# 2. 爬取数据质量验证
# ============================================================
def verify_scraped_data(json_file: str):
    """验证爬取数据的质量"""
    print("\n" + "=" * 60)
    print("  爬取数据质量验证")
    print("=" * 60)

    if not os.path.exists(json_file):
        print(f"  ❌ 文件不存在: {json_file}")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = len(data)
    print(f"\n  总记录数: {total}")

    # 字段完整率
    fields = ["title", "company", "jd_raw", "salary", "location", "tags"]
    print("\n  字段完整率:")
    for field in fields:
        count = sum(1 for d in data if d.get(field))
        rate = count / max(total, 1)
        bar = "█" * int(rate * 20) + "░" * (20 - int(rate * 20))
        emoji = "✅" if rate > 0.7 else "⚠️" if rate > 0.3 else "❌"
        print(f"    {emoji} {field:15s} {bar} {rate:.0%} ({count}/{total})")

    # JD 文本长度分布
    jd_lengths = [len(d.get("jd_raw", "")) for d in data if d.get("jd_raw")]
    if jd_lengths:
        avg_len = sum(jd_lengths) / len(jd_lengths)
        min_len = min(jd_lengths)
        max_len = max(jd_lengths)
        short = sum(1 for l in jd_lengths if l < 50)
        print(f"\n  JD 文本长度: 平均{avg_len:.0f}字 | 最短{min_len}字 | 最长{max_len}字")
        print(f"  过短(<50字): {short}条 {'⚠️ 需检查' if short > total*0.2 else '✅ 正常'}")

    # 公司去重
    companies = set(d.get("company", "").strip() for d in data if d.get("company"))
    print(f"\n  涉及公司数: {len(companies)}")

    # 关键词覆盖
    keywords_used = set(d.get("_keyword", "") for d in data)
    print(f"  关键词覆盖: {len(keywords_used)} 个")

    # 平台分布
    platforms = {}
    for d in data:
        p = d.get("_platform", "unknown")
        platforms[p] = platforms.get(p, 0) + 1
    if platforms:
        print(f"  平台分布: {platforms}")

    print(f"\n  {'✅ 数据质量良好' if total > 50 else '⚠️ 数据量偏少，建议继续抓取'}")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    print("JD 数据验证工具")
    print("-" * 40)
    print("用法:")
    print("  1. 验证爬取数据:   python scraper/verify_data.py data")
    print("  2. AI基准测试:     python scraper/verify_data.py ai <API_KEY>")
    print()

    if len(sys.argv) < 2:
        print("请指定验证模式: data 或 ai")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "data":
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        found = False
        for f in os.listdir(data_dir) if os.path.exists(data_dir) else []:
            if f.startswith("raw_jd_") and f.endswith(".json"):
                verify_scraped_data(os.path.join(data_dir, f))
                found = True
        if not found:
            # 也检查上级目录
            parent = os.path.dirname(os.path.abspath(__file__))
            for f in os.listdir(parent):
                if f.startswith("raw_jd") and f.endswith(".json"):
                    verify_scraped_data(os.path.join(parent, f))
                    found = True
        if not found:
            print("未找到爬取数据文件，请先运行 jd_scraper.py")

    elif mode == "ai":
        if len(sys.argv) < 3:
            print("请提供 API Key: python scraper/verify_data.py ai YOUR_API_KEY")
            sys.exit(1)
        api_key = sys.argv[2]
        result = run_ai_benchmark(api_key)
        print(f"\n最终结果: {result['passed']}/{result['total']} 通过")

    else:
        print(f"未知模式: {mode}")
