# v0.4.0：更专业的投递判断、公开资料补充、GitHub 冷启动

这版重点不是堆功能，而是把结果页做得更像一个真正能帮求职者做决定的产品。

## 新增

- 结果页顶部新增“投递判断 / 招聘方第一反应 / 投递前先补什么”
- 公开资料补充支持来源可信度和排序
- 公开搜索客户端升级到 `ddgs`
- 新增 BYOK 文档，明确大模型走用户自带密钥路线
- 新增发布前隐私检查脚本
- 新增社交平台发帖执行包
- 新增 GitHub Beta 反馈 issue 模板

## 为什么值得更新

之前的结果更像“系统做了很多事”，现在更像“用户应该怎么做下一步”。

这版特别强调三件事：

1. 不只给分，还给投递判断
2. 不只给链接，还给公开来源可信度
3. 不只强调功能，还把隐私安全做进发布流程

## 本地验证

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1 -ResumePath "your_resume.pdf" -JdFile "data\samples\sample_supply_chain_jd.txt" -EnablePublicResearch
```

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_publish_readiness.ps1
```

## 已知边界

- 公开资料补充是辅助层，不会直接覆盖确定性分数
- 非 GitHub 平台的自动发布还没有接通官方稳定 API
- 大模型能力仍按 BYOK 方向推进，暂不强依赖
