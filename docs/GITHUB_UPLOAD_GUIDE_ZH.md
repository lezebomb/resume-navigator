# Resume Navigator GitHub 上传指南

版本：v0.2  
日期：2026-04-22

## 1. 这份指南解决什么问题

如果你是第一次把本地项目上传到 GitHub，这份指南会带你完成完整流程：

1. 在 GitHub 网站创建空仓库
2. 在本地检查仓库状态
3. 提交代码
4. 绑定远程仓库
5. 推送到 GitHub

## 2. 你现在这台电脑的已知状态

我已经替你检查过当前环境，结论是：

- 本地已经是 Git 仓库
- `git user.name` 已配置
- `git user.email` 已配置
- 还没有配置 `origin`
- 还没有安装 `gh`

这意味着：

- 我可以继续帮你整理代码、提交本地 commit
- 但在没有远程仓库地址和 GitHub 登录能力之前，我还不能直接替你完成 `git push`

## 3. 你要先做的 2 件事

### 第 1 件：在 GitHub 网站创建空仓库

打开 [GitHub](https://github.com/) 并登录。

然后：

1. 点击右上角 `+`
2. 点击 `New repository`
3. 仓库名建议填写：`resume-navigator`
4. 描述建议填写：`Chinese-first resume diagnosis system with ATS checks, JD matching, and explainable optimization workflows`
5. 选择 `Public`
6. 不要勾选自动创建 `README`、`.gitignore`、`LICENSE`
7. 点击 `Create repository`

### 第 2 件：把仓库地址准备好

创建完成后，你会看到类似下面的地址：

```text
https://github.com/你的用户名/resume-navigator.git
```

把这个地址记下来，后面会用到。

## 4. 在哪里运行命令

所有命令都在 PowerShell 里运行。

先打开 PowerShell，然后执行：

```powershell
cd C:\Users\24981\Desktop\Resume_ATS_Project
```

## 5. 先检查一次发布准备情况

运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_publish_readiness.ps1
```

你会看到：

- 当前是不是 Git 仓库
- 有没有配置远程仓库
- 有没有配置 Git 用户信息
- 有没有安装 `gh`
- 当前工作区是不是还有未提交内容

## 6. 首次上传的标准命令

如果你已经创建好了 GitHub 空仓库，在 PowerShell 中执行：

```powershell
git status
git add .
git commit -m "feat: upgrade deterministic scoring, beta feedback loop, and polished web demo"
git remote add origin https://github.com/YOUR_USERNAME/resume-navigator.git
git branch -M main
git push -u origin main
```

注意：

- 你需要把 `YOUR_USERNAME` 改成你的 GitHub 用户名
- 如果提示 `origin already exists`，不要慌，按下面第 8 节处理

## 7. 如果你希望我继续接管到 push

你只需要完成下面任意一种准备：

### 方案 A

1. 你先在 GitHub 网站创建空仓库
2. 把仓库地址告诉我
3. 然后继续让我操作

这样我就可以继续替你执行：

- `git add`
- `git commit`
- `git remote add`
- `git push`

### 方案 B

安装 GitHub CLI：

- 官网：[GitHub CLI](https://cli.github.com/)

安装后在 PowerShell 中运行：

```powershell
gh auth login
```

登录成功后再告诉我继续，我就能更顺地接管后续 GitHub 发布流程。

## 8. 常见报错怎么处理

### 报错 1：`remote origin already exists`

先看当前远程地址：

```powershell
git remote -v
```

如果地址错了，改成正确地址：

```powershell
git remote set-url origin https://github.com/YOUR_USERNAME/resume-navigator.git
```

### 报错 2：`Authentication failed`

这通常说明：

- 你还没登录 GitHub
- 或者 Git 本地凭证还没配置好

解决办法：

1. 安装并登录 [GitHub Desktop](https://desktop.github.com/)
2. 或者安装 `gh` 后运行：

```powershell
gh auth login
```

### 报错 3：`failed to push some refs`

可能原因：

- 远程仓库已经有内容
- 本地和远程分支不一致

先运行：

```powershell
git pull --rebase origin main
```

如果你不确定要不要这么做，先停下来告诉我，我再帮你判断。

## 9. 上传完成后建议立刻做的事

上传成功后，建议你在 GitHub 仓库页面补齐这些内容：

1. 在 `About` 中填写一句话介绍
2. 添加 Topics
3. 打开 Issues
4. 打开 Discussions
5. 检查 Actions 是否通过

建议 Topics：

- resume
- ats
- job-search
- career
- fastapi
- python
- chinese-nlp
- open-source

## 10. 后续每次更新怎么推送

以后每次改完代码，在 PowerShell 里重复下面的流程：

```powershell
cd C:\Users\24981\Desktop\Resume_ATS_Project
git status
git add .
git commit -m "feat: 这里写本次改动摘要"
git push
```

## 11. 最适合新手的实际顺序

如果你想最稳妥地完成第一次公开发布，建议按这个顺序做：

1. 先看一次 `check_publish_readiness.ps1`
2. 在 GitHub 网站创建空仓库
3. 回到 PowerShell 绑定 `origin`
4. 执行首次 `git push`
5. 刷新 GitHub 页面确认代码已上传
6. 再开始发第一条开发日志
