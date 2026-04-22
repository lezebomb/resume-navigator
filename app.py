"""
========================================
ATS 简历智能诊断应用 - 主界面 v3.2
========================================
"""

import streamlit as st
import uuid
import io
import re
from utils.parser import extract_text_from_pdf, extract_text_from_docx, check_format_issues
from utils.ai_analyzer import analyze_resume, generate_improved_resume
from utils.search_agent import run_research_agent
from utils.history import (
    save_diagnosis_record, load_all_diagnosis_records, delete_diagnosis_record,
    save_chat_session, load_all_chat_sessions, load_chat_session, delete_chat_session,
    update_diagnosis_record_with_improved_resume,
)
from utils.chat import chat_with_consultant
from google import genai

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="ATS 简历智能诊断",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def clean_markdown(text):
    """移除文本中的 Markdown 符号"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **加粗**
    text = re.sub(r'\*(.+?)\*', r'\1', text)       # *斜体*
    text = text.replace("## ", "").replace("### ", "").replace("# ", "")
    text = re.sub(r'^- ', '• ', text, flags=re.MULTILINE)
    text = text.replace("```", "")
    return text


def extract_context_from_jd(jd_text, api_key):
    """
    从 JD 文本中提取公司名称、岗位名称和行业关键词。
    返回 dict: {"company_name": ..., "job_title": ..., "industry_keywords": ...}
    """
    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "请从以下 JD 中提取三个信息，以 JSON 格式返回（不要输出其他内容）：\n"
                '{"company_name": "公司名称", "job_title": "岗位名称", "industry_keywords": "行业/赛道关键词"}\n'
                "规则：\n"
                "- 如果 JD 中没写明公司名称，company_name 返回 \"该类公司\"\n"
                "- industry_keywords 是该公司所属的行业/赛道描述，例如：\"快消品/日化外企\" \"互联网大厂\" \"新能源汽车\" \"四大会计师事务所\" 等\n"
                "- 如果无法判断行业，industry_keywords 返回 \"综合企业\"\n\n"
                f"{jd_text[:800]}"
            ),
        )
        import json as _json
        text = (resp.text or "").strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = _json.loads(text)
        return {
            "company_name": result.get("company_name", "该类公司")[:30],
            "job_title": result.get("job_title", jd_text.strip()[:15])[:30],
            "industry_keywords": result.get("industry_keywords", "综合企业")[:40],
        }
    except Exception:
        pass

    first_line = jd_text.strip().split("\n")[0].strip()
    return {
        "company_name": "该类公司",
        "job_title": first_line[:20] if len(first_line) < 30 else jd_text.strip()[:15],
        "industry_keywords": "综合企业",
    }


# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
    html, body { font-family: 'Noto Sans SC', sans-serif; }

    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], #MainMenu, footer, .stDeployButton {
        display: none !important; visibility: hidden !important;
    }
    .viewerBadge_container__r5tak { display: none !important; }



    .main-title {
        text-align: center; padding: 1rem 0 0.3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2.2rem; font-weight: 700; letter-spacing: 2px;
    }
    .sub-title { text-align: center; color: #888; font-size: 1rem; margin-bottom: 1.5rem; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important; border: none; padding: 0.6rem 1.5rem;
        font-size: 1rem; font-weight: 600; border-radius: 12px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(102,126,234,0.4); }

    .info-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
        padding: 1.5rem; border-radius: 16px; margin: 1rem 0;
        border-left: 5px solid #667eea; color: #e0e0e0 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .info-card h3 { color: #fff !important; }
    .info-card p { color: #c0c0d0 !important; }

    .score-big { text-align: center; font-size: 4rem; font-weight: 700; margin: 0.5rem 0; }
    .score-label { text-align: center; font-size: 1rem; color: #aaa; }
    .tag-match {
        display: inline-block; background: rgba(39,174,96,0.15); color: #27ae60;
        padding: 0.2rem 0.7rem; border-radius: 8px; margin: 0.2rem;
        font-size: 0.85rem; border: 1px solid rgba(39,174,96,0.3);
    }
    .tag-miss {
        display: inline-block; background: rgba(231,76,60,0.15); color: #e74c3c;
        padding: 0.2rem 0.7rem; border-radius: 8px; margin: 0.2rem;
        font-size: 0.85rem; border: 1px solid rgba(231,76,60,0.3);
    }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 0.7rem 1.5rem; border-radius: 10px 10px 0 0; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 共用函数：渲染完整诊断
# ============================================================
def render_full_diagnosis(data):
    overall_score = data.get("overall_score", 0)
    if overall_score >= 90: score_color = "#27ae60"
    elif overall_score >= 75: score_color = "#f39c12"
    elif overall_score >= 60: score_color = "#e67e22"
    else: score_color = "#e74c3c"

    st.markdown(f'<div class="score-big" style="color:{score_color}">{overall_score}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="score-label">{data.get("overall_comment", "")}</div>', unsafe_allow_html=True)
    st.markdown("---")

    dim_names = {
        "hard_skills": "🎯 硬技能匹配", "soft_skills": "🧠 软技能分析",
        "quantification": "📊 量化指标", "anti_cheating": "🛡️ 反作弊检测",
        "keyword_density": "🔑 关键词密度",
    }
    for key, label in dim_names.items():
        dim_data = data.get(key, {})
        dim_score = dim_data.get("score", "N/A")
        st.markdown(f"**{label} — 得分: {dim_score}/100**")

        if key == "hard_skills":
            matched = dim_data.get("matched", [])
            missing = dim_data.get("missing", [])
            if matched:
                tags = "".join([f'<span class="tag-match">{s}</span>' for s in matched])
                st.markdown(f"✅ 已匹配: {tags}", unsafe_allow_html=True)
            if missing:
                tags = "".join([f'<span class="tag-miss">{s}</span>' for s in missing])
                st.markdown(f"❌ 缺失: {tags}", unsafe_allow_html=True)

        if key == "soft_skills":
            matched_soft = dim_data.get("matched", [])
            if matched_soft:
                for item in matched_soft:
                    if isinstance(item, dict):
                        st.markdown(f"  ✅ {item.get('jd_skill', '')} → _{item.get('resume_evidence', '')}_")
                    else:
                        st.markdown(f"  ✅ {item}")
            missing_soft = dim_data.get("missing", [])
            if missing_soft:
                tags = "".join([f'<span class="tag-miss">{s}</span>' for s in missing_soft])
                st.markdown(f"❌ 缺失: {tags}", unsafe_allow_html=True)

        if key == "quantification":
            good = dim_data.get("good_examples", [])
            if good:
                st.markdown("**✅ 好的量化表达:**")
                for g in good:
                    st.markdown(f"  - {g}")
            needs = dim_data.get("needs_improvement", [])
            if needs:
                st.markdown("**⚠️ 需要改进:**")
                for n in needs:
                    if isinstance(n, dict):
                        st.markdown(f"  - ❌ 原文: _{n.get('original', '')}_")
                        st.markdown(f"  - ✅ 建议: **{n.get('improved', '')}**")
                    else:
                        st.markdown(f"  - {n}")

        if key == "anti_cheating":
            issues = dim_data.get("issues", [])
            for iss in issues:
                st.warning(f"⚠️ {iss}")

        if key == "keyword_density":
            hf = dim_data.get("high_frequency_jd_keywords", [])
            if hf:
                kw_tags = "".join([f'<span class="tag-match">{k}</span>' for k in hf])
                st.markdown(f"**JD 高频词:** {kw_tags}", unsafe_allow_html=True)
            cov = dim_data.get("resume_keyword_coverage", "")
            if cov:
                st.markdown(f"**覆盖率:** {cov}")

        suggestion = dim_data.get("suggestion", "")
        if suggestion:
            st.info(f"💡 {suggestion}")
        st.markdown("")

    exp_data = data.get("expansion_suggestions", {})
    if exp_data:
        st.markdown("**🚀 拓展建议**")
        for k, lbl in [("certificates", "📜 推荐证书"), ("experiences", "💼 建议经历"), ("skills_to_learn", "📚 建议技能")]:
            items = exp_data.get(k, [])
            if items:
                st.markdown(f"**{lbl}:**")
                for it in items:
                    st.markdown(f"- {it}")
        if exp_data.get("suggestion"):
            st.info(f"💡 {exp_data['suggestion']}")


# ============================================================
# 共用函数：下载按钮
# ============================================================
def render_download_buttons(text_content, key_prefix="dl"):
    dl1, dl2 = st.columns(2)
    with dl1:
        try:
            from docx import Document as DocxDoc
            doc = DocxDoc()
            # 设置默认字体为宋体
            from docx.shared import Pt
            style = doc.styles['Normal']
            style.font.name = '宋体'
            style.font.size = Pt(11)
            style.font.color.rgb = None  # 黑色

            for line in text_content.split("\n"):
                line = line.strip()
                if not line:
                    continue
                doc.add_paragraph(line)
            buf = io.BytesIO()
            doc.save(buf)
            buf.seek(0)
            st.download_button(
                "💾 下载 Word (.docx)", data=buf.getvalue(),
                file_name="优化简历.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True, key=f"{key_prefix}_docx",
            )
        except Exception as e:
            st.warning(f"Word 生成失败: {e}")

    with dl2:
        try:
            from fpdf import FPDF
            import os

            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # 尝试多个中文字体路径
            font_loaded = False
            windir = os.environ.get("WINDIR", r"C:\Windows")
            font_candidates = [
                os.path.join(windir, "Fonts", "simsun.ttc"),   # 宋体
                os.path.join(windir, "Fonts", "msyh.ttc"),     # 微软雅黑
                os.path.join(windir, "Fonts", "simhei.ttf"),   # 黑体
                os.path.join(windir, "Fonts", "msyhbd.ttc"),   # 微软雅黑粗体
            ]
            for fp in font_candidates:
                if os.path.exists(fp):
                    try:
                        pdf.add_font("zhfont", "", fp, uni=True)
                        pdf.set_font("zhfont", size=11)
                        font_loaded = True
                        break
                    except Exception:
                        continue

            if not font_loaded:
                pdf.set_font("Helvetica", size=11)

            # 写入内容，控制行宽避免溢出
            page_width = pdf.w - pdf.l_margin - pdf.r_margin
            for line in text_content.split("\n"):
                line = line.strip()
                if not line:
                    pdf.ln(4)
                    continue
                pdf.multi_cell(page_width, 7, line)

            pdf_buf = io.BytesIO(pdf.output())
            st.download_button(
                "📄 下载 PDF (.pdf)", data=pdf_buf.getvalue(),
                file_name="优化简历.pdf", mime="application/pdf",
                use_container_width=True, key=f"{key_prefix}_pdf",
            )
        except Exception as e:
            st.warning(f"PDF 生成失败: {e}")


# ============================================================
# API Key
# ============================================================
api_col1, api_col2 = st.columns(2)
with api_col1:
    api_key_input = st.text_input(
        "🔑 请输入 Gemini API Key (必填)", type="password",
        placeholder="🔑 请输入 Gemini API Key (必填)",
        key="api_key_input", label_visibility="collapsed",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input
with api_col2:
    tavily_key_input = st.text_input(
        "🔍 请输入 Tavily API Key (必填)",
        type="password",
        placeholder="🔍 请输入 Tavily API Key (必填)",
        key="tavily_api_key_input",
        label_visibility="collapsed",
    )
    if tavily_key_input:
        st.session_state["tavily_api_key"] = tavily_key_input
st.markdown('<h1 class="main-title">🎯 ATS 简历智能诊断系统</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">基于 AI 大模型 · 六维精准诊断 · 专业咨询对话 · 一键优化下载</p>', unsafe_allow_html=True)

tab_diagnosis, tab_chat, tab_history = st.tabs(["📊 简历诊断", "💬 AI 咨询师", "📁 历史记录"])


# ============================================================
# TAB 1: 简历诊断
# ============================================================
with tab_diagnosis:
    # ---- 输入区域（垂直排列，占满屏宽） ----
    st.markdown("### 📤 上传简历")
    uploaded_file = st.file_uploader("选择简历", type=["pdf", "docx"], key="resume_upload")
    st.markdown("### 📋 粘贴目标岗位 JD")
    jd_text = st.text_area("粘贴JD", height=200, placeholder="粘贴招聘要求...", key="jd_input_main")
    start_btn = st.button("🚀 开始智能诊断", use_container_width=True, key="start_diag")

    st.markdown("---")

    # ---- 诊断执行逻辑 ----
    if start_btn:
        if not st.session_state.get("api_key"):
            st.error("🔑 请在顶部输入 Gemini API Key！")
        elif not st.session_state.get("tavily_api_key"):
            st.error("🔍 请在顶部输入 Tavily API Key！")
        elif not uploaded_file:
            st.warning("⚠️ 请先上传简历文件！")
        elif not jd_text.strip():
            st.warning("⚠️ 请先粘贴 JD 信息！")
        else:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            with st.spinner("📖 正在解析简历..."):
                resume_text = extract_text_from_pdf(uploaded_file) if file_ext == "pdf" else extract_text_from_docx(uploaded_file)
            if not resume_text.strip():
                st.error("❌ 无法提取文字！")
            else:
                with st.spinner("🔍 格式体检中..."):
                    format_issues = check_format_issues(uploaded_file, file_ext)

                with st.spinner("🏢 正在识别目标公司与岗位..."):
                    jd_context = extract_context_from_jd(
                        jd_text,
                        st.session_state["api_key"],
                    )
                    company_name = jd_context["company_name"]
                    job_title = jd_context["job_title"]
                    industry_keywords = jd_context["industry_keywords"]

                with st.spinner(f"🕵️‍♂️ 正在全网检索【{company_name} × {job_title}】的淘汰红线与面经..."):
                    insights = run_research_agent(
                        company_name,
                        industry_keywords,
                        job_title,
                        st.session_state["api_key"],
                        st.session_state["tavily_api_key"],
                    )
                st.session_state["industry_insights"] = insights
                st.session_state["industry_job_title"] = job_title
                st.session_state["industry_company"] = company_name

                with st.spinner("🧠 AI 深度分析中（约15~30秒）..."):
                    result = analyze_resume(
                        resume_text,
                        jd_text,
                        insights,
                        st.session_state["api_key"],
                    )
                if result["success"]:
                    st.session_state["last_diagnosis"] = {
                        "data": result["data"], "resume_text": resume_text,
                        "jd_text": jd_text, "format_issues": format_issues,
                        "filename": uploaded_file.name,
                    }
                    st.session_state["improved_resume"] = None
                    save_diagnosis_record(uploaded_file.name, resume_text, jd_text, result, format_issues, insights)
                else:
                    st.error(f"❌ 诊断失败: {result.get('error', '未知错误')}")

    # ---- 结果展示（占满屏宽） ----
    if st.session_state.get("last_diagnosis"):
        diag = st.session_state["last_diagnosis"]

        st.markdown("### 🔍 格式体检")
        for issue in diag["format_issues"]:
            if issue["level"] == "error": st.error(issue["message"])
            elif issue["level"] == "warning": st.warning(issue["message"])
            else: st.success(issue["message"])

        if st.session_state.get("industry_insights"):
            company_label = st.session_state.get("industry_company", "")
            job_label = st.session_state.get("industry_job_title", "该岗位")
            expander_title = f"📚 查看【{company_label} × {job_label}】的专属面经与机筛红线" if company_label else f"📚 查看【{job_label}】的全网真实面经与机筛红线"
            with st.expander(expander_title, expanded=False):
                st.markdown(st.session_state["industry_insights"])

        st.markdown("### 📊 AI 诊断报告")
        render_full_diagnosis(diag["data"])

        st.markdown("---")
        st.markdown("### ✨ AI 简历优化与下载")
        if st.button("🪄 一键生成优化简历", key="gen_improved_btn", use_container_width=True):
            with st.spinner("✨ AI 正在为你重写简历..."):
                improved_result = generate_improved_resume(
                    diag["resume_text"],
                    diag["jd_text"],
                    st.session_state["api_key"],
                )
            if improved_result["success"]:
                cleaned = clean_markdown(improved_result["improved_text"])
                st.session_state["improved_resume"] = cleaned
                update_diagnosis_record_with_improved_resume(diag["filename"], cleaned)
            else:
                st.error(f"❌ 优化失败: {improved_result.get('error')}")

        if st.session_state.get("improved_resume"):
            st.markdown("#### 左：原始简历 | 右：AI 优化版（可编辑）")
            cmp_l, cmp_r = st.columns(2)
            with cmp_l:
                st.markdown("**📄 原始简历**")
                st.text_area("原始", diag["resume_text"], height=600, disabled=True,
                             key="orig_disp_main", label_visibility="collapsed")
            with cmp_r:
                st.markdown("**✨ AI 优化版（可自行修改）**")
                edited_resume = st.text_area("优化版", st.session_state["improved_resume"],
                                              height=600, key="edit_disp_main", label_visibility="collapsed")

            st.markdown("#### 📥 一键下载（无水印，黑色宋体）")
            render_download_buttons(edited_resume, "diag_main")

    elif not start_btn:
        st.markdown("### 👋 欢迎使用 ATS 简历智能诊断")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="info-card"><h3>📤 上传简历</h3><p>支持 PDF 和 Word</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="info-card"><h3>📋 粘贴 JD</h3><p>粘贴招聘要求</p></div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="info-card"><h3>🎯 获取报告</h3><p>AI 六维深度剖析</p></div>', unsafe_allow_html=True)


# ============================================================
# TAB 2: AI 咨询师
# ============================================================
with tab_chat:
    if "current_chat_id" not in st.session_state:
        st.session_state["current_chat_id"] = None
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    if "editing_chat_id" not in st.session_state:
        st.session_state["editing_chat_id"] = None
    if "chat_file_text" not in st.session_state:
        st.session_state["chat_file_text"] = None

    chat_left, chat_right = st.columns([1, 3])

    with chat_left:
        st.markdown("### 💬 对话列表")

        if st.button("➕ 新建对话", use_container_width=True, key="new_chat_btn"):
            st.session_state["current_chat_id"] = str(uuid.uuid4())[:8]
            st.session_state["chat_messages"] = []
            st.session_state["editing_chat_id"] = None
            st.rerun()

        st.markdown("---")

        chat_sessions = load_all_chat_sessions()
        if chat_sessions:
            for si, session in enumerate(chat_sessions):
                sid = session.get("session_id", "")
                title = session.get("title", "新对话")

                if st.session_state.get("editing_chat_id") == sid:
                    new_title = st.text_input("名称", value=title, key=f"rn_{si}", label_visibility="collapsed")
                    r1, r2 = st.columns(2)
                    with r1:
                        if st.button("✅", key=f"sr_{si}"):
                            save_chat_session(sid, load_chat_session(sid), title=new_title)
                            st.session_state["editing_chat_id"] = None
                            st.rerun()
                    with r2:
                        if st.button("❌", key=f"cr_{si}"):
                            st.session_state["editing_chat_id"] = None
                            st.rerun()
                else:
                    c1, c2, c3 = st.columns([5, 1, 1])
                    with c1:
                        if st.button(f"💬 {title}", key=f"ld_{si}", use_container_width=True):
                            st.session_state["current_chat_id"] = sid
                            st.session_state["chat_messages"] = load_chat_session(sid)
                            st.rerun()
                    with c2:
                        if st.button("✏️", key=f"ed_{si}"):
                            st.session_state["editing_chat_id"] = sid
                            st.rerun()
                    with c3:
                        cfk = f"cdc_{si}"
                        if st.session_state.get(cfk):
                            pass
                        else:
                            if st.button("🗑️", key=f"dl_{si}"):
                                st.session_state[cfk] = True
                                st.rerun()

                    cfk = f"cdc_{si}"
                    if st.session_state.get(cfk):
                        st.warning(f"删除「{title}」？")
                        y, n = st.columns(2)
                        with y:
                            if st.button("是", key=f"ydc_{si}"):
                                delete_chat_session(sid)
                                st.session_state[cfk] = False
                                if st.session_state.get("current_chat_id") == sid:
                                    st.session_state["current_chat_id"] = None
                                    st.session_state["chat_messages"] = []
                                st.rerun()
                        with n:
                            if st.button("否", key=f"ndc_{si}"):
                                st.session_state[cfk] = False
                                st.rerun()
        else:
            st.caption("暂无对话记录")

        # 文件上传
        st.markdown("---")
        st.markdown("##### 📎 上传文件")
        chat_file = st.file_uploader("上传", type=["pdf", "docx", "txt"], key="chat_file_up", label_visibility="collapsed")
        if chat_file:
            ext = chat_file.name.split(".")[-1].lower()
            if ext == "pdf":
                st.session_state["chat_file_text"] = extract_text_from_pdf(chat_file)
            elif ext == "docx":
                st.session_state["chat_file_text"] = extract_text_from_docx(chat_file)
            else:
                st.session_state["chat_file_text"] = chat_file.read().decode("utf-8", errors="ignore")
                chat_file.seek(0)
            if st.session_state["chat_file_text"]:
                st.success("✅ 已加载")
        else:
            st.session_state["chat_file_text"] = None

        # 当前对话内的时间轴导航
        st.markdown("---")
        st.markdown("##### 🕐 时间轴")
        if st.session_state["chat_messages"]:
            user_msgs = [(i, m) for i, m in enumerate(st.session_state["chat_messages"]) if m["role"] == "user"]
            for idx, (msg_idx, msg) in enumerate(user_msgs):
                preview = msg["content"][:18] + ("..." if len(msg["content"]) > 18 else "")
                if st.button(f"Q{idx+1}: {preview}", key=f"tl_{msg_idx}", use_container_width=True):
                    # 使用 JS 滚动到对应消息
                    st.components.v1.html(
                        f'<script>parent.document.getElementById("msg-anchor-{msg_idx}")?.scrollIntoView({{behavior:"smooth",block:"start"}});</script>',
                        height=0,
                    )
        else:
            st.caption("对话后显示")

    with chat_right:
        st.markdown("### 🧑‍💼 AI 简历咨询师")
        st.caption("直接输入问题即可开始对话，左侧时间轴可快速跳转")

        # 显示历史消息
        if st.session_state["chat_messages"]:
            for i, msg in enumerate(st.session_state["chat_messages"]):
                st.markdown(f'<div id="msg-anchor-{i}"></div>', unsafe_allow_html=True)
                with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🧑‍💼"):
                    st.markdown(msg["content"])

        # 聊天输入框（自动在底部）
        user_input = st.chat_input("输入你的问题（可直接开始新对话）...")

        if user_input:
            if not st.session_state.get("api_key"):
                st.error("🔑 请在顶部输入 Gemini API Key！")
            elif not st.session_state.get("tavily_api_key"):
                st.error("🔍 请在顶部输入 Tavily API Key！")
            else:
                if st.session_state["current_chat_id"] is None:
                    st.session_state["current_chat_id"] = str(uuid.uuid4())[:8]
                    st.session_state["chat_messages"] = []

                st.session_state["chat_messages"].append({"role": "user", "content": user_input})
                with st.chat_message("user", avatar="👤"):
                    st.markdown(user_input)

                file_text = st.session_state.get("chat_file_text")
                with st.chat_message("assistant", avatar="🧑‍💼"):
                    with st.spinner("思考中..."):
                        reply = chat_with_consultant(
                            st.session_state["chat_messages"],
                            st.session_state["api_key"],
                            file_text=file_text,
                        )
                    st.markdown(reply)

                st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
                save_chat_session(st.session_state["current_chat_id"], st.session_state["chat_messages"])


# ============================================================
# TAB 3: 历史记录
# ============================================================
with tab_history:
    st.markdown("### 📁 诊断历史记录")
    records = load_all_diagnosis_records()

    if not records:
        st.info("📭 暂无诊断记录。")
    else:
        st.caption(f"共 {len(records)} 条记录（无上限）")

        for ri, record in enumerate(records):
            rec_id = record.get("id", ri)
            filename = record.get("filename", "未知文件")
            timestamp = record.get("timestamp", "")
            score = record.get("overall_score", 0)

            if score >= 90: score_emoji = "🟢"
            elif score >= 75: score_emoji = "🟡"
            elif score >= 60: score_emoji = "🟠"
            else: score_emoji = "🔴"

            st.markdown(f"**{score_emoji} {filename}** | 评分: {score} | {timestamp}")

            detail_key = f"detail_{ri}"
            if detail_key not in st.session_state:
                st.session_state[detail_key] = False

            btn_c, del_c = st.columns([6, 1])
            with btn_c:
                lbl = "🔽 收起详情" if st.session_state[detail_key] else "▶ 展开详情"
                if st.button(lbl, key=f"tg_{ri}", use_container_width=True):
                    st.session_state[detail_key] = not st.session_state[detail_key]
                    st.rerun()
            with del_c:
                cfk = f"cdr_{ri}"
                if st.session_state.get(cfk):
                    pass
                else:
                    if st.button("🗑️", key=f"dr_{ri}"):
                        st.session_state[cfk] = True
                        st.rerun()

            # 删除确认
            cfk = f"cdr_{ri}"
            if st.session_state.get(cfk):
                st.warning(f"确认删除「{filename}」？")
                yc, nc = st.columns(2)
                with yc:
                    if st.button("✅ 确认删除", key=f"ydr_{ri}"):
                        delete_diagnosis_record(rec_id)
                        st.session_state[cfk] = False
                        st.rerun()
                with nc:
                    if st.button("❌ 取消", key=f"ndr_{ri}"):
                        st.session_state[cfk] = False
                        st.rerun()

            if st.session_state[detail_key]:
                dt1, dt2, dt3, dt4, dt5 = st.tabs(["📊 完整诊断", "📚 专属面经与红线", "✨ 优化版简历", "📄 简历原文", "📋 JD 原文"])
                with dt1:
                    diag_r = record.get("diagnosis_result", {})
                    if diag_r.get("success") and diag_r.get("data"):
                        render_full_diagnosis(diag_r["data"])
                    else:
                        st.warning("此次诊断未获取到 AI 结果")
                with dt2:
                    saved_insights = record.get("industry_insights", "")
                    if saved_insights:
                        st.markdown(saved_insights)
                    else:
                        st.info("此条记录未包含行业情报（可能是旧版本保存的记录）")
                with dt3:
                    saved_improved = record.get("improved_resume", "")
                    if saved_improved:
                        st.text_area("优化版简历", saved_improved, height=500, disabled=True, key=f"imp_{ri}", label_visibility="collapsed")
                    else:
                        st.info("此条记录未生成优化简历")
                with dt4:
                    st.text(record.get("resume_text", "无内容"))
                with dt5:
                    st.text(record.get("jd_text", "无内容"))

            st.markdown("---")

# 页脚
st.markdown(
    '<p style="text-align:center;color:#555;font-size:0.85rem;margin-top:2rem;">'
    '🎯 ATS 简历智能诊断系统 v3.3 | Powered by Advanced AI Models</p>',
    unsafe_allow_html=True,
)
