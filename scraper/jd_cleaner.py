"""
========================================
模块三：数据清洗、去重与本地落盘
========================================
功能：
  1. 正则清洗文本（去 HTML 标签、特殊字符、冗余换行）
  2. 基于"公司名称+岗位名称"生成 Hash 唯一键去重
  3. 结构化追加保存为 JSONL（JSON Lines）格式
  4. 支持后续 RAG 向量化 / 模型微调使用
========================================
"""

import hashlib
import json
import os
import re
from typing import Optional


# 输出目录
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 默认输出文件
DEFAULT_JSONL = os.path.join(DATA_DIR, "cleaned_jd.jsonl")
HASH_INDEX_FILE = os.path.join(DATA_DIR, "jd_hash_index.json")


# ============================================================
# 文本清洗函数
# ============================================================
def deep_clean_text(text: str) -> str:
    """
    深度清洗文本：
    1. 去除所有 HTML 标签
    2. 去除不可见 Unicode 字符（零宽空格、控制字符等）
    3. 合并连续空白和换行
    4. 去除首尾空白
    """
    if not text:
        return ""

    # 步骤1：去 HTML 标签
    clean = re.sub(r'<[^>]+>', ' ', text)

    # 步骤2：去不可见/特殊字符
    # 零宽空格 (U+200B), 零宽非断行空格 (U+FEFF),
    # 零宽连接符 (U+200D), 零宽非连接符 (U+200C)
    clean = re.sub(r'[\u200b\u200c\u200d\ufeff\u00a0]', '', clean)
    # 去控制字符（但保留换行 \n 和 tab \t）
    clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', clean)

    # 步骤3：规范化空白
    # 将 \r\n 统一为 \n
    clean = clean.replace('\r\n', '\n').replace('\r', '\n')
    # 行首尾空白
    lines = [line.strip() for line in clean.split('\n')]
    # 合并连续空行（最多保留1个空行）
    result_lines = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                result_lines.append("")
                prev_empty = True
        else:
            result_lines.append(line)
            prev_empty = False

    return '\n'.join(result_lines).strip()


def clean_company_name(name: str) -> str:
    """清洗公司名称：去除多余后缀、空白"""
    name = name.strip()
    # 去除常见后缀
    suffixes = ["有限公司", "股份有限公司", "有限责任公司", "集团", "（中国）", "(中国)"]
    clean_name = name
    for suffix in suffixes:
        clean_name = clean_name.replace(suffix, "").strip()
    return clean_name or name  # 如果清洗后为空，返回原名


# ============================================================
# 去重逻辑
# ============================================================
def generate_hash_key(company_name: str, job_title: str) -> str:
    """
    基于"公司名称+岗位名称"生成唯一 Hash 键。
    使用 MD5 作为快速 hash（此处不要求密码学安全性）。
    """
    # 规范化：去空白、转小写
    normalized = f"{company_name.strip().lower()}|{job_title.strip().lower()}"
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def load_hash_index(index_file: str = HASH_INDEX_FILE) -> set:
    """加载已有的 Hash 索引，用于去重"""
    if not os.path.exists(index_file):
        return set()
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except (json.JSONDecodeError, ValueError):
        return set()


def save_hash_index(hash_set: set, index_file: str = HASH_INDEX_FILE):
    """保存 Hash 索引到文件"""
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(list(hash_set), f, ensure_ascii=False)


# ============================================================
# 数据验证
# ============================================================
def validate_record(record: dict) -> bool:
    """
    验证清洗后的记录是否合格：
    - 必须有公司名称
    - 必须有岗位名称
    - JD 描述不能为空且长度 >= 20 字
    """
    company = record.get("company_info", {}).get("name", "")
    title = record.get("job_info", {}).get("title", "")
    desc = record.get("job_info", {}).get("description", "")

    if not company.strip():
        return False
    if not title.strip():
        return False
    if not desc.strip() or len(desc.strip()) < 20:
        return False
    return True


# ============================================================
# 核心处理流程
# ============================================================
def clean_and_store(
    parsed_records: list[dict],
    output_file: str = DEFAULT_JSONL,
    index_file: str = HASH_INDEX_FILE,
) -> dict:
    """
    清洗、去重、验证并追加保存到 JSONL。

    参数：
        parsed_records: parse_all() 输出的结构化数据列表
        output_file: JSONL 输出路径
        index_file: Hash 索引文件路径

    返回：
        {"total": int, "new": int, "duplicate": int, "invalid": int}
    """
    stats = {"total": len(parsed_records), "new": 0, "duplicate": 0, "invalid": 0}

    # 加载已有 Hash 索引
    hash_index = load_hash_index(index_file)
    initial_count = len(hash_index)

    # 追加模式打开 JSONL 文件
    with open(output_file, "a", encoding="utf-8") as f:
        for record in parsed_records:
            # === 步骤1：深度清洗文本字段 ===
            if "job_info" in record:
                record["job_info"]["description"] = deep_clean_text(
                    record["job_info"].get("description", "")
                )
                record["job_info"]["title"] = deep_clean_text(
                    record["job_info"].get("title", "")
                )
            if "company_info" in record:
                record["company_info"]["name"] = deep_clean_text(
                    record["company_info"].get("name", "")
                )

            # === 步骤2：验证 ===
            if not validate_record(record):
                stats["invalid"] += 1
                continue

            # === 步骤3：去重 ===
            company_name = record["company_info"]["name"]
            job_title = record["job_info"]["title"]
            hash_key = generate_hash_key(company_name, job_title)

            if hash_key in hash_index:
                stats["duplicate"] += 1
                continue

            # === 步骤4：追加写入 JSONL ===
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            hash_index.add(hash_key)
            stats["new"] += 1

    # 保存更新后的 Hash 索引
    save_hash_index(hash_index, index_file)

    print(f"\n[清洗结果]")
    print(f"  总计: {stats['total']} 条")
    print(f"  新增: {stats['new']} 条")
    print(f"  重复: {stats['duplicate']} 条（已跳过）")
    print(f"  无效: {stats['invalid']} 条（已跳过）")
    print(f"  Hash 索引: {initial_count} → {len(hash_index)} 条")
    print(f"  输出文件: {output_file}")

    return stats


# ============================================================
# 独立运行入口：处理已抓取的原始数据
# ============================================================
if __name__ == "__main__":
    from jd_parser import parse_all

    # 读取原始抓取数据
    raw_file = os.path.join(os.path.dirname(__file__), "raw_jd_data.json")
    if not os.path.exists(raw_file):
        print(f"[错误] 未找到原始数据文件: {raw_file}")
        print("请先运行 jd_scraper.py 抓取数据")
        exit(1)

    with open(raw_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"[读取] 加载 {len(raw_data)} 条原始数据")

    # 解析
    parsed = parse_all(raw_data)

    # 清洗 + 去重 + 存储
    stats = clean_and_store(parsed)
    print(f"\n[完成] 流水线执行结束")
