# Resume Navigator

Resume Navigator 是一个面向中文求职场景的简历诊断系统，当前重点解决 4 件事：

1. 判断简历是否更容易被 ATS 正确读取
2. 判断简历是否真正对齐目标 JD
3. 给出可解释、可执行的修改建议
4. 把简历诊断自然承接到面试准备

当前仓库里同时保留了两层内容：

- 旧版 `Streamlit` 原型：`app.py`
- 新版可扩展架构：`backend/` + `apps/`

## 项目现状

项目正在持续重构中。

当前重构的目标不是“立刻做成一个很大的 AI 平台”，而是先把最核心、最可信、最容易验证的分析链路搭稳：

- 结构化简历解析
- 结构化 JD 解析
- 确定性 ATS 规则引擎
- 确定性匹配评分与可信度判断
- 用户可读的结果页
- 面试承接问题生成

## 新架构已经实现的能力

- 模块化配置层
- 结构化领域模型
- PDF / DOCX 简历解析
- ATS 确定性体检
- JD 结构化解析
- 基于技能、要求、量化表达、经历信号的匹配引擎
- 深度复核机制
- 后台任务式分析页，避免首页长时间卡住
- 中文默认、英文切换的 Web 演示入口
- 本地历史记录和试用反馈收集
- 可回归的单元测试

## 快速开始

### 1. 创建虚拟环境

在 Windows PowerShell 中运行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果你的 `python` 不在 `PATH` 里，也可以直接使用本机安装好的 Python 可执行文件。

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 配置环境变量

把 `.env.example` 复制成 `.env`，然后按需填写。

说明：

- 当前确定性分析链不依赖大模型 key 也能运行
- 未来如果接入大模型解释 / 改写，再配置对应 key 即可

### 4. 启动新版 Web 应用

```powershell
uvicorn apps.web.main:app --reload
```

启动后打开：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/history`
- `http://127.0.0.1:8000/feedback`
- `http://127.0.0.1:8000/docs`

### 5. 启动旧版 Streamlit 原型

```powershell
streamlit run app.py
```

### 6. 用命令行跑一次本地分析

```powershell
python scripts\run_local_analysis.py --resume "your_resume.pdf" --jd-file "target_jd.txt"
```

## 本地验证

### 快速验证

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1
```

### 用真实简历和 JD 做验证

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1 -ResumePath "your_resume.pdf" -JdFile "data\samples\sample_supply_chain_jd.txt"
```

### 检查是否适合发布到 GitHub

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_publish_readiness.ps1
```

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
tests/
```

## 相关文档

当前仓库已经包含面向开发、验证、推广和发布的中文文档：

- `docs/PRD.md`
- `docs/ARCHITECTURE_BLUEPRINT.md`
- `docs/FRONTEND_UI_REDESIGN_PLAN_ZH.md`
- `docs/LOCAL_VALIDATION_GUIDE_ZH.md`
- `docs/GITHUB_UPLOAD_GUIDE_ZH.md`
- `docs/COMMUNITY_PUBLISHING_GUIDE_ZH.md`
- `docs/GROWTH_PLAYBOOK_ZH.md`
- `docs/LLM_INTEGRATION_DECISION_ZH.md`
- `docs/INTERVIEW_SOURCE_STRATEGY_ZH.md`
- `docs/SEARCH_INTERVIEW_GTM_STRATEGY_ZH.md`
- `docs/SOCIAL_PLATFORM_API_AND_CONTENT_PLAN_ZH.md`
- `docs/BETA_TESTER_OPERATIONS_ZH.md`

## 开源与合规说明

开源版默认产品不依赖未授权抓取受保护招聘平台的数据。

如果以后做本地研究型连接器，也只能作为：

- 默认关闭
- 本地使用
- 非公开依赖

不能把它做成公开产品的核心基础。

## 接下来要继续做的事

1. 按 JD 改写简历
2. 结果页进一步用户化
3. 导出优化版简历
4. 面试承接继续专业化
5. 扩充公开来源并做证据化整理
