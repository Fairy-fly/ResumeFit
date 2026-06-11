# Architecture

## 1. 架构目标

ResumeFit 的架构应服务两个阶段：

- Demo 阶段：快速跑通核心求职辅助闭环，代码结构清晰，便于迭代。
- 商业化阶段：预留用户体系、计费、更多模型、更多导出格式和数据库升级能力。

架构不追求过早复杂化，但必须避免把业务逻辑堆在单个大文件中。

## 2. 总体结构

```text
resume-fit/
  frontend/              # Vue 3 application
  backend/               # FastAPI application
  prompts/               # Prompt templates and prompt docs
  docs/                  # Future extended documentation
  README.md
```

MVP 可先采用前后端分离结构：

- Vue 3 负责交互、表单、结果展示和 Markdown 预览。
- FastAPI 负责业务 API、数据库访问、AI service、Prompt 加载和工作流编排。
- SQLite 负责本地持久化。
- AI provider 通过 OpenAI-compatible HTTP API 调用。

## 3. 后端分层建议

```text
backend/
  app/
    main.py
    core/
      config.py
      database.py
      security.py
    api/
      routes/
        health.py
        resume_profiles.py
        projects.py
        job_descriptions.py
        analyses.py
        resume_versions.py
    models/
      user.py
      resume_profile.py
      project.py
      job_description.py
      job_analysis.py
      match_report.py
      resume_version.py
      interview_question.py
    ai/
      client.py
      prompt_loader.py
    schemas/
      user.py
      resume_profile.py
      project.py
      job_description.py
      analysis.py
      match_report.py
      resume_version.py
      interview_question.py
    services/
      job_analysis_service.py
      match_service.py
      resume_generation_service.py
      risk_detection_service.py
      interview_question_service.py
    repositories/
      user_repository.py
      resume_profile_repository.py
      project_repository.py
      job_description_repository.py
      job_analysis_repository.py
      match_report_repository.py
      resume_version_repository.py
      interview_question_repository.py
  migrations/
```

分层职责：

- `api/routes/`：处理 HTTP 请求和响应，不写复杂业务逻辑。
- `schemas/`：定义请求和响应 DTO。
- `models/`：定义数据库模型。
- `repositories/`：封装数据库读写。
- `services/`：组织业务流程和 AI 调用。
- `ai/`：封装 OpenAI-compatible client 和 Prompt 加载。
- `core/`：配置、数据库连接、安全基础设施。

## 4. 前端结构建议

```text
frontend/
  src/
    main.ts
    App.vue
    router/
      index.ts
    api/
      client.ts
      resumeProfiles.ts
      projects.ts
      jobDescriptions.ts
      analyses.ts
      resumeVersions.ts
    pages/
      DashboardPage.vue
      ResumeProfilePage.vue
      ProjectsPage.vue
      JobDescriptionsPage.vue
      AnalysisWorkspacePage.vue
      ResumeVersionsPage.vue
    components/
      resume/
      projects/
      jobs/
      analysis/
      common/
    stores/
```

前端原则：

- 页面负责组织用户流程。
- API 调用集中放在 `src/api/`。
- 通用组件放在 `components/common/`。
- 不在组件中硬编码后端地址，应通过环境变量配置。

## 5. AI Service 设计

MVP 默认使用 DeepSeek API，但代码必须按 OpenAI-compatible 接口设计。

建议配置：

```text
AI_PROVIDER=deepseek
AI_BASE_URL=https://api.deepseek.com
AI_API_KEY=...
AI_MODEL=deepseek-chat
AI_TIMEOUT_SECONDS=60
```

服务层命名应保持供应商中立：

- 使用 `AIClient`，不要命名为 `DeepSeekClient`。
- 使用 `AI_BASE_URL`，不要命名为 `DEEPSEEK_URL`。
- 使用 `AI_MODEL`，不要命名为 `DEEPSEEK_MODEL`。

后续切换 OpenAI、通义、智谱或其他兼容接口时，只需要调整配置和少量适配逻辑。

## 6. Prompt 管理

所有 Prompt 放在 `prompts/` 目录，不直接散落在业务代码中。

建议文件：

```text
prompts/
  jd_analyzer_v1.md
  match_scorer_v1.md
  resume_writer_v1.md
  truth_checker_v1.md
  interview_question_v1.md
  job_analysis.md
  match_report.md
  resume_generation.md
  risk_detection.md
  interview_questions.md
```

后端通过 `PromptLoader` 加载 Prompt，并注入结构化上下文。

## 7. AI 工作流

### JD 分析

输入：

- 原始 JD 文本

输出：

- 结构化 `JobAnalysis`

### 匹配评分

输入：

- `ResumeProfile`
- `Project[]`
- `JobDescription`
- `JobAnalysis`

输出：

- `MatchReport`

### 定制简历生成

输入：

- `ResumeProfile`
- `Project[]`
- `JobAnalysis`
- `MatchReport`

输出：

- Markdown 简历内容
- 生成说明
- 修改原因 `change_explanations`

### 真实性风险检测

输入：

- 原始资料
- 生成后的 `ResumeVersion`
- 本次生成选择的 `Project[]`
- `JobDescription`
- `JobAnalysis`
- `MatchReport`

输出：

- 风险等级
- 风险项
- 修改建议
- 缺失证据
- 面试追问风险点提示

### 面试追问预测

输入：

- JD
- JD 分析
- 定制简历
- 项目经历
- 匹配报告
- 最新真实性风险检测结果（如果存在）

输出：

- 面试问题列表
- 为什么会问
- 关联简历内容
- 建议回答
- 回答策略
- 风险提醒

## 8. 数据库演进

MVP 使用 SQLite，适合本地 Demo 和单用户/少量用户验证。

商业化阶段可升级 PostgreSQL：

- 保留整数主键或 UUID 的一致策略。
- 使用迁移工具管理 schema。
- 为用户维度、版本维度和 AI 任务日志添加索引。
- 将大文本、AI 输出和审计日志拆分清楚。

## 9. 安全与配置

必须遵守：

- 不硬编码 API Key。
- 不把 `.env` 提交到仓库。
- 不在日志中输出完整 API Key。
- 用户简历内容属于敏感数据，日志中避免打印完整原文。
- AI 请求和响应可在 Demo 阶段做最小记录，商业化前必须增加隐私策略和数据删除能力。

### V0.3 认证与用户隔离

V0.3 已接入多用户基础能力：

- 后端提供 `/auth/register`、`/auth/login`、`/auth/me`。
- 鉴权方式为 JWT Bearer Token。
- `JWT_SECRET_KEY`、`JWT_ALGORITHM`、`ACCESS_TOKEN_EXPIRE_MINUTES` 从环境变量读取。
- 密码只保存哈希，不保存明文密码。
- 前端将 `access_token` 保存到 `localStorage`。
- API client 在有 token 时自动携带 `Authorization: Bearer <token>`。
- 业务 route 通过 `get_current_user` 获取当前用户，再把 `current_user.id` 传入 service。
- service/repository 使用 `user_id` 过滤用户数据，避免跨用户读取。

已完成用户隔离的数据范围：

- 通用简历 `ResumeProfile`
- 项目经历 `Project`
- 岗位 JD `JobDescription`
- 匹配报告 `MatchReport`
- 简历版本 `ResumeVersion`
- Markdown 导出
- 真实性风险检测 `TruthCheckResult`
- 面试追问预测 `InterviewQuestionResult`

跨表生成流程也必须遵守用户隔离。例如生成匹配报告时，所选简历、项目和 JD 必须属于当前用户；生成简历版本、真实性检测和面试追问时，关联的报告、版本、项目、JD 和分析结果也必须归属于当前用户。

### V0.4 AI 用量与额度

V0.4 新增 AI 调用日志和基础额度系统，但不实现支付、会员、订单或管理员后台。

- AI 调用日志写入 `ai_usage_logs`，按 `user_id` 隔离。
- 记录功能类型、模型、成功/失败、错误信息、token usage 和估算成本字段。
- 额度配置来自 `.env`：`AI_MONTHLY_CALL_LIMIT`、`AI_INPUT_TOKEN_PRICE_PER_1K`、`AI_OUTPUT_TOKEN_PRICE_PER_1K`。
- 五个 AI 功能在 service 层接入用量记录：JD 分析、匹配报告、定制简历、真实性检测、面试追问。
- `/usage/summary` 为当前用户返回本月用量、剩余额度、功能分布和最近调用记录。
- 额度耗尽时在调用模型前返回 `429 Monthly AI quota exceeded.`。

## 10. 后续商业化扩展点

- `BillingService`：会员、套餐、支付。
- `ExportService`：PDF、Word、多模板导出。
- `ProviderRegistry`：多 AI 模型和供应商管理。
- `AuthService`：当前已支持基础注册、登录、JWT，后续可扩展 OAuth、Refresh Token、会话管理和找回密码。
- `UsageTrackingService`：V0.4 已支持基础调用次数、额度、成本字段预留，后续可扩展套餐和精细化计费。

### V0.5 个人中心与账户设置

V0.5 新增账户聚合能力和前端个人中心页面，但不改变数据库核心结构，也不实现支付、会员套餐、订单、管理员后台、密码修改或头像上传。

后端新增账户接口：

- `GET /account/me`
  - 需要 JWT Bearer Token。
  - 通过 `get_current_user` 获取当前登录用户。
  - 返回 `id`、`email`、`display_name`、`status`、`created_at`、`updated_at` 和 `usage_summary`。
  - `usage_summary` 复用 V0.4 `AIUsageService`，不重复实现统计逻辑。

- `PATCH /account/me`
  - 需要 JWT Bearer Token。
  - 只允许修改当前用户自己的 `display_name`。
  - 不允许修改 `email`、`status`、`password_hash`、角色或额度字段。

前端新增 `/account` 页面：

- 展示账户信息与 V0.4 用量概览。
- 支持修改昵称，保存成功后同步更新页面和 Sidebar 当前用户名称。
- 提供跳转 `/usage` 的入口，用于查看详细 AI 用量。
- 商业化入口仅为静态预留说明，不包含支付、会员或订单流程。

### V0.6 管理后台基础版

V0.6 新增轻量管理后台，用于查看用户基础信息和 AI 用量概览，并进行账号启用 / 禁用管理。本阶段不实现支付、会员套餐、订单、发票、复杂 RBAC、操作审计、删除用户或修改用户密码。

管理员识别：

- 复用 `users` 表，新增 `role` 字段。
- `role='admin'` 的用户可访问后台接口。
- `role='user'` 的普通用户访问 `/admin/*` 返回 `403`。
- 继续使用 `status='active'` 判断账号是否可登录和调用业务接口。
- 禁用用户后，登录会失败；已有 token 调用业务接口也会返回 `401`。

后端接口：

- `GET /admin/users`：用户列表，支持分页和按 email / display_name 搜索。
- `GET /admin/users/{user_id}`：用户详情，返回账户基础信息和 `usage_summary`。
- `PATCH /admin/users/{user_id}/status`：启用 / 禁用用户，禁止管理员禁用自己。
- `GET /admin/usage/summary`：全站 AI 用量概览。

前端页面：

- 新增 `/admin`。
- Sidebar 仅 admin 用户显示“管理后台”入口。
- 前端隐藏入口只是体验优化，真正权限由后端接口校验。
- 后台不展示用户简历正文、项目正文、JD 原文或 AI 生成内容，避免过早暴露敏感求职资料。
- `TemplateService`：简历模板和样式。
- `ApplicationTracker`：投递进度管理。
## V0.7 DOCX 导出架构补充

V0.7 新增 DOCX 简历导出能力，但不改变 AI 生成链路和数据库核心结构。

后端导出流程：

```text
GET /resume-versions/{id}/export/docx
        |
        v
get_current_user
        |
        v
ResumeVersionRepository.get_by_id_for_user
        |
        v
ExportService / python-docx
        |
        v
DOCX bytes Response
```

## V0.8 DOCX 模板架构补充

V0.8 在 V0.7 DOCX 导出链路上增加模板参数与模板渲染器，但不改变权限、AI、用量和数据库结构。

后端导出流程：

```text
GET /resume-versions/{id}/export/docx?template=modern
        |
        v
FastAPI Query 校验 template
        |
        v
get_current_user
        |
        v
ResumeVersionRepository.get_by_id_for_user
        |
        v
ExportService
        |
        v
MarkdownBlock parser
        |
        v
DocxTemplateRenderer registry
        |
        v
DOCX bytes Response
```

模板设计：

- `standard`：默认模板，保持 V0.7 简洁版式。
- `modern`：更强标题层级、更舒适段落间距和轻量强调色。
- `compact`：更小字号和更紧凑间距，适合压缩页数。

关键约束：

- 支持模板集合固定为 `standard`、`modern`、`compact`。
- 不传 `template` 时默认 `standard`。
- 非法模板由请求参数校验返回 `422`。
- 模板渲染只消费 `ResumeVersion.content_markdown`。
- 导出不调用 `AIClient`，不调用 `AIUsageService`。
- 文件继续以内存流返回，不长期保存到公开目录。
- 权限仍按当前登录用户校验 ResumeVersion 归属。
```

关键约束：

- DOCX 内容只来自 `ResumeVersion.content_markdown`。
- 导出过程不调用 `AIClient`。
- 导出过程不调用 `AIUsageService`，不计入 AI 使用额度。
- 导出结果使用内存流返回，不长期保存文件。
- 权限沿用 V0.3 用户隔离，用户只能导出自己的 ResumeVersion。
- Markdown 导出接口继续保留。

当前边界：

- PDF 导出暂未实现。
- 不做模板选择 UI。
- 不做导出历史表。
- 不新增支付、会员、订单或在线 Word 预览能力。

### V0.8 边界更新说明

V0.7 文档中“暂不提供模板选择 UI”的边界已在 V0.8 解除：当前 `/versions` 页面已支持 `standard`、`modern`、`compact` 三种 DOCX 模板选择。其余边界仍保持不变：不做 PDF 导出、不做在线 Word 预览、不做复杂模板编辑器、不做导出历史、不新增数据库表。
