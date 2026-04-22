# 用户自带大模型（BYOK）接入说明

## 结论

这个项目后续如果接入大模型，推荐默认采用 `BYOK`（Bring Your Own Key，用户自带密钥）模式。

原因很直接：

1. 成本更可控：公开版仓库不需要替用户承担推理成本
2. 隐私更稳：用户可以只在自己本地环境里放密钥
3. 发布更安全：仓库不需要保存任何真实密钥
4. 产品更清晰：确定性评分负责“判断”，大模型负责“解释 / 改写 / 面试承接”

## 推荐用途

大模型适合做这些：

- 把结构化诊断结果解释成更自然的用户语言
- 根据 JD 安全改写简历 bullet
- 生成更像面试表达的话术框架
- 做中英双语润色

大模型不应该直接承担这些核心职责：

- 直接决定 ATS 分数
- 直接决定匹配总分
- 在没有证据时凭空生成经历或项目

## 当前配置项

在 `.env` 里可以使用这些字段：

```env
LLM_ACCESS_MODE=byok
ENABLE_OPTIONAL_LLM=false
GOOGLE_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

## 新手怎么操作

### 1. 复制环境变量文件

在项目根目录打开 PowerShell：

```powershell
Copy-Item .env.example .env
```

### 2. 编辑 `.env`

用 VS Code 或记事本打开项目根目录下的 `.env`，填入你自己的密钥。

例如：

```env
LLM_ACCESS_MODE=byok
ENABLE_OPTIONAL_LLM=true
OPENAI_API_KEY=你的密钥
OPENAI_MODEL=gpt-4o-mini
```

### 3. 重新启动服务

```powershell
uvicorn apps.web.main:app --reload
```

## 安全提醒

- 不要把 `.env` 上传到 GitHub
- 不要把截图里包含完整密钥的内容发到社交平台
- 如果怀疑密钥泄露，第一时间去平台后台重置
