"""
========================================
历史记录管理模块
========================================
功能:
  1. 保存每次诊断的记录（简历文本、JD、诊断结果、时间戳）
  2. 读取历史记录列表
  3. 查看单条历史详情
  4. 保存聊天对话记录
========================================
"""

import json
import os
from datetime import datetime

# 历史记录存储目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "diagnosis_history.json")
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")


def _ensure_data_dir():
    """确保 data 目录存在"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def save_diagnosis_record(filename, resume_text, jd_text, diagnosis_result, format_issues, industry_insights=""):
    """
    保存一条诊断记录。
    
    参数:
        filename (str): 上传的简历文件名
        resume_text (str): 提取的简历文本
        jd_text (str): 目标岗位 JD
        diagnosis_result (dict): AI 诊断结果
        format_issues (list): 格式体检结果
        industry_insights (str): 全网行业情报
    """
    _ensure_data_dir()
    
    # 读取现有记录
    records = load_all_diagnosis_records()
    
    # 创建新记录
    new_record = {
        "id": len(records) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "resume_text": resume_text,
        "jd_text": jd_text,
        "diagnosis_result": diagnosis_result,
        "format_issues": format_issues,
        "industry_insights": industry_insights,
        "overall_score": diagnosis_result.get("data", {}).get("overall_score", 0) if diagnosis_result.get("success") else 0,
    }
    
    # 添加到列表头部（最新的在前面）
    records.insert(0, new_record)
    
    # 写入文件
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def load_all_diagnosis_records():
    """
    读取所有诊断历史记录。
    
    返回:
        list[dict]: 记录列表，最新的在前面
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def delete_diagnosis_record(record_id):
    """
    删除指定 ID 的诊断记录。
    
    参数:
        record_id (int): 要删除的记录 ID
    """
    records = load_all_diagnosis_records()
    records = [r for r in records if r.get("id") != record_id]
    
    _ensure_data_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# ============================================================
# 聊天记录管理
# ============================================================

def save_chat_session(session_id, messages, title=""):
    """
    保存一次聊天会话。
    
    参数:
        session_id (str): 会话 ID
        messages (list): 消息列表
        title (str): 会话标题
    """
    _ensure_data_dir()
    
    sessions = load_all_chat_sessions()
    
    # 查找是否已存在该会话
    found = False
    for i, session in enumerate(sessions):
        if session.get("session_id") == session_id:
            sessions[i]["messages"] = messages
            sessions[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if title:
                sessions[i]["title"] = title
            found = True
            break
    
    if not found:
        # 自动生成标题：取第一条用户消息的前 20 个字
        if not title and messages:
            for msg in messages:
                if msg.get("role") == "user":
                    title = msg["content"][:20] + ("..." if len(msg["content"]) > 20 else "")
                    break
        
        sessions.insert(0, {
            "session_id": session_id,
            "title": title or "新对话",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "messages": messages,
        })
    
    
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def load_all_chat_sessions():
    """
    读取所有聊天会话列表。
    
    返回:
        list[dict]: 会话列表
    """
    if not os.path.exists(CHAT_HISTORY_FILE):
        return []
    
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def load_chat_session(session_id):
    """
    读取指定会话的消息记录。
    
    参数:
        session_id (str): 会话 ID
    
    返回:
        list: 消息列表，如果不存在返回空列表
    """
    sessions = load_all_chat_sessions()
    for session in sessions:
        if session.get("session_id") == session_id:
            return session.get("messages", [])
    return []


def delete_chat_session(session_id):
    """
    删除指定的聊天会话。
    
    参数:
        session_id (str): 要删除的会话 ID
    """
    sessions = load_all_chat_sessions()
    sessions = [s for s in sessions if s.get("session_id") != session_id]
    
    _ensure_data_dir()
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def update_diagnosis_record_with_improved_resume(filename, improved_text):
    """
    将优化后的简历文本追加保存到最近一条匹配的诊断记录中。

    参数:
        filename (str): 简历文件名（用于匹配记录）
        improved_text (str): 优化后的简历文本
    """
    records = load_all_diagnosis_records()

    # 找到最新（列表中最靠前）的匹配记录
    for record in records:
        if record.get("filename") == filename:
            record["improved_resume"] = improved_text
            break
    else:
        # 如果没有匹配，存到第一条
        if records:
            records[0]["improved_resume"] = improved_text

    _ensure_data_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
