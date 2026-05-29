# Resume Navigator

Resume Navigator 是一个面向中文求职场景的简历诊断系统。它不是只给一个“AI 打分”，而是帮助求职者回答更实际的几个问题：

- 这份简历现在能不能投？
- 为什么能投，或者为什么还不够稳？
- 投递前最应该先补哪一块？
- 面试时最可能被追问哪里？
- 如何把简历改得更贴近目标 JD，同时不编造经历？

项目默认使用确定性规则进行 ATS 体检、JD 对齐和证据判断；大模型和公开搜索都作为可选增强层，用户可以自行配置 API Key。

## 主要功能

- PDF / DOCX 简历解析
- JD 岗位描述结构化解析
- ATS 兼容性检查
- 简历与 JD 的硬技能、关键词、必选要求、量化结果和经历证据匹配
- 深度诊断模式：要求级证据卡片、结论稳定度、优先动作
- 可选公开资料补充：支持 Tavily API，未配置时可回退公开搜索
- 可选大模型增强：支持用户自带 Gemini / OpenAI Key，用于润色用户可见摘要
- JD 定向改写建议：只基于真实经历表达，不鼓励编造
- 面试承接：根据当前缺口生成更像真实面试的追问、回答骨架和练习提示
- 中文优先 Web 界面，并支持英文切换
- 本地历史记录、反馈收集和 JSON 导出

## 产品原则

- 分数不完全交给大模型，核心判断优先走可解释规则。
- 大模型只做增强，不负责改写事实、不接管总分。
- 公开资料只做补充背景，不直接覆盖 ATS 和匹配结论。
- 默认隐私优先，真实简历、`.env`、运行数据、导出文件不会提交到 GitHub。
- 面向用户展示“能不能投、为什么、先改什么、面试会问什么”，不在主界面展示开发调试信息。

## 快速开始

下面以 Windows PowerShell 为例。

### 1. 克隆项目

```powershell
git clone https://github.com/lezebomb/resume-navigator.git
cd resume-navigator
```

如果你已经在本地打开了这个项目，可以直接进入项目目录：

```powershell
cd C:\Users\24981\Desktop\Resume_ATS_Project
```

### 2. 创建虚拟环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 提示脚本无法运行，可以先执行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

然后重新运行：

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

### 4. 配置环境变量

复制示例配置：

```powershell
Copy-Item .env.example .env
```

默认不配置任何 API Key 也能运行确定性诊断。

如果想开启可选大模型增强，在 `.env` 中填写：

```env
ENABLE_OPTIONAL_LLM=true

# 二选一即可
GOOGLE_API_KEY=你的 Gemini Key
GEMINI_MODEL=gemini-2.5-flash

OPENAI_API_KEY=你的 OpenAI Key
OPENAI_MODEL=gpt-4o-mini
```

如果想开启 Tavily 搜索增强，在 `.env` 中填写：

```env
TAVILY_API_KEY=你的 Tavily Key
SEARCH_PROVIDER=auto
PUBLIC_RESEARCH_MAX_RESULTS=5
```

说明：

- `SEARCH_PROVIDER=auto`：有 Tavily Key 时优先使用 Tavily，没有结果时回退公开搜索。
- `SEARCH_PROVIDER=tavily`：只使用 Tavily。
- 公开搜索只作为补充资料，不会直接改写核心分数。

### 5. 启动 Web 应用

```powershell
uvicorn apps.web.main:app --reload
```

浏览器打开：

```text
http://127.0.0.1:8000/
```

示例案例页：

```text
http://127.0.0.1:8000/cases
```

英文界面：

```text
http://127.0.0.1:8000/?lang=en
```

## 如何使用

1. 打开首页。
2. 上传一份 PDF 或 DOCX 简历。
3. 粘贴目标岗位 JD。
4. 建议保留默认的“深度诊断”模式。
5. 如果你想参考公开面经和岗位资料，可以勾选“补充公开资料搜索”。
6. 点击开始分析。
7. 等待系统跳转到结果页。
8. 重点查看“投递判断”“招聘方第一反应”“投递前先补什么”“改写建议”“面试承接”。

结果页里的“复制投递摘要”和“复制面试练习卡”可以直接用于后续修改和练习。

## 本地命令行分析

如果不想打开网页，也可以用命令行运行：

```powershell
python scripts\run_local_analysis.py --resume "your_resume.pdf" --jd-file "target_jd.txt" --analysis-mode deep
```

开启公开资料补充：

```powershell
python scripts\run_local_analysis.py --resume "your_resume.pdf" --jd-file "target_jd.txt" --analysis-mode deep --enable-public-research
```

## 验证项目是否正常

运行完整验证：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1
```

用自己的简历和示例 JD 验证：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1 -ResumePath "your_resume.pdf" -JdFile "data\samples\sample_supply_chain_jd.txt" -EnablePublicResearch
```

验证内容包括：

- 单元测试
- Web 入口导入
- 本地诊断链路
- 可选公开资料补充链路

## 发布前隐私检查

在上传 GitHub 前建议运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_publish_readiness.ps1
```

这个脚本会检查：

- Git 远程仓库配置
- GitHub CLI 登录状态
- 工作区变更
- `.env`、PDF、DOCX、运行数据等隐私风险

## 目录结构

```text
apps/
  web/                 Web 页面、模板、静态样式
backend/
  api/                 API 数据结构与路由
  core/                配置与日志
  providers/           可插拔外部提供方
  services/            简历解析、ATS、JD、匹配、搜索、改写、面试承接
docs/                  产品文档、发布文案、推广素材
scripts/               本地运行与验证脚本
tests/                 单元测试
utils/                 旧版原型复用工具
app.py                 旧版 Streamlit 原型
```

## 可选 API 配置说明

### 大模型

大模型是可选功能。默认情况下，系统不需要大模型也能完成核心诊断。

当前大模型只用于：

- 压缩和润色用户看到的摘要
- 后续可扩展为更自然的改写建议
- 后续可扩展为更强的面试回答反馈

它不会用于：

- 直接决定总分
- 编造经历
- 覆盖确定性证据判断

### Tavily

Tavily 用于搜索公开岗位资料、面经和技能要求。

它不会用于：

- 抓取用户隐私数据
- 绕过平台限制
- 直接改写核心评分

## 常见问题

### 1. 没有 API Key 能用吗？

可以。核心诊断链路不依赖 API Key。

### 2. 为什么分析不是只出一个分数？

因为求职者真正需要的是“能不能投、为什么、先改什么、面试会问什么”。分数只是辅助，不应该成为唯一结论。

### 3. 会不会把我的简历上传到 GitHub？

不会。`.gitignore` 默认忽略 `.env`、PDF、DOCX、上传文件、导出文件和运行时数据。

### 4. 可以用于英文岗位吗？

可以。当前界面支持中文和英文切换，但产品体验优先围绕中文求职场景设计。

### 5. 为什么不让大模型直接打分？

因为单次模型打分不稳定，也难以复核。这个项目把评分核心放在确定性规则和证据链上，大模型只做增强。

## 重要文档

- [产品需求文档](docs/PRD.md)
- [架构蓝图](docs/ARCHITECTURE_BLUEPRINT.md)
- [本地验证指南](docs/LOCAL_VALIDATION_GUIDE_ZH.md)
- [GitHub 上传指南](docs/GITHUB_UPLOAD_GUIDE_ZH.md)
- [BYOK 大模型配置说明](docs/BYOK_LLM_SETUP_ZH.md)
- [最终发布内容包](docs/FINAL_LAUNCH_CONTENT_ZH.md)
- [v0.5.0 版本说明](docs/RELEASE_v0.5.0_ZH.md)

## License

如果你准备公开给更多人使用，建议补充明确的开源许可证，例如 MIT License。
