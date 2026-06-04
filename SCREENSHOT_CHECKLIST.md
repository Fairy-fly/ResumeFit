# ResumeFit 答辩截图清单

## 1. 首页 Dashboard

- 截图名称：`01_dashboard.png`
- 截图位置：`http://localhost:5173/`
- 截图重点：8 步 Demo 流程、数据统计卡片、快捷入口。
- 答辩时怎么讲：这是系统首页，展示从简历输入到 Markdown 导出的完整使用路径，便于现场按流程演示。

## 2. 通用简历页面

- 截图名称：`02_resume_profile.png`
- 截图位置：`http://localhost:5173/resume`
- 截图重点：简历标题输入、Markdown 正文输入、已保存简历列表。
- 答辩时怎么讲：通用简历是后续 AI 生成的主要事实来源，系统不会凭空生成用户没有提供的经历。

## 3. 项目库页面

- 截图名称：`03_projects.png`
- 截图位置：`http://localhost:5173/projects`
- 截图重点：项目名称、项目类型、我的角色、技术栈、项目描述、个人贡献、作品链接。
- 答辩时怎么讲：项目库用于记录用户真实项目经历，后续匹配报告和定制简历会读取用户选择的项目。

## 4. JD 分析页面

- 截图名称：`04_job_analysis.png`
- 截图位置：`http://localhost:5173/jobs`
- 截图重点：JD 输入区域、岗位分析结果卡片、必备技能、加分技能、关键词。
- 答辩时怎么讲：系统通过统一 AI service 分析 JD，输出稳定 JSON，再由前端以卡片形式展示。

## 5. 匹配度报告页面

- 截图名称：`05_match_report.png`
- 截图位置：`http://localhost:5173/analysis`
- 截图重点：简历选择、项目多选、JD 选择、匹配分数、优势、不足、建议。
- 答辩时怎么讲：匹配报告综合简历、项目和 JD 分析结果，帮助用户知道当前简历与岗位的差距。

## 6. 定制简历生成页面

- 截图名称：`06_resume_version.png`
- 截图位置：`http://localhost:5173/versions`
- 截图重点：匹配报告选择、生成按钮、Markdown 简历内容、修改原因。
- 答辩时怎么讲：系统生成的是 Markdown 简历，同时给出每处修改原因，便于用户理解 AI 修改依据。

## 7. 真实性风险检测结果

- 截图名称：`07_truth_check.png`
- 截图位置：`http://localhost:5173/versions`
- 截图重点：总体风险等级、风险表达、风险类型、证据状态、更稳妥改法。
- 答辩时怎么讲：这个模块用于控制 AI 过度包装问题，提醒用户哪些表达可能缺少证据或面试风险较高。

## 8. 面试追问预测结果

- 截图名称：`08_interview_questions.png`
- 截图位置：`http://localhost:5173/versions`
- 截图重点：面试问题、为什么会问、关联简历内容、难度、建议回答、风险提醒。
- 答辩时怎么讲：系统根据简历、JD 和风险检测结果，帮助用户提前准备可能被问到的问题。

## 9. Markdown 导出按钮或导出文件

- 截图名称：`09_markdown_export.png`
- 截图位置：`http://localhost:5173/versions` 或本地下载文件。
- 截图重点：导出 Markdown 按钮、浏览器下载结果、`.md` 文件内容。
- 答辩时怎么讲：MVP 阶段先支持 Markdown 导出，后续可以扩展 PDF 和 Word。

## 10. FastAPI docs 页面

- 截图名称：`10_fastapi_docs.png`
- 截图位置：`http://localhost:8000/docs`
- 截图重点：接口列表，例如 `/resume-profiles`、`/projects`、`/job-descriptions`、`/match-reports`、`/resume-versions`。
- 答辩时怎么讲：FastAPI 自动生成接口文档，说明后端 API 结构清晰，便于调试和扩展。

## 11. 数据库表结构或测试数据

- 截图名称：`11_database_schema.png`
- 截图位置：SQLite 查看工具、命令行或 `DATABASE_SCHEMA.md`。
- 截图重点：`resume_profiles`、`projects`、`job_descriptions`、`job_analyses`、`match_reports`、`resume_versions`、`truth_check_results`、`interview_question_results`。
- 答辩时怎么讲：数据库把原始资料和 AI 生成结果分开保存，支持版本追溯和后续扩展。

## 12. pytest 通过截图

- 截图名称：`12_pytest_passed.png`
- 截图位置：PowerShell 终端。
- 截图重点：执行 `python -m pytest` 后显示测试通过。
- 答辩时怎么讲：后端测试使用 mock AI，避免依赖真实 DeepSeek 调用，同时覆盖核心接口和错误处理。

## 13. npm run build 通过截图

- 截图名称：`13_npm_build_passed.png`
- 截图位置：PowerShell 终端。
- 截图重点：执行 `npm run build` 后显示构建成功。
- 答辩时怎么讲：前端 TypeScript 和 Vue 构建通过，说明页面代码可以正常打包。

## 截图准备建议

- 截图前准备一套演示数据，避免页面为空。
- 不要在截图中暴露真实 API Key、邮箱、手机号或隐私内容。
- 截图尽量使用同一浏览器尺寸，PPT 观感更统一。
- 终端截图保留关键命令和结果即可，不需要截太长日志。
