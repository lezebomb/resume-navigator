"""
==============================================
社区生态爬虫 v1（Community Scraper）
==============================================
用途：抓取"真实发生了什么"
  - 面经与背景数据 → interview_experiences.jsonl
  - HR 淘汰标准     → hr_rejection_rules.jsonl

策略：纯文本语义嗅探 + by_js 点击 + 显式等待
==============================================
"""

import json
import hashlib
import os
import random
import re
import sys
import time
from datetime import datetime

from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import Keys

# ============================================================
# 路径
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_COMPANIES = os.path.join(BASE_DIR, "config_companies.json")
DATA_DIR = os.path.join(BASE_DIR, "data")
INTERVIEW_FILE = os.path.join(DATA_DIR, "interview_experiences.jsonl")
HR_RULES_FILE = os.path.join(DATA_DIR, "hr_rejection_rules.jsonl")
PROFILE_DIR = os.path.join(BASE_DIR, "dp_profile")

for d in [DATA_DIR, PROFILE_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# 平台首页（仅首页，不构造搜索 URL）
# ============================================================
PLATFORMS = {
    "nowcoder": {
        "name": "牛客网",
        "homepage": "https://www.nowcoder.com",
    },
    "zhihu": {
        "name": "知乎",
        "homepage": "https://www.zhihu.com",
    },
}

# ============================================================
# 面经搜索关键词模板（{company} 会被替换）
# ============================================================
INTERVIEW_QUERIES = [
    "{company} 实习 面经",
    "{company} 经管 面试",
    "{company} 商业分析 面经",
    "{company} 产品 面经",
    "{company} 供应链 面试",
    "{company} 采购 实习 面试题",
]

# HR 淘汰标准搜索词（公司无关，全局采集）
HR_REJECTION_QUERIES = [
    "简历被筛 经管 实习",
    "HR 筛选简历 标准",
    "HR 吐槽 简历",
    "简历 一票否决",
    "面试 淘汰 原因 实习",
    "校招 简历 扣分项",
    "实习 面试 踩坑",
    "HR 不要的简历特征",
]

# 脏词清洗
DIRTY_WORDS = [
    "举报", "微信扫码分享", "来自BOSS直聘", "kanzhun",
    "去App", "前往App", "查看更多信息", "点击查看地图",
    "​赞同​", "​添加评论​", "​分享​", "​收藏​", "​喜欢​",
    "​关注问题", "​写回答​",
]


# ============================================================
# 核心引擎
# ============================================================
class CommunityScraper:

    def __init__(self):
        self.page = None
        self.target_companies = []
        self.seen_interview = set()
        self.seen_hr = set()
        self.count_interview = 0
        self.count_hr = 0

        self._load_existing_ids(INTERVIEW_FILE, self.seen_interview)
        self._load_existing_ids(HR_RULES_FILE, self.seen_hr)

    # -------- 配置 --------
    def load_companies(self):
        with open(CONFIG_COMPANIES, "r", encoding="utf-8") as f:
            raw = json.load(f)
        for cat_val in raw.values():
            for name in cat_val.get("companies", []):
                self.target_companies.append(name)
        print(f"[配置] {len(self.target_companies)} 家公司")

    # -------- 浏览器 --------
    def start_browser(self):
        co = ChromiumOptions()
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_user_data_path(os.path.join(PROFILE_DIR, "community"))
        co.set_user_agent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        self.page = ChromiumPage(addr_or_opts=co)
        print("[OK] 浏览器就绪")

    def login_and_wait(self, platform="nowcoder"):
        plat = PLATFORMS.get(platform, PLATFORMS["nowcoder"])
        self.page.get(plat["homepage"])
        time.sleep(3)
        print("\n" + "=" * 60)
        print(f"  已导航到 {plat['name']}（{plat['homepage']}）")
        print("  请在浏览器中登录，完成后按回车")
        print("=" * 60)
        input(">> 按回车开始 <<\n")
        self.current_platform = platform

    # ============================================================
    # 主入口
    # ============================================================
    def run(self, mode="interview", platform="nowcoder", test_limit=0):
        if mode == "interview":
            self._run_interview(platform, test_limit)
        elif mode == "hr":
            self._run_hr_rules(platform)
        elif mode == "all":
            self._run_interview(platform, test_limit)
            self._run_hr_rules(platform)
        print(f"\n[完成] 面经:{self.count_interview} 条 | HR规则:{self.count_hr} 条")

    # ============================================================
    # 面经采集
    # ============================================================
    def _run_interview(self, platform, test_limit=0):
        companies = self.target_companies[:test_limit] if test_limit > 0 else self.target_companies
        plat = PLATFORMS.get(platform, PLATFORMS["nowcoder"])

        print(f"\n[面经] 平台={plat['name']} | {len(companies)} 家公司\n")

        for ci, company in enumerate(companies):
            print(f"\n{'='*50}")
            print(f"[{ci+1}/{len(companies)}] 🏢 {company}")

            for q_tpl in INTERVIEW_QUERIES:
                query = q_tpl.format(company=company)
                self._search_and_collect(
                    query=query,
                    company=company,
                    output_file=INTERVIEW_FILE,
                    seen_set=self.seen_interview,
                    data_type="interview",
                    platform=platform,
                )

            if (ci + 1) % 3 == 0:
                rest = random.randint(15, 30)
                print(f"  [防封] 休息 {rest}s...")
                time.sleep(rest)

    # ============================================================
    # HR 淘汰标准采集
    # ============================================================
    def _run_hr_rules(self, platform):
        plat = PLATFORMS.get(platform, PLATFORMS["nowcoder"])
        print(f"\n[HR规则] 平台={plat['name']} | {len(HR_REJECTION_QUERIES)} 条搜索词\n")

        for qi, query in enumerate(HR_REJECTION_QUERIES):
            print(f"\n  [{qi+1}/{len(HR_REJECTION_QUERIES)}] 🔍 {query}")
            self._search_and_collect(
                query=query,
                company="",
                output_file=HR_RULES_FILE,
                seen_set=self.seen_hr,
                data_type="hr_rule",
                platform=platform,
            )
            self._sleep(5, 12)

    # ============================================================
    # 通用搜索 → 结果列表 → 点击 → 提取正文
    # ============================================================
    def _search_and_collect(self, query, company, output_file, seen_set, data_type, platform="nowcoder"):

        # ---- 物理拟人搜索 ----
        if not self._physical_search(query, platform):
            return

        # ---- 异常页面拦截 ----
        if self._check_search_anomaly():
            print(f"    [Warning] 搜索异常页面，跳过")
            return

        # ---- 找到搜索结果列表中可点击的条目 ----
        result_items = self._find_result_items(query)
        if not result_items:
            print(f"    > 无搜索结果")
            return

        print(f"    > 找到 {len(result_items)} 条结果")

        max_items = min(len(result_items), 8)  # 每次搜索最多取 8 条

        for i in range(max_items):
            try:
                # 重新获取（因为 DOM 可能因导航变化）
                items = self._find_result_items(query)
                if i >= len(items):
                    break
                item = items[i]

                # 提取标题
                title = ""
                try:
                    title = item.text[:60] if item.text else ""
                except Exception:
                    pass

                # 生成去重 ID
                uid = hashlib.md5(f"{title}|{query}".encode()).hexdigest()
                if uid in seen_set:
                    continue

                # 点击进入详情
                try:
                    item.click(by_js=True)
                except Exception:
                    continue

                time.sleep(2)

                # ---- 提取正文 ----
                content = self._extract_post_content()
                if not content or len(content) < 30:
                    self._go_back()
                    continue

                content = self._clean_text(content)

                # ---- 组装数据 ----
                record = {
                    "type": data_type,
                    "company": company,
                    "query": query,
                    "title": title.strip(),
                    "content": content,
                    "source_url": self.page.url,
                    "fetch_time": datetime.now().isoformat(),
                }

                # ---- 面经特有：提取背景和面试题 ----
                if data_type == "interview":
                    record["background"] = self._extract_background(content)
                    record["questions"] = self._extract_questions(content)

                # ---- 落盘 ----
                self._save_jsonl(record, output_file, seen_set, uid)
                if data_type == "interview":
                    self.count_interview += 1
                else:
                    self.count_hr += 1

                print(f"      ✅ [{i+1}] {title[:30]}...")

                self._go_back()
                self._sleep(3, 6)

            except Exception as e:
                print(f"      [异常] {e}")
                self._go_back()

    # ============================================================
    # 搜索结果定位（纯文本语义 + tag:a）
    # ============================================================
    def _find_result_items(self, query):
        """找到搜索结果页中可点击的帖子链接"""
        items = []

        # 策略 1: 找包含关键词片段的 <a> 链接
        try:
            keywords = query.split()
            for kw in keywords[:2]:
                if len(kw) < 2:
                    continue
                hits = self.page.eles(f'text:{kw}', timeout=2)
                for h in hits:
                    try:
                        if h.tag and h.tag.lower() == 'a' and h.text and len(h.text) > 5:
                            items.append(h)
                    except Exception:
                        continue
                if len(items) >= 3:
                    break
        except Exception:
            pass

        # 策略 2: 所有 <a> 中文本 > 10 字的（通用兜底）
        if len(items) < 3:
            try:
                all_a = self.page.eles('tag:a', timeout=2)
                for a in all_a:
                    try:
                        t = a.text or ""
                        href = a.attr('href') or ""
                        if len(t) > 10 and ('discuss' in href or 'question' in href
                                             or 'answer' in href or 'article' in href
                                             or 'zhuanlan' in href or 'post' in href):
                            items.append(a)
                    except Exception:
                        continue
            except Exception:
                pass

        # 去重（按 text）
        seen_text = set()
        unique = []
        for it in items:
            try:
                t = (it.text or "")[:50]
                if t and t not in seen_text:
                    seen_text.add(t)
                    unique.append(it)
            except Exception:
                continue
        return unique

    # ============================================================
    # 帖子正文提取（纯文本语义嗅探）
    # ============================================================
    def _extract_post_content(self):
        """尝试用多种锚点 + body 兜底提取帖子正文"""

        # 策略 1: 找帖子正文的常见锚点
        content_anchors = ["面经", "经历", "分享", "背景", "面试", "一面", "二面",
                           "简历", "HR", "筛选", "淘汰", "岗位"]
        for anchor in content_anchors:
            try:
                el = self.page.ele(f'text:{anchor}', timeout=0.5)
                if el:
                    # 向上找到大容器
                    for level in range(1, 5):
                        try:
                            p = el.parent(level)
                            if p:
                                t = p.text or ""
                                if len(t) > 100:
                                    return t[:5000]
                        except Exception:
                            break
            except Exception:
                continue

        # 策略 2: body 全文取中间部分
        try:
            body = self.page.ele('tag:body')
            if body:
                full = body.text or ""
                if len(full) > 300:
                    return full[100:4000]
                return full
        except Exception:
            pass

        return ""

    # ============================================================
    # 面经特有：提取发帖人背景
    # ============================================================
    @staticmethod
    def _extract_background(text):
        """从面经中提取背景信息"""
        bg = {}
        # 学校
        for kw in ["985", "211", "双一流", "本科", "硕士", "博士", "海归", "海外"]:
            if kw in text:
                bg["education_hint"] = kw
                break
        # 过往实习
        intern_re = re.compile(r'(?:实习|经历)[:：]?\s*(.{5,60})')
        m = intern_re.search(text)
        if m:
            bg["prior_intern"] = m.group(1).strip()
        return bg

    # ============================================================
    # 面经特有：提取面试题
    # ============================================================
    @staticmethod
    def _extract_questions(text):
        """从面经中提取面试问题"""
        questions = []
        # 匹配 "问了xxx" / "Q: xxx" / "问题：xxx"
        patterns = [
            re.compile(r'[问Q][:：\s]*(.{5,80})[？?。\n]'),
            re.compile(r'\d+[\.、]\s*(.{5,80})[？?。\n]'),
        ]
        for pat in patterns:
            for m in pat.finditer(text):
                q = m.group(1).strip()
                if q and q not in questions:
                    questions.append(q)
        return questions[:10]  # 最多 10 题

    # ============================================================
    # 清洗
    # ============================================================
    @staticmethod
    def _clean_text(raw):
        if not raw:
            return ""
        for dirty in DIRTY_WORDS:
            raw = raw.replace(dirty, "")
        raw = re.sub(r'\n{3,}', '\n', raw)
        raw = re.sub(r'[ \t]{3,}', ' ', raw)
        return raw.strip()

    # ============================================================
    # JSONL 落盘
    # ============================================================
    @staticmethod
    def _save_jsonl(record, filepath, seen_set, uid):
        try:
            line = json.dumps(record, ensure_ascii=False)
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
            seen_set.add(uid)
        except Exception as e:
            print(f"    [落盘错误] {e}")

    @staticmethod
    def _load_existing_ids(filepath, seen_set):
        if not os.path.exists(filepath):
            return
        n = 0
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    raw = f"{obj.get('title','')}|{obj.get('query','')}"
                    seen_set.add(hashlib.md5(raw.encode()).hexdigest())
                    n += 1
                except Exception:
                    continue
        if n:
            print(f"[断点续爬] {filepath} 已有 {n} 条")

    # ============================================================
    # 物理拟人搜索（核心重构）
    # ============================================================
    def _physical_search(self, query, platform="nowcoder"):
        """
        在当前页面找到搜索框 → 清空 → 输入关键词 → 回车
        不构造任何 URL
        """
        plat = PLATFORMS.get(platform, PLATFORMS["nowcoder"])

        # 先回到首页（确保搜索框可用）
        try:
            self.page.get(plat["homepage"])
            time.sleep(2)
        except Exception as e:
            print(f"    [导航错误] {e}")
            return False

        # ---- 定位搜索输入框（多策略） ----
        search_box = None

        # 策略 1: type=search 的 input
        try:
            search_box = self.page.ele('tag:input@type=search', timeout=2)
        except Exception:
            pass

        # 策略 2: placeholder 含"搜索"的 input
        if not search_box:
            try:
                search_box = self.page.ele('tag:input@placeholder:搜索', timeout=2)
            except Exception:
                pass

        # 策略 3: placeholder 含 "search" 的 input
        if not search_box:
            try:
                search_box = self.page.ele('tag:input@placeholder:search', timeout=2)
            except Exception:
                pass

        # 策略 4: name/id 含 search/query 的 input
        if not search_box:
            try:
                for attr_kw in ['search', 'query', 'keyword', 'kw']:
                    try:
                        el = self.page.ele(f'tag:input@name:{attr_kw}', timeout=1)
                        if el:
                            search_box = el
                            break
                    except Exception:
                        continue
            except Exception:
                pass

        # 策略 5: 页面上第一个可见的 text input
        if not search_box:
            try:
                inputs = self.page.eles('tag:input', timeout=2)
                for inp in inputs:
                    try:
                        t = inp.attr('type') or 'text'
                        if t.lower() in ('text', 'search', ''):
                            search_box = inp
                            break
                    except Exception:
                        continue
            except Exception:
                pass

        if not search_box:
            print(f"    [错误] 找不到搜索框")
            return False

        # ---- 清空 → 输入 → 回车 ----
        try:
            search_box.click(by_js=True)
            time.sleep(0.3)
            search_box.clear()
            time.sleep(0.2)
            search_box.input(query)
            time.sleep(0.5)
            search_box.input('\n')  # 发送 Enter
        except Exception as e:
            print(f"    [搜索输入错误] {e}")
            return False

        # ---- 强制等待搜索结果渲染 ----
        time.sleep(3)

        try:
            self.page.wait.doc_loaded(timeout=8)
        except Exception:
            pass

        self._sleep(1, 2)
        print(f"    [搜索] {query}")
        return True

    # ============================================================
    # 异常页面检测（404 / 无结果 / 验证码）
    # ============================================================
    def _check_search_anomaly(self):
        """检测当前页面是否出现异常，返回 True 表示有异常"""
        try:
            body = self.page.ele('tag:body')
            if not body:
                return True
            text = (body.text or "")[:1000]

            anomaly_keywords = [
                "404", "页面不存在", "页面未找到", "Page Not Found",
                "没有找到相关", "暂无结果", "无搜索结果",
                "请完成验证", "验证码", "安全验证", "操作频繁",
                "请求过于频繁", "访问受限", "账号异常",
            ]
            for kw in anomaly_keywords:
                if kw in text:
                    print(f"    [异常检测] 页面含「{kw}」")
                    return True
        except Exception:
            pass
        return False

    # ============================================================
    # 辅助
    # ============================================================
    def _go_back(self):
        try:
            self.page.back()
            time.sleep(1.5)
        except Exception:
            pass

    def _sleep(self, lo=3, hi=8):
        time.sleep(random.uniform(lo, hi))


# ============================================================
# 入口
# ============================================================
def main():
    mode = "interview"
    platform = "nowcoder"
    test_limit = 0

    args = sys.argv[1:]
    for arg in args:
        if arg in ("interview", "hr", "all"):
            mode = arg
        elif arg in PLATFORMS:
            platform = arg
        elif arg == "test":
            test_limit = 3
        elif arg.isdigit():
            test_limit = int(arg)

    scraper = CommunityScraper()
    scraper.load_companies()
    scraper.start_browser()
    scraper.login_and_wait(platform)

    print(f"\n[模式] {mode} | 平台={platform} | limit={test_limit or '全量'}")
    scraper.run(mode=mode, platform=platform, test_limit=test_limit)


if __name__ == "__main__":
    main()
