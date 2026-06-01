# MVP Plan

## 1. MVP 目标

MVP 的目标是做出一个可演示、可试用、能体现产品价值的 ResumeFit Demo，而不是一次性完成商业化平台。

MVP 成功标准：

- 用户能输入通用简历和项目经历。
- 用户能粘贴岗位 JD。
- 系统能输出 JD 分析、匹配报告、定制简历、真实性风险和面试追问。
- 用户能保存多个简历版本。
- 用户能导出 Markdown。
- AI 接口使用 OpenAI-compatible 结构，默认配置可指向 DeepSeek。

## 2. 阶段划分

### Phase 0: 项目骨架

目标：建立可扩展的前后端基础结构。

任务：

- 创建 Vue 3 前端项目。
- 创建 FastAPI 后端项目。
- 配置 SQLite。
- 配置环境变量读取。
- 建立 `prompts/` 目录。
- 建立基础 API 路由结构。
- 建立 AI service 抽象。

验收：

- 前后端可以本地启动。
- 后端有健康检查接口。
- AI 配置不硬编码在代码中。

### Phase 1: 数据录入

目标：完成事实来源输入。

任务：

- 通用简历创建、编辑和查看。
- 项目库创建、编辑、删除和列表。
- JD 创建、编辑和查看。

验收：

- 用户可以录入基本求职资料。
- 数据持久化到 SQLite。
- 页面流程可以演示。

### Phase 2: AI 分析链路

目标：跑通从 JD 到匹配报告的 AI 能力。

任务：

- JD 分析 Prompt。
- 匹配度评分 Prompt。
- 后端 AI 调用封装。
- 结果 JSON 解析和存储。
- 前端展示分析结果和匹配报告。

验收：

- 输入 JD 后可以生成结构化分析。
- 系统可以根据简历和项目库生成匹配报告。
- AI 输出失败时有错误提示。

### Phase 3: 简历生成与风险检测

目标：生成可信的岗位定制简历。

任务：

- 定制简历生成 Prompt。
- 真实性风险检测 Prompt。
- 简历版本保存。
- Markdown 预览。
- 风险提示展示。

验收：

- 系统能生成 Markdown 格式简历。
- 生成结果能关联 JD 和匹配报告。
- 风险检测可以指出可疑表述。

### Phase 4: 面试追问与导出

目标：补齐求职准备闭环。

任务：

- 面试追问预测 Prompt。
- 面试问题列表展示。
- Markdown 导出。
- 多版本列表和详情页。

验收：

- 用户可以查看岗位相关面试追问。
- 用户可以导出 Markdown。
- 用户可以回看历史版本。

## 3. MVP 页面建议

最小页面集合：

- Dashboard：展示最近 JD、匹配报告和简历版本。
- Resume Profile：编辑通用简历。
- Projects：管理项目库。
- Job Descriptions：录入和查看 JD。
- Analysis Workspace：展示 JD 分析、匹配报告、生成简历、风险检测和面试追问。
- Resume Versions：查看和导出历史版本。

## 4. MVP API 建议

基础资源 API：

- `GET /health`
- `POST /resume-profiles`
- `GET /resume-profiles/{id}`
- `PUT /resume-profiles/{id}`
- `POST /projects`
- `GET /projects`
- `PUT /projects/{id}`
- `DELETE /projects/{id}`
- `POST /job-descriptions`
- `GET /job-descriptions`
- `GET /job-descriptions/{id}`

AI 工作流 API：

- `POST /job-descriptions/{id}/analyze`
- `POST /job-descriptions/{id}/match`
- `POST /job-descriptions/{id}/generate-resume`
- `POST /truth-check-results`
- `GET /truth-check-results?resume_version_id={id}`
- `POST /resume-versions/{id}/interview-questions`
- `GET /resume-versions`
- `GET /resume-versions/{id}`
- `GET /resume-versions/{id}/export/markdown`

## 5. 优先级

### P0

- 通用简历输入。
- 项目库管理。
- JD 输入。
- JD 分析。
- 匹配度评分。
- 定制简历生成。
- Markdown 导出。

### P1

- 真实性风险检测。
- 面试追问预测。
- 多版本管理。
- AI 输出结构校验。

### P2

- UI 优化。
- 简历模板。
- 更细的版本对比。
- 多模型切换 UI。
- 简历导入。

## 6. MVP 不进入范围

- 支付。
- 会员。
- 招聘网站爬取。
- 手机 APP。
- 企业后台。
- 自动投递。
- 复杂权限。
- PDF/Word 导出。

## 7. Demo 演示脚本

1. 打开 ResumeFit Dashboard。
2. 展示一份已录入的通用简历。
3. 展示项目库中 2 到 3 个项目。
4. 粘贴一个目标岗位 JD。
5. 点击分析 JD。
6. 查看岗位关键词、硬技能和隐含要求。
7. 生成匹配度评分。
8. 查看优势、短板和优化建议。
9. 生成岗位定制简历。
10. 查看真实性风险提示。
11. 查看面试追问预测。
12. 保存版本并导出 Markdown。
