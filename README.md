# Resume Navigator

Resume Navigator 是一个面向中文求职场景的简历诊断系统。它的目标不是“秒出一个看起来很聪明的分数”，而是尽量把下面几件事做扎实：

1. 判断简历是否容易被 ATS 正确读取
2. 判断简历是否真的对齐目标 JD
3. 给出可执行、可解释、尽量有证据的修改建议
4. 把诊断自然承接到面试准备，而不是停在打分页

当前仓库同时保留了两层内容：

- 旧版 `Streamlit` 原型：`app.py`
- 新版可扩展架构：`backend/` + `apps/`

## 现在已经能做什么

- 结构化解析 PDF / DOCX 简历
- 结构化解析 JD
- 基于确定性规则的 ATS 体检
- 基于技能、要求、量化结果和经历信号的匹配分析
- 深度复核模式：要求级证据卡片、置信度、过程追踪
- 可选的公开资料补充：搜索公开岗位要求、面经和技能资料，用来丰富报告
- 面试承接：根据当前简历缺口和岗位要求生成更像真实面试的追问
- Web 界面：默认简体中文，可切换英文
- 结果页默认面向求职者展示，不再把内部阶段耗时、开发者披露信息放在主视图里
- 本地历史记录、反馈收集、JSON 导出

## 产品原则

- 评分核心优先走确定性链路，不把总分完全交给大模型
- 公开资料补充只做辅助证据，不直接覆盖 ATS 与匹配分数
- 大模型默认走“用户自带密钥 BYOK”路线，不要求把私钥写进仓库
- 隐私优先，用户简历、导出文件、运行时数据默认不提交到 GitHub
- 最终产品优先展示用户需要的结论、缺口、改写建议和面试承接，不展示开发调试信息

## 快速开始

### 1. 创建虚拟环境

在 Windows PowerShell 中运行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 配置环境变量

把 `.env.example` 复制成 `.env`，然后按需填写。

说明：

- 当前确定性分析链不依赖大模型密钥也能运行
- 如果要启用后续改写 / 解释类大模型能力，建议采用本地自带密钥方式
- 是否开启公开资料补充可以通过环境变量或页面勾选来控制

### 4. 启动新版 Web 应用

```powershell
uvicorn apps.web.main:app --reload
```

打开：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/history`
- `http://127.0.0.1:8000/feedback`
- `http://127.0.0.1:8000/docs`

### 5. 启动旧版 Streamlit 原型

```powershell
streamlit run app.py
```

### 6. 命令行跑一次本地分析

```powershell
python scripts\run_local_analysis.py --resume "your_resume.pdf" --jd-file "target_jd.txt" --analysis-mode deep
```

如果想顺手开启公开资料补充：

```powershell
python scripts\run_local_analysis.py --resume "your_resume.pdf" --jd-file "target_jd.txt" --analysis-mode deep --enable-public-research
```

## 本地验证

### 快速验证

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1
```

### 用真实简历和 JD 验证

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1 -ResumePath "your_resume.pdf" -JdFile "data\samples\sample_supply_chain_jd.txt"
```

如果想一起验证公开资料补充：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1 -ResumePath "your_resume.pdf" -JdFile "data\samples\sample_supply_chain_jd.txt" -EnablePublicResearch
```

### 发布前检查

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_publish_readiness.ps1
```

这会同时检查：

- Git 远程和用户配置
- GitHub CLI 状态
- 工作区变更
- 隐私安全风险

## 仓库结构

```text
apps/
  web/
backend/
  api/
  core/
  providers/
  services/
docs/
scripts/
tests/
```

## 重要文档

- `docs/PRD.md`
- `docs/ARCHITECTURE_BLUEPRINT.md`
- `docs/FRONTEND_UI_REDESIGN_PLAN_ZH.md`
- `docs/LOCAL_VALIDATION_GUIDE_ZH.md`
- `docs/GITHUB_UPLOAD_GUIDE_ZH.md`
- `docs/GROWTH_PLAYBOOK_ZH.md`
- `docs/LLM_INTEGRATION_DECISION_ZH.md`
- `docs/BYOK_LLM_SETUP_ZH.md`
- `docs/INTERVIEW_SOURCE_STRATEGY_ZH.md`
- `docs/SEARCH_INTERVIEW_GTM_STRATEGY_ZH.md`
- `docs/SOCIAL_PLATFORM_API_AND_CONTENT_PLAN_ZH.md`
- `docs/SOCIAL_PLATFORM_EXECUTION_PACK_ZH.md`
- `docs/SOCIAL_POST_PACK_V0_5_ZH.md`
- `docs/BETA_TESTER_OPERATIONS_ZH.md`

## 隐私与合规

- `.gitignore` 默认忽略 `.env`、运行时数据库、上传文件、导出文件、PDF / DOCX、浏览器 profile / cookies 等内容
- 公开版产品不依赖未授权抓取的受保护招聘平台数据
- 如果以后保留本地研究型连接器，也必须默认关闭、只在私有环境里使用

## 下一步重点

1. 按 JD 改写简历
2. 继续把结果页做得更偏用户视角
3. 导出优化版简历
4. 面试承接继续专业化
5. 扩充公开来源并做更强的证据化表达
