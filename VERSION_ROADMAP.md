# ResumeFit Version Roadmap

本文档记录 ResumeFit 从 Demo MVP 到产品化、多用户、用量统计、个人中心和管理后台基础版的版本演进。它用于帮助答辩、验收、后续开发和 Git 标签管理。

## 1. 项目版本线总览

- `v0.1-demo-mvp`
- `v0.2-product-experience`
- `v0.3-multi-user`
- `v0.4-ai-usage-quota`
- `v0.5-account-center`
- `v0.6-admin-basic`
- `v0.7-docx-export`

当前最新稳定版本：`v0.7-docx-export`

## 2. 各版本完成内容与能力边界

### v0.1-demo-mvp

完成内容：

- Dashboard 演示流程。
- 通用简历输入。
- 项目库管理。
- 岗位 JD 分析。
- 匹配度报告。
- 定制简历生成。
- 真实性风险检测。
- 面试追问预测。
- Markdown 导出。

核心能力边界：

- 跑通求职辅助主流程。
- 后端使用 FastAPI + SQLite。
- 前端使用 Vue 3。
- AI 使用统一 `AIClient`，默认 DeepSeek OpenAI-compatible API。
- Demo 阶段固定用户数据，优先验证功能闭环。

没有做：

- 登录注册。
- 多用户隔离。
- 支付、会员、订单。
- 招聘网站爬取。
- PDF/Word 导出。

### v0.2-product-experience

完成内容：

- 固定左侧 Sidebar。
- 历史内容详情查看。
- 历史内容折叠。
- `/versions` 页面组件拆分。
- 历史 ResumeVersion 回填 Markdown 预览。
- 复制和导出作用于当前选中版本。
- `/versions` 生成上下文折叠。
- 修改原因卡片优化。
- 空状态与下一步 CTA。
- 加载状态与防重复点击。
- 错误提示产品化。
- 历史记录体验优化。
- Dashboard 产品化引导。

核心能力边界：

- 不新增大业务功能。
- 专注让 V0.1 从课程 Demo 更接近可用产品。
- 保留所有已有主流程。

没有做：

- 登录注册。
- 多用户隔离。
- 支付、会员、订单。
- 招聘网站爬取。
- PDF/Word 导出。

### v0.3-multi-user

完成内容：

- 后端注册、登录、JWT、当前用户接口。
- 前端登录、注册、退出登录。
- token 保存到 localStorage。
- API 自动携带 `Authorization: Bearer <token>`。
- 未登录路由拦截。
- 登录/注册页独立布局。
- `/resume-profiles` 用户隔离。
- `/projects` 用户隔离。
- `/job-descriptions` 用户隔离。
- `/match-reports` 用户隔离。
- `/resume-versions` 用户隔离。
- Markdown 导出用户隔离。
- `/truth-check-results` 用户隔离。
- `/interview-question-results` 用户隔离。

核心能力边界：

- 不同用户之间的简历、项目、JD、报告、版本、真实性检测、面试追问互不可见。
- 用户不能通过 ID 操作别人的数据。
- 禁止明文密码存储。
- JWT Secret 从环境变量读取。

没有做：

- refresh token。
- 邮箱验证。
- 找回密码。
- 第三方登录。
- 支付、会员、订单。
- 复杂权限系统。

### v0.4-ai-usage-quota

完成内容：

- 新增 `ai_usage_logs` 表。
- 新增 AI 使用日志 repository/service/schema。
- 新增 `GET /usage/summary`。
- 五个 AI 调用点接入日志与额度：
  - JD 分析。
  - 匹配报告。
  - 定制简历生成。
  - 真实性风险检测。
  - 面试追问预测。
- 新增 `AI_MONTHLY_CALL_LIMIT` 基础月额度。
- 超额时返回 `429 Monthly AI quota exceeded.`。
- 超额时不调用模型，不生成新的业务结果。
- 前端新增 `/usage` 页面。
- Sidebar 新增“用量统计”。
- 额度耗尽错误转成友好中文提示。

核心能力边界：

- 为后续商业化准备调用日志、额度和成本统计基础。
- 按用户隔离用量统计。
- 记录成功/失败、功能类型、模型、错误信息、token usage 和估算成本字段。

没有做：

- 支付。
- 会员套餐。
- 订单。
- 发票。
- 管理后台。
- 真实扣费。

### v0.5-account-center

完成内容：

- 后端新增账户接口：
  - `GET /account/me`
  - `PATCH /account/me`
- `/account/me` 返回账户信息和 `usage_summary`。
- 只允许修改当前用户自己的 `display_name`。
- 修改昵称后 `/auth/me` 同步返回新昵称。
- 前端新增 `/account` 个人中心页面。
- 个人中心展示：
  - email
  - display_name
  - status
  - created_at
  - updated_at
  - usage_summary
- 支持修改昵称。
- 修改昵称后 Sidebar 同步更新。
- 展示 V0.4 用量概览。
- 可跳转 `/usage` 查看详细用量。
- 商业化入口仅为静态预留说明。

核心能力边界：

- 允许用户查看自己的账户信息和用量概览。
- 允许用户修改昵称。
- 不允许用户修改 email、status、role、quota、password_hash。

没有做：

- 支付。
- 会员套餐。
- 订单。
- 管理员后台。
- 密码修改。
- 邮箱验证。
- 找回密码。
- 头像上传。

### v0.6-admin-basic

完成内容：

- 完成管理后台基础版。
- `users` 表新增 `role` 字段，支持 `user` / `admin`。
- SQLite 轻量迁移补齐 `users.role`，旧用户默认 `role='user'`。
- 新增 `get_current_admin_user`。
- 普通用户访问 `/admin/*` 返回 `403`。
- 新增后台接口：
  - `GET /admin/users`
  - `GET /admin/users/{user_id}`
  - `PATCH /admin/users/{user_id}/status`
  - `GET /admin/usage/summary`
- 前端新增 `/admin` 管理后台页面。
- Sidebar 仅 admin 用户显示“管理后台”。
- `/auth/me`、登录、注册返回用户 `role`。
- 禁用用户后不能登录。
- 禁用用户旧 token 也不能继续调用业务接口。
- 后台用户列表支持分页和按 email / display_name 搜索。
- 后台用户详情展示账户信息、用量概览和最近 AI 调用记录。
- 后台支持启用 / 禁用用户，但不允许 admin 禁用自己。

核心能力边界：

- 管理员可以查看用户列表、用户详情和全站 AI 用量概览。
- 管理员可以启用或禁用用户。
- 后台接口必须登录且必须 admin。
- 前端隐藏管理入口只是体验优化，真正权限以后端 `/admin/*` 为准。
- 后台响应不返回 `password_hash`、token 或真实密钥。

验收结果：

- 后端测试：`84 passed, 3 warnings`
- 前端 `npm run build`：通过

没有做：

- 支付。
- 会员套餐。
- 订单。
- 发票。
- 复杂 RBAC。
- 多管理员协作。
- 操作审计日志。
- 删除用户。
- 修改用户密码。
- 头像上传。
- 招聘网站爬取。
- PDF/Word 导出。

### v0.7-docx-export

完成内容：

- 新增 DOCX 简历导出增强版。
- 后端新增接口：
  - `GET /resume-versions/{id}/export/docx`
- 使用 `python-docx` 基于 `ResumeVersion.content_markdown` 生成 DOCX。
- DOCX 导出使用内存流返回，不长期保存文件。
- DOCX 导出不调用 AI。
- DOCX 导出不计入 AI 使用额度。
- DOCX 导出沿用 V0.3 用户隔离。
- 用户只能导出自己的 ResumeVersion。
- 前端 `/versions` 页面新增“导出 DOCX”按钮。
- Markdown 导出继续保留。

核心能力边界：

- DOCX 内容来源是已经保存的 `ResumeVersion.content_markdown`。
- 导出接口需要登录，并按当前用户 id 校验 ResumeVersion 归属。
- 文件名来自后端 `Content-Disposition`，不包含 token、email、用户 id 等敏感信息。
- 导出文件即时返回，不保存到公开目录。

验收结果：

- 后端测试：`88 passed, 3 warnings`
- 前端 `npm run build`：通过

没有做：

- PDF 导出。
- 模板选择 UI。
- 导出历史。
- 新数据库表。
- 支付。
- 会员套餐。
- 订单。
- 在线 Word 预览。
- 招聘网站爬取。
- 头像上传。

## 3. 当前最新稳定版本说明

当前最新稳定版本为：`v0.7-docx-export`。

该版本已经具备：

- 完整求职辅助主流程。
- 产品化前端体验。
- 多用户注册登录。
- JWT 鉴权。
- 用户数据隔离。
- AI 调用日志。
- 基础月额度限制。
- 用量统计页面。
- 个人中心。
- 管理后台基础版。
- DOCX 简历导出。

适合用于：

- 课程答辩。
- 项目展示。
- 本地 Demo。
- 后续商业化功能的基础版本。
- 后续后台运营能力的起点。

## 4. 当前技术栈

前端：

- Vue 3
- TypeScript
- Vite
- Vue Router
- 原生 CSS / 组件化页面结构

后端：

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT Bearer Token
- bcrypt / passlib 风格密码哈希

AI：

- 统一 `AIClient`
- OpenAI-compatible Chat Completions
- 默认 DeepSeek
- Prompt 文件统一放在 `prompts/`

数据与权限：

- `users`
- `resume_profiles`
- `projects`
- `job_descriptions`
- `job_analyses`
- `match_reports`
- `resume_versions`
- `truth_check_results`
- `interview_question_results`
- `ai_usage_logs`
- `user/admin` 轻量角色

## 5. 当前已具备的产品能力

求职主流程：

- 输入通用简历。
- 添加项目经历。
- 粘贴并分析岗位 JD。
- 生成匹配度报告。
- 生成定制简历。
- 检测真实性风险。
- 预测面试追问。
- 导出 Markdown 简历。
- 导出 DOCX 简历。

多用户能力：

- 注册。
- 登录。
- 退出登录。
- 当前用户信息。
- 前端路由鉴权。
- 后端 JWT 鉴权。
- 用户数据隔离。

用量能力：

- AI 调用日志。
- 本月调用次数。
- 剩余额度。
- 功能分布。
- 最近调用记录。
- 超额拦截。

账户能力：

- 个人中心。
- 查看账户信息。
- 修改昵称。
- 查看用量概览。
- 跳转详细用量页。

管理后台能力：

- admin 角色识别。
- 用户列表。
- 用户搜索。
- 用户详情。
- 用户启用 / 禁用。
- 全站 AI 用量概览。
- 禁用用户访问拦截。

导出能力：

- Markdown 导出。
- DOCX 导出。
- 导出权限按当前用户隔离。
- DOCX 导出不调用 AI、不消耗 AI 额度。

## 6. 后续 V0.8 推荐方向

推荐方向：导出体验与后台可观测增强。

可以考虑：

- PDF 导出。
- 简历导出模板选择。
- DOCX 排版增强。
- 更详细的后台用量趋势。
- 按用户查看功能调用分布。
- 最近失败 AI 调用列表。
- 后台错误诊断页面。
- 管理员手动调整用户月额度。
- 更完整的管理后台验收文档。

继续暂缓：

- 支付。
- 真实会员扣费。
- 订单。
- 发票。
- 复杂 RBAC。
- 多租户组织。
- 操作审计日志。
- 删除用户。
- 修改用户密码。
- 在线 Word 预览。

## 7. 版本维护建议

- 每个稳定阶段都创建 Git tag。
- 每个版本完成后更新验收清单。
- 业务功能、权限能力、商业化能力分阶段推进。
- 不要为了提前商业化而破坏当前清晰的主流程。
- 管理后台可以逐步增强，但 V0.6 只保留轻量后台边界。
