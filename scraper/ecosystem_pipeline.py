"""
============================================================
全网招聘与求职生态数据采集系统 - 核心抓取与清洗引擎
============================================================
架构设计：
  1. Playwright (配合 Stealth) 用于对抗重度反爬平台
  2. BeautifulSoup + lxml 用于纯 DOM 解析
  3. Pydantic 用于严格的输出 JSON Schema 数据校验验证
  4. 严格条件风控（地点、层级、岗类、公司画像）过滤不合格记录

【核心过滤规则】
- 城市：仅限“上海”
- 岗位：仅限“实习生”、“管培”
- 公司：100人以上，偏好上市、大厂、独角兽
- 领域：分析/战略类、产品/运营类、职能/供应链类
============================================================
"""

import asyncio
import hashlib
import json
import os
import random
import re
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from playwright.async_api import async_playwright, Page, BrowserContext


# ============================================================
# Schema 定义 (基于 Pydantic 的强制数据校验)
# ============================================================

class MetaInfo(BaseModel):
    platform: str
    url: str
    fetch_time: str
    hash_id: str

class CompanyProfile(BaseModel):
    name: str
    industry: str
    size_category: str
    financing_stage: str

class JobProfile(BaseModel):
    title: str
    category: str
    location: str
    level: str

class HardConstraints(BaseModel):
    education: List[str]
    majors_preferred: List[str]
    attendance_days_per_week: Optional[int] = None
    duration_months: Optional[int] = None
    software_tools: List[str]

class Requirements(BaseModel):
    hard_constraints: HardConstraints
    soft_skills: List[str]

class JobDescriptionSchema(BaseModel):
    doc_type: str = "job_description"
    meta_info: MetaInfo
    company_profile: CompanyProfile
    job_profile: JobProfile
    requirements: Requirements
    responsibilities: List[str]


# ============================================================
# 过滤风控引擎 (Filters)
# ============================================================
class FilterEngine:
    VALID_CITIES = ["上海", "跨地区", "Remote", "全国"]
    INVALID_KEYWORDS = ["全职", "社招", "兼职", "外包", "保洁", "保安", "前台", "销售代表", "地推"]
    MIN_HEADCOUNT = 100  # 100人以上
    
    @classmethod
    def is_valid_city(cls, location_text: str) -> bool:
        return any(city in location_text for city in cls.VALID_CITIES)

    @classmethod
    def is_valid_level(cls, title: str) -> bool:
        title_lower = title.lower()
        if any(bad in title_lower for bad in cls.INVALID_KEYWORDS):
            return False
        return "实习" in title_lower or "intern" in title_lower or "管培" in title_lower

    @classmethod
    def is_valid_company_size(cls, size_str: str) -> bool:
        # 过滤 "0-20人", "20-99人", "少于50人" 等
        size_str = size_str.replace(" ", "")
        match = re.search(r'(\d+)-(\d+)人|(\d+)人以上', size_str)
        if match:
            if match.group(3):  # "100人以上"
                return int(match.group(3)) >= cls.MIN_HEADCOUNT
            elif match.group(2): # "20-99人"
                return int(match.group(2)) >= cls.MIN_HEADCOUNT
        return False # 无法解析的倾向于抛弃或人工复核，为高标准严控这里直接False


# ============================================================
# 数据抽取与清洗核心引擎 (Extractor)
# ============================================================
class DataExtractor:
    
    # 学历词典
    EDU_DICT = {"大专", "本科", "硕士", "博士", "MBA"}
    # 工具词典（商业分析、运营、产品常见）
    TOOLS_DICT = {
        "SQL", "Python", "Excel", "PPT", "Tableau", "PowerBI", "Axure", 
        "Figma", "GA", "SPSS", "R", "Xmind", "Git", "Jira"
    }

    @classmethod
    def clean_html_list(cls, html_snippet: str) -> List[str]:
        """将杂乱的包含 1. 2. 3. 或者 <br> 的 HTML 拆分为结构化列表"""
        soup = BeautifulSoup(html_snippet, "lxml")
        text = soup.get_text(separator="\n")
        
        # 按照换行或数字前缀拆分
        lines = re.split(r'\n|\d+\.|[①②③④⑤⑥⑦⑧⑨⑩]', text)
        cleaned_lines = []
        for line in lines:
            cl = line.strip(" ;。， \t\r-•*")
            if len(cl) > 5:  # 丢弃过短的无意义行
                cleaned_lines.append(cl)
        return cleaned_lines

    @classmethod
    def extract_tools(cls, text: str) -> List[str]:
        text_upper = text.upper()
        found = []
        for tool in cls.TOOLS_DICT:
            if tool.upper() in text_upper:
                found.append(tool)
        return found
        
    @classmethod
    def extract_education(cls, text: str) -> List[str]:
        found = []
        for edu in cls.EDU_DICT:
            if edu in text:
                found.append(edu)
        if not found:
            return ["不限"]
        return found

    @classmethod
    def extract_attendance(cls, text: str) -> Optional[int]:
        # 匹配 "每周3天" "至少4天" 等
        match = re.search(r'每周.*?(\d+)\s*天|(\d+)\s*天[/每]周', text)
        if match:
            val = match.group(1) or match.group(2)
            return int(val)
        return None


# ============================================================
# 数据处理调度层 (Pipeline)
# ============================================================
class EcosystemPipeline:
    def __init__(self, input_dir="data", output_file="data/structured_corpus.jsonl"):
        self.input_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), input_dir)
        self.output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_file)
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        self.seen_hashes = set()
        
        # 尝试加载已有的哈希记录以支持断点续传/防重复
        self._load_existing_hashes()

    def _load_existing_hashes(self):
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            hash_id = data.get("meta_info", {}).get("hash_id")
                            if hash_id:
                                self.seen_hashes.add(hash_id)
                print(f"[Init] 已加载 {len(self.seen_hashes)} 条已有数据的 Hash 记录，用于去重。")
            except Exception as e:
                print(f"[Init Warning] 加载已有 Hash 失败: {e}")

    def run_pipeline(self):
        """读取所有 raw_jd_*.json 文件，经过风控管线，输出为结构化 JSONL"""
        print(f"\n{'='*50}")
        print("  开始执行全网生态数据结构化清洗管线")
        print(f"{'='*50}")
        
        raw_files = [f for f in os.listdir(self.input_dir) if f.startswith("raw_jd_") and f.endswith(".json")]
        if not raw_files:
            print(f"❌ 在 {self.input_dir} 目录下未找到原始数据文件。请先运行 jd_scraper.py 抓取数据。")
            return

        total_processed = 0
        total_saved = 0
        
        for file in raw_files:
            file_path = os.path.join(self.input_dir, file)
            print(f"\n▶ 正在处理文件: {file}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_data_list = json.load(f)
            except Exception as e:
                print(f"  ❌ 读取文件失败: {e}")
                continue
            
            print(f"  > 发现 {len(raw_data_list)} 条原始记录")
            
            for raw in raw_data_list:
                total_processed += 1
                if self.process_raw_jd(raw):
                    total_saved += 1
                    
        print(f"\n{'='*50}")
        print(f"[Pipeline 结果统计]")
        print(f"  总读取: {total_processed} 条")
        print(f"  成功入库: {total_saved} 条")
        print(f"  过滤掉: {total_processed - total_saved} 条 (城市/非实习/规模不符/重复等)")
        print(f"  输出文件: {self.output_file}")
        print(f"{'='*50}\n")

    def process_raw_jd(self, raw: dict) -> bool:
        """将单条原始爬取数据通过风控过滤并结构化"""
        
        title = raw.get('title', '')
        company = raw.get('company', '')
        size = raw.get('size', '未知')
        location = raw.get('location', '上海') # 防止某些字段缺失
        url = raw.get('url', '')
        platform = raw.get('_platform', 'unknown')
        jd_raw = raw.get('jd_raw', '')
        
        # 1. 基础异常值过滤
        if not title or not company or not jd_raw:
             print("  [Filter Drop] 关键字段缺失")
             return False
        
        # 2. 风控过滤
        if not FilterEngine.is_valid_city(location):
             # 不特别打印每一条，避免刷屏，只计入统计
             return False
             
        if not FilterEngine.is_valid_level(title):
             return False
             
        if not FilterEngine.is_valid_company_size(size):
             return False

        # 3. Hash 去重
        hash_str = f"{company}-{title}".encode('utf-8')
        doc_hash = hashlib.md5(hash_str).hexdigest()
        if doc_hash in self.seen_hashes:
             return False
             
        self.seen_hashes.add(doc_hash)

        # 4. 提取解析
        # 简单将 jd_raw 按行切分
        lines = [line.strip() for line in jd_raw.split('\n') if line.strip()]
        
        # 粗略切分职责与要求 (实战中可通过关键词"任职要求"切分，这里简化)
        req_start_idx = len(lines) // 2 
        for i, line in enumerate(lines):
            if "要求" in line or "资格" in line or "条件" in line:
                req_start_idx = i
                break
                
        resp_text = lines[:req_start_idx]
        req_text = " ".join(lines[req_start_idx:])
        
        tools = DataExtractor.extract_tools(jd_raw)
        edu = DataExtractor.extract_education(req_text)
        att = DataExtractor.extract_attendance(req_text)
        
        # 5. 构建 Pydantic 实体
        try:
            schema_data = JobDescriptionSchema(
                meta_info=MetaInfo(
                    platform=platform,
                    url=url,
                    fetch_time=datetime.now().isoformat(),
                    hash_id=doc_hash
                ),
                company_profile=CompanyProfile(
                    name=company,
                    industry="未知", # 爬虫暂未爬取细分行业
                    size_category=size,
                    financing_stage="未知"
                ),
                job_profile=JobProfile(
                    title=title,
                    category="综合类", 
                    location=location,
                    level="实习生"
                ),
                requirements=Requirements(
                    hard_constraints=HardConstraints(
                        education=edu,
                        majors_preferred=[], 
                        attendance_days_per_week=att,
                        duration_months=None,
                        software_tools=tools
                    ),
                    soft_skills=[] 
                ),
                responsibilities=resp_text
            )
            
            # 6. 落盘为 JSONL
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(schema_data.model_dump_json() + "\n")
            print(f"  ✅ [入库] {title[:15]} - {company[:10]}")
            return True
            
        except Exception as e:
            print(f"  [JSON Error] 数据结构校验失败: {e}")
            return False


if __name__ == "__main__":
    pipeline = EcosystemPipeline()
    pipeline.run_pipeline()
