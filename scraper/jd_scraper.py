"""
==============================================
全量 JD 抓取引擎 v4（纯文本语义嗅探版）
==============================================
彻底摆脱固定 CSS 选择器！

定位策略：
  1. 列表探测：直接搜 page 中包含目标公司名的文本元素
  2. JD 提取：搜 "职位描述/岗位职责/任职要求" 文本 → .parent() 上溯
  3. 滚动：直接对 body 发送 PAGE_DOWN
  4. 保底：body 全文 + 正则截取
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

from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import Keys

# ============================================================
# 路径
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_COMPANIES = os.path.join(BASE_DIR, "config_companies.json")
CONFIG_KEYWORDS = os.path.join(BASE_DIR, "config_keywords.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "valid_scraped_data.jsonl")
PROFILE_DIR = os.path.join(BASE_DIR, "dp_profile")

for d in [os.path.join(BASE_DIR, "data"), PROFILE_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# JD 区块的文本锚点（用于语义定位，非 CSS）
# ============================================================
JD_ANCHORS = ["职位描述", "岗位职责", "任职要求", "工作职责", "工作内容", "职责描述", "岗位描述"]
SALARY_RE = re.compile(r'\d+[-~到至]\d+[Kk元·/千万]+[/每]?[月天年]?')
SIZE_RE = re.compile(r'\d+[-~]\d+人|\d+人以上')
LOC_RE = re.compile(r'((?:上海|北京|深圳|广州|杭州|南京|成都|武汉|苏州)[·\-\s]?[\u4e00-\u9fa5]{0,10}[区县]?)')
EXP_RE = re.compile(r'(经验不限|在校[/·]?实习|\d+[-~]\d+年)')


# ============================================================
# 核心引擎
# ============================================================
class DrissionScraper:

    SEARCH_URL = "https://www.zhipin.com/web/geek/job?query={keyword}&city=101020100"

    def __init__(self):
        self.page = None
        self.target_companies = []
        self.target_set = set()
        self.company_categories = {}
        self.directions = {}
        self.seen_ids = set()
        self.saved_count = 0
        self.title_filter_keywords = set()

        # ---- 岗位有效性判定词表 ----
        self.title_blacklist = [
            '研发', '开发', '测试', '算法', 'IT', '工程师', '前端', '后端',
            '医药代表', '医学', '科学家', '销售代表', '地推', '客服',
            '护士', '药师', '临床', '注册', '机械', '电气', '嵌入式',
        ]
        self.neutral_words = ['实习', '管培', '储备干部', '轮岗', 'Intern', 'Trainee']
        self.business_words = [
            '运营', '产品', '市场', '分析', '供应链', '采购', '财务',
            'HR', '人力', '战略', '商业', '项目管理', '品牌', '投资',
            '咨询', '审计', 'BD', '商务', 'PMO', 'ERP',
        ]
        self._load_existing_ids()

    # -------- 配置 --------
    def load_configs(self):
        with open(CONFIG_COMPANIES, "r", encoding="utf-8") as f:
            raw = json.load(f)
        for cat_key, cat_val in raw.items():
            desc = cat_val.get("description", cat_key)
            for name in cat_val.get("companies", []):
                self.target_companies.append(name)
                self.target_set.add(name)
                self.company_categories[name] = desc

        with open(CONFIG_KEYWORDS, "r", encoding="utf-8") as f:
            kw_raw = json.load(f)
        for dir_key, dir_val in kw_raw.items():
            kws = set()
            for field in ["hard_skills", "terms", "soft_skills"]:
                kws.update(dir_val.get(field, []))
            self.directions[dir_key] = {
                "direction": dir_val.get("direction", dir_key),
                "keywords": kws,
            }
        # 构建标题过滤关键词集（从方向名 + 通用经管词）
        self.title_filter_keywords = {
            "采购", "供应链", "运营", "产品", "商业分析", "战略",
            "金融", "投资", "咨询", "财务", "审计", "市场", "品牌",
            "HR", "人力", "数据分析", "管培", "BD", "商务", "实习",
            "项目管理", "PMO", "ERP", "SaaS", "CRM",
        }
        # 也从配置文件的 direction 名称中提取关键词
        for _, d_info in self.directions.items():
            for word in d_info["direction"]:
                if len(word) >= 2:
                    self.title_filter_keywords.add(word)

        print(f"[配置] {len(self.target_companies)} 家公司 | {len(self.directions)} 个方向 | {len(self.title_filter_keywords)} 个标题过滤词")

    # -------- 浏览器 --------
    def start_browser(self):
        co = ChromiumOptions()
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_user_data_path(os.path.join(PROFILE_DIR, "boss"))
        co.set_user_agent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        self.page = ChromiumPage(addr_or_opts=co)
        print("[OK] 浏览器就绪")

    def login_and_wait(self):
        self.page.get("https://www.zhipin.com/")
        time.sleep(3)
        print("\n" + "=" * 60)
        print("  请在浏览器中登录，完成后按回车")
        print("=" * 60)
        input(">> 按回车开始 <<\n")

    # ============================================================
    # 主入口
    # ============================================================
    def run_scraper(self, test_limit=0):
        targets = self.target_companies[:test_limit] if test_limit > 0 else self.target_companies
        total = len(targets)
        print(f"\n[启动] {total} 家公司\n")

        for ci, company in enumerate(targets):
            cat = self.company_categories.get(company, "")
            print(f"\n{'='*55}")
            print(f"[{ci+1}/{total}] 🏢 {company}  ({cat})")
            print(f"{'='*55}")

            self._scrape_company(company)

            if (ci + 1) % 3 == 0:
                rest = random.randint(10, 20)
                print(f"\n  [防封] 休息 {rest}s...")
                time.sleep(rest)

        print(f"\n{'='*55}")
        print(f"[完成] 本次新增 {self.saved_count} 条 => {OUTPUT_FILE}")

    # ============================================================
    # 单个公司的采集流程
    # ============================================================
    def _scrape_company(self, company):
        keyword = f"{company} 实习"
        url = self.SEARCH_URL.format(keyword=keyword)

        try:
            self.page.get(url)
        except Exception as e:
            print(f"  [导航错误] {e}")
            return

        # 显式等待 SPA 渲染
        try:
            self.page.wait.doc_loaded(timeout=10)
        except Exception:
            pass
        self._sleep(3, 5)
        self._scroll_body(3)
        time.sleep(2)

        # ============================================================
        # 策略 1：基于文本搜索包含目标公司名的元素
        # ============================================================
        max_scroll_rounds = 8
        processed_hrefs = set()

        for scroll_round in range(max_scroll_rounds):
            # 找到所有包含公司名文本的元素
            hits = self._find_company_hits(company)
            new_hits = [h for h in hits if id(h) not in {id(x) for x in []}
                        and self._get_nearby_href(h) not in processed_hrefs]

            if not new_hits and scroll_round == 0:
                # 如果第一轮就没找到，可能页面确实没有该公司的结果
                print(f"  > 未找到包含「{company}」的元素")
                # 打印 debug
                try:
                    body = self.page.ele('tag:body')
                    full_text = body.text if body else ""
                    print(f"  [Debug] 页面文本长度: {len(full_text)}")
                    print(f"  [Debug] 出现「{company}」: {'是' if company in full_text else '否'}")
                except Exception:
                    pass
                return

            if not new_hits:
                print(f"  > 第 {scroll_round+1} 轮无新增结果")
                break

            print(f"\n  [第 {scroll_round+1} 轮] 找到 {len(new_hits)} 个包含「{company}」的元素")

            for i, hit_el in enumerate(new_hits):
                href = self._get_nearby_href(hit_el)
                if href in processed_hrefs:
                    continue
                if href:
                    processed_hrefs.add(href)

                try:
                    # ---- 记录点击前的标签页 ----
                    tabs_before = set(self.page.tab_ids)
                    original_tab = self.page.tab_ids[0]

                    result = self._click_and_extract(hit_el, company, i, len(new_hits))

                    # ---- 优化一：标签页生命周期管理 ----
                    try:
                        tabs_after = set(self.page.tab_ids)
                        new_tabs = tabs_after - tabs_before
                        for t_id in new_tabs:
                            try:
                                tab = self.page.get_tab(t_id)
                                if tab:
                                    tab.close()
                            except Exception:
                                pass
                        # 确保控制权回到主列表页
                        if original_tab in self.page.tab_ids:
                            self.page.to_tab(original_tab)
                    except Exception:
                        pass

                    if result:
                        title = result.get("title", "")
                        jd = result.get("jd_full_text", "")

                        # ---- 第一层：黑名单拦截 ----
                        if any(bw in title for bw in self.title_blacklist):
                            print(f"    [黑名单] {title[:30]}")
                        # ---- 第二层：直接命中经管业务词 → 通过 ----
                        elif any(bw in title for bw in self.business_words):
                            matched_dir = self._check_relevance(result)
                            result["matched_direction"] = matched_dir or "标题直通"
                            result["company_category"] = self.company_categories.get(company, "")
                            result["fetch_time"] = datetime.now().isoformat()
                            self._save_to_jsonl(result)
                            print(f"    ✅ [{i+1}/{len(new_hits)}] {title[:25]} | {result['matched_direction'][:15]}")
                        # ---- 第三层：仅命中中性词 → 需 JD 二次校验 ----
                        elif any(nw in title for nw in self.neutral_words):
                            has_biz = any(bw in title + jd[:1500] for bw in self.business_words)
                            if has_biz:
                                matched_dir = self._check_relevance(result)
                                result["matched_direction"] = matched_dir or "中性词+JD校验"
                                result["company_category"] = self.company_categories.get(company, "")
                                result["fetch_time"] = datetime.now().isoformat()
                                self._save_to_jsonl(result)
                                print(f"    ✅ [{i+1}/{len(new_hits)}] {title[:25]} | JD校验通过")
                            else:
                                print(f"    [丢弃] 中性词无业务佐证: {title[:30]}")
                        else:
                            print(f"    [丢弃] 标题无经管词: {title[:30]}")
                    else:
                        print(f"    ⚠️ [{i+1}/{len(new_hits)}] 提取失败")
                except Exception as e:
                    print(f"    [异常] {e}")
                    # 异常时也清理标签页
                    try:
                        for t_id in set(self.page.tab_ids) - tabs_before:
                            self.page.get_tab(t_id).close()
                        self.page.to_tab(original_tab)
                    except Exception:
                        pass

                self._sleep(3, 8)

            # 向下滚动加载更多
            self._scroll_body(3)
            self._sleep(2, 4)

    # ============================================================
    # 文本模糊匹配：找到包含公司名的元素
    # ============================================================
    def _find_company_hits(self, company):
        """
        使用 DrissionPage 的 text: 模糊匹配
        找到页面中所有包含目标公司名的元素
        """
        hits = []
        try:
            # 方式 1: text: 模糊匹配
            elements = self.page.eles(f'text:{company}', timeout=3)
            if elements:
                hits = list(elements)
                print(f"    [文本匹配] text:{company} → {len(hits)} 个元素")
        except Exception:
            pass

        if not hits:
            # 方式 2: 用 tag:a 找包含公司名的链接
            try:
                all_a = self.page.eles('tag:a', timeout=2)
                for a in all_a:
                    try:
                        if a.text and company in a.text:
                            hits.append(a)
                    except Exception:
                        continue
                if hits:
                    print(f"    [链接匹配] <a> 含「{company}」→ {len(hits)} 个")
            except Exception:
                pass

        return hits

    # ============================================================
    # 点击 → sleep → 暴力提取（极简版）
    # ============================================================
    def _click_and_extract(self, hit_el, company, idx, total):
        data = {"company": company}

        # ---- 向上找到卡片容器 (tag:li) ----
        card = hit_el
        try:
            node = hit_el
            for _ in range(6):
                p = node.parent()
                if not p:
                    break
                node = p
                try:
                    if node.tag and node.tag.lower() == 'li':
                        card = node
                        break
                except Exception:
                    pass
        except Exception:
            pass

        # ---- 卡片基础信息 ----
        card_text = ""
        try:
            card_text = card.text or ""
        except Exception:
            pass

        data["title"] = self._extract_title_from_card(card)
        data["url"] = self._get_nearby_href(card)
        m = SALARY_RE.search(card_text)
        data["salary"] = m.group(0) if m else ""
        m = LOC_RE.search(card_text)
        data["location"] = m.group(1) if m else ""

        # ---- 记录卡片标题（用于对暗号） ----
        target_title = data.get("title", "").strip()

        # ---- JS 强制点击卡片 ----
        try:
            card.click(by_js=True)
        except Exception:
            return None

        # ============================================================
        # 标题对暗号：轮询右侧面板标题是否等于 target_title（5 秒超时）
        # ============================================================
        matched = False
        if target_title and len(target_title) >= 2:
            for _ in range(10):  # 10 × 0.5s = 5s
                time.sleep(0.5)
                try:
                    right_title_el = self.page.ele(f'text={target_title}', timeout=0.3)
                    if right_title_el:
                        matched = True
                        break
                except Exception:
                    continue
        else:
            # 没有标题可对，退化为硬等
            time.sleep(2)
            matched = True

        if not matched:
            print(f"    [超时] 右侧未刷新到「{target_title[:15]}」，跳过")
            return None

        # ============================================================
        # 缩窄提取：锚点 → .next() 兄弟节点 → .parent(1) → body 保底
        # ============================================================
        jd_text = ""
        for anchor in JD_ANCHORS:
            try:
                el = self.page.ele(f'text:{anchor}', timeout=1)
                if not el:
                    continue

                # 优先取下一个兄弟节点（正文通常紧跟在标题后）
                try:
                    sib = el.next()
                    if sib:
                        t = sib.text or ""
                        if len(t) > 50:
                            jd_text = t
                            break
                except Exception:
                    pass

                # 次选：最近 1 层 parent
                try:
                    t = el.parent().text or ""
                    if len(t) > 50:
                        jd_text = t
                        break
                except Exception:
                    pass

                # 再次选：2 层 parent
                try:
                    t = el.parent(2).text or ""
                    if len(t) > 50:
                        jd_text = t
                        break
                except Exception:
                    pass

            except Exception:
                continue

        # ---- 保底：body 全文截取 ----
        if not jd_text or len(jd_text) < 50:
            jd_text = self._extract_jd_from_body()

        # ---- 脏词清洗 ----
        jd_text = self._clean_jd(jd_text)

        data["jd_full_text"] = jd_text

        # ---- 从页面文本补充字段 ----
        page_text = jd_text
        if not data["salary"]:
            m = SALARY_RE.search(page_text)
            data["salary"] = m.group(0) if m else ""
        if not data["location"]:
            m = LOC_RE.search(page_text)
            data["location"] = m.group(1) if m else ""
        m = SIZE_RE.search(page_text)
        data["company_size"] = m.group(0) if m else ""
        data["education"] = ""
        for kw in ["博士", "硕士", "本科", "大专"]:
            if kw in page_text:
                data["education"] = kw
                break
        m = EXP_RE.search(page_text)
        data["experience"] = m.group(0) if m else ""
        data["industry"] = self._first_match(page_text[:2000],
            ["互联网", "金融", "医疗", "教育", "电商", "人工智能", "新能源", "汽车", "制造", "咨询", "半导体", "生物医药"])
        data["financing"] = self._first_match(page_text[:2000],
            ["已上市", "上市公司", "A轮", "B轮", "C轮", "D轮", "天使轮", "战略投资"])
        data["benefits"] = [kw for kw in
            ["五险一金", "餐补", "交通补贴", "弹性工作", "转正机会", "实习津贴"]
            if kw in page_text]

        if not data["title"]:
            data["title"] = (data["jd_full_text"] or "")[:30].split("\n")[0]

        return data if data.get("jd_full_text") and len(data["jd_full_text"]) > 30 else None

    # ============================================================
    # 脏词清洗
    # ============================================================
    @staticmethod
    def _clean_jd(raw):
        """去除 UI 杂音 + 压缩多余换行"""
        if not raw:
            return ""
        for dirty in ["举报", "微信扫码分享", "来自BOSS直聘", "kanzhun",
                       "去App", "与BOSS随时沟通", "前往App", "查看更多信息",
                       "BOSS直聘", "boss直聘", "boss", "直聘", "点击查看地图"]:
            raw = raw.replace(dirty, "")
        # 连续 3+ 换行 → 单换行
        raw = re.sub(r'\n{3,}', '\n', raw)
        # 连续空格
        raw = re.sub(r'[ \t]{3,}', ' ', raw)
        return raw.strip()

    # ============================================================
    # 文本锚点定位 JD：搜 "职位描述" → .parent() 上溯
    # ============================================================
    def _extract_jd_by_text_anchor(self):
        """
        在右侧面板中搜索 JD_ANCHORS 关键词（如"岗位职责"）
        找到后向上追溯 parent 取完整文本
        """
        for anchor in JD_ANCHORS:
            try:
                el = self.page.ele(f'text:{anchor}', timeout=1)
                if not el:
                    continue

                # 向上追溯 1~4 级 parent，找包含完整 JD 的容器
                best_text = ""
                node = el
                for level in range(5):
                    try:
                        node = node.parent()
                        if not node:
                            break
                        t = node.text
                        if t and len(t) > len(best_text):
                            best_text = t
                            # 如果已经很长，不需要继续往上
                            if len(best_text) > 200:
                                break
                    except Exception:
                        break

                if best_text and len(best_text) > 50:
                    print(f"    [JD锚点] 「{anchor}」→ {len(best_text)} 字")
                    return best_text.strip()

            except Exception:
                continue

        return ""

    # ============================================================
    # 保底：从 body 全文中截取 JD
    # ============================================================
    def _extract_jd_from_body(self):
        """
        保底方案：获取 body 全文，
        用正则截取从"职位描述/岗位职责"到之后 2000 字的内容
        """
        try:
            body = self.page.ele('tag:body')
            if not body:
                return ""
            full_text = body.text or ""

            # 尝试从锚点截取
            for anchor in JD_ANCHORS:
                pos = full_text.find(anchor)
                if pos >= 0:
                    jd = full_text[pos:pos + 3000]
                    if len(jd) > 50:
                        print(f"    [JD保底] body全文截取 → {len(jd)} 字")
                        return jd.strip()

            # 终极保底：取 body 中间部分（跳过导航头尾）
            if len(full_text) > 500:
                mid = full_text[200:3000]
                return mid.strip()

            return full_text.strip()

        except Exception:
            return ""

    # ============================================================
    # 从卡片中提取标题
    # ============================================================
    def _extract_title_from_card(self, card):
        """从卡片元素中提取职位名称"""
        # 尝试找 <a> 链接的文本（通常是职位名）
        try:
            link = card.ele('tag:a@href:/job_detail/', timeout=1)
            if link and link.text:
                return link.text.strip()
        except Exception:
            pass

        # 尝试找 h3/span 等
        for tag in ['tag:h3', 'tag:h2', 'tag:span']:
            try:
                el = card.ele(tag, timeout=1)
                if el and el.text and len(el.text.strip()) < 40:
                    return el.text.strip()
            except Exception:
                continue

        return ""

    # ============================================================
    # 提取附近的 href（用于去重和数据记录）
    # ============================================================
    def _get_nearby_href(self, el):
        """从元素自身或 parent 中提取 job_detail 链接"""
        for _ in range(4):
            try:
                href = el.attr('href')
                if href and '/job_detail/' in href:
                    if href.startswith('/'):
                        href = "https://www.zhipin.com" + href
                    return href.split('?')[0]

                # 找子 <a>
                a = el.ele('tag:a@href:/job_detail/', timeout=0.5)
                if a:
                    h = a.attr('href')
                    if h:
                        if h.startswith('/'):
                            h = "https://www.zhipin.com" + h
                        return h.split('?')[0]

                el = el.parent()
                if not el:
                    break
            except Exception:
                break
        return ""

    # ============================================================
    # 经管相关性检测
    # ============================================================
    def _check_relevance(self, detail):
        title = detail.get("title", "")
        jd = detail.get("jd_full_text", "")[:1500]
        combined = title + " " + jd

        best_dir, best_score = None, 0
        for _, dir_info in self.directions.items():
            score = sum(1 for kw in dir_info["keywords"] if kw in combined)
            if score > best_score:
                best_score = score
                best_dir = dir_info["direction"]

        if best_score >= 1:
            return best_dir

        for kw in ["采购", "供应链", "运营", "产品", "商业分析", "战略",
                    "金融", "投资", "咨询", "财务", "审计", "市场", "品牌",
                    "HR", "人力", "数据分析", "管培", "BD", "商务", "实习"]:
            if kw in title:
                return f"标题匹配:{kw}"
        return None

    # ============================================================
    # JSONL 原子化落盘
    # ============================================================
    def _save_to_jsonl(self, data_dict):
        try:
            uid = self._make_id(data_dict)
            if uid in self.seen_ids:
                return
            line = json.dumps(data_dict, ensure_ascii=False)
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
            self.seen_ids.add(uid)
            self.saved_count += 1
        except Exception as e:
            print(f"    [落盘错误] {e}")

    def _make_id(self, d):
        url = d.get("url", "")
        if url:
            return url
        raw = f"{d.get('company','')}|{d.get('title','')}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _load_existing_ids(self):
        if not os.path.exists(OUTPUT_FILE):
            return
        n = 0
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    self.seen_ids.add(self._make_id(obj))
                    n += 1
                except Exception:
                    continue
        if n:
            print(f"[断点续爬] 已有 {n} 条")

    # ============================================================
    # 辅助
    # ============================================================
    def _first_match(self, text, candidates):
        for kw in candidates:
            if kw in text:
                return kw
        return ""

    def _sleep(self, lo=3, hi=8):
        time.sleep(random.uniform(lo, hi))

    def _scroll_body(self, n=3):
        """直接对 body 发送 PAGE_DOWN，最简单最通用"""
        for _ in range(n):
            try:
                self.page.actions.key_down(Keys.PAGE_DOWN)
                time.sleep(random.uniform(0.5, 1.2))
            except Exception:
                try:
                    self.page.scroll.down(600)
                    time.sleep(random.uniform(0.5, 1.0))
                except Exception:
                    pass

    def _get_body_text(self):
        """获取 body 全文（用于 smart wait 对比）"""
        try:
            body = self.page.ele('tag:body')
            if body:
                return body.text or ""
        except Exception:
            pass
        return ""

# ============================================================
# 入口
# ============================================================
def main():
    mode = "test"
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    scraper = DrissionScraper()
    scraper.load_configs()
    scraper.start_browser()
    scraper.login_and_wait()

    if mode == "test":
        print("[模式] 🧪 测试 — 前 6 家公司")
        scraper.run_scraper(test_limit=6)
    elif mode == "full":
        print(f"[模式] 🔥 全量 — {len(scraper.target_companies)} 家")
        scraper.run_scraper()
    else:
        try:
            n = int(mode)
            print(f"[模式] 自定义 — 前 {n} 家")
            scraper.run_scraper(test_limit=n)
        except ValueError:
            print("用法: python jd_scraper.py [test|full|数字]")
            sys.exit(1)


if __name__ == "__main__":
    main()
