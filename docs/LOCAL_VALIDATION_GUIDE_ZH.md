# Resume Navigator 本地验证指南

版本：v0.2  
日期：2026-04-22

## 1. 这份指南是干什么的

每次我帮你改完一批代码后，你都可以按这份指南自己验证：

- 单测有没有通过
- 网页能不能打开
- 上传简历后能不能得到结果
- 历史记录和反馈页能不能正常访问
- 真正的简历和 JD 分析结果是不是基本合理

## 2. 先打开 PowerShell

打开 PowerShell 后，先进入项目目录：

```powershell
cd C:\Users\24981\Desktop\Resume_ATS_Project
```

## 3. 最推荐的新手验证方式：一键验证

直接运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1
```

这个脚本会自动做两件事：

1. 跑单元测试
2. 检查新 Web 入口能不能正常导入

如果你想再加上“真实简历 + 真实 JD”的验证，就运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1 -ResumePath "樊宇苗-同济经管硕士-采购供应链.pdf" -JdFile "data\samples\sample_supply_chain_jd.txt"
```

运行成功后，你会看到：

- `OK`
- `Resume Navigator`
- `Validation finished.`

并且会生成：

- `data\runtime\validation_result.json`

## 4. 如何自己启动网页

如果你想亲眼看 UI 页面效果，在 PowerShell 里运行：

```powershell
& 'C:\Users\24981\AppData\Local\Programs\Python\Python312\python.exe' -m uvicorn apps.web.main:app --reload
```

然后在浏览器里打开：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/history`
- `http://127.0.0.1:8000/feedback`

你应该能看到：

- 首页上传页
- 历史记录页
- 反馈看板页

## 5. 首页应该怎么验证

打开首页后，重点看这几件事：

1. 页面能否正常加载
2. 文案是否清晰
3. 上传表单是否正常
4. 按钮能否跳转到历史页和反馈页

如果首页一片空白、报错、按钮失效，说明前端入口有问题，需要告诉我。

## 6. 上传分析怎么验证

在首页按这个顺序操作：

1. 点击上传文件
2. 选择一份 PDF 或 DOCX 简历
3. 在 JD 输入框里粘贴目标岗位描述
4. 点击“开始分析”

成功后你应该能看到：

- ATS 分数
- Role Match 分数
- 优势信号
- 风险信号
- 证据高亮
- 技能覆盖
- 评分构成
- 提交反馈表单

## 7. 判断结果是否“基本合理”的标准

你不是要追求第一次就 100% 准，而是看它是否越来越像一个有判断依据的产品。

重点看下面这些点：

1. `section` 是否识别对了
2. 缺失硬技能是否真的是你没写进去的
3. 优先动作是否具体、能改
4. 风险信号是否和你的直觉相符
5. 评分构成是否讲得通

## 8. 如果你觉得结果不准，要记录什么

请尽量把问题记录成这种形式：

1. 哪个 section 识别错了
2. 哪个技能明明写了却没匹配上
3. 哪个建议太空泛
4. 哪个分数看起来明显不合理
5. 你的目标岗位真实更看重什么

你把这些告诉我，我就能更快定点修复，而不是盲改。

## 9. 如何验证反馈功能

在结果页底部：

1. 给整体体验打分
2. 给准确度打分
3. 给可执行性打分
4. 填写“最不准的地方”和“下一步想要的功能”
5. 点击提交反馈

提交成功后你应该看到感谢页。

然后打开：

- `http://127.0.0.1:8000/feedback`

你应该能看到刚才的反馈记录。

## 10. 如果你不想开网页，也可以直接跑命令行分析

运行：

```powershell
& 'C:\Users\24981\AppData\Local\Programs\Python\Python312\python.exe' scripts\run_local_analysis.py --resume "你的简历.pdf" --jd-file "你的JD.txt" --output "data\runtime\manual_check.json"
```

说明：

- `--resume` 是简历文件路径
- `--jd-file` 是 JD 文本文件路径
- `--output` 是分析结果保存路径

## 11. 如何准备一个 JD.txt

如果你不会建 JD 文件，可以这样做：

1. 在桌面或项目目录里右键新建文本文档
2. 命名成 `my_jd.txt`
3. 把岗位描述粘进去并保存

例如：

```text
岗位：供应链分析师
公司：某制造业公司
工作地点：上海
任职要求：
1. 本科及以上学历，2年以上供应链、采购或运营分析经验；
2. 熟悉 Excel、SQL，能够进行数据分析和报表搭建；
3. 具备跨部门沟通、项目推进和结果落地能力；
4. 有制造业、快消或供应链优化项目经验优先。
```

如果你懒得自己建，也可以直接用现成样例：

- `data/samples/sample_supply_chain_jd.txt`

## 12. 常见报错和解决办法

### 报错 1：系统提示禁止运行 `.ps1`

直接这样运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1
```

### 报错 2：找不到 `uvicorn`

不要直接输入 `uvicorn`，改用：

```powershell
& 'C:\Users\24981\AppData\Local\Programs\Python\Python312\python.exe' -m uvicorn apps.web.main:app --reload
```

### 报错 3：上传后返回 400

优先检查：

1. 简历是不是 PDF 或 DOCX
2. 文件是不是空的
3. JD 文本是不是没填

### 报错 4：结果很怪

优先判断是哪一类问题：

1. PDF 文本提取问题
2. Section 标题识别问题
3. 技能词典覆盖不够
4. JD 写法很特殊

这些都可以继续修，不代表产品方向错了。

## 13. 我建议你每次开发后的验证顺序

最省时间的顺序是：

1. 先跑 `validate_project.ps1`
2. 再启动网页
3. 用一份真实简历和一份真实 JD 跑一次
4. 再提交一条反馈，确认反馈链路也没坏

这是最适合新手、也最能及时发现问题的验证顺序。
