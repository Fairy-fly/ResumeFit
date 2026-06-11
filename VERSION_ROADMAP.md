# ResumeFit Version Roadmap

本文档记录 ResumeFit 从 Demo MVP 到产品化基础版的版本演进，用于后续开发规划、验收对照和项目展示。

## 1. 项目版本线总览

当前稳定版本线：

- `v0.1-demo-mvp`
- `v0.2-product-experience`
- `v0.3-multi-user`
- `v0.4-ai-usage-quota`
- `v0.5-account-center`

当前最新稳定版本：`v0.5-account-center`

## 2. 各版本完成内容

### v0.1-demo-mvp

完成 ResumeFit 的核心 Demo 闭环：

- Dashboard 首页流程。
- 通用简历输入。
- 项目库管理。
- 岗位 JD 分析。
- 简历与岗位匹配度报告。
- 定制简历生成。
- 真实性风险检测。
- 面试追问预测。
- Markdown 导出。

核心边界：

- 重点验证从“用户资料输入”到“定制简历生成与导出”的主流程。
- AI service 使用 OpenAI-compatible 抽象，默认可接 DeepSeek。
- Prompt 放在 `prompts/` 目录。
- 数据使用 SQLite。

未做内容：

- 不做登录注册。
- 不做多用户隔离。
- 不做支付、会员、订单。
- 不做招聘网站爬取。
- 不做 PDF/Word 导出。
- 不做企业后台。

### v0.2-product-experience

完成产品化体验优化：

- `/versions` 页面组件拆分。
- 历史版本回填 Markdown 预览。
- 复制和导出作用于当前选中 ResumeVersion。
- 历史内容详情查看。
- 空状态与下一步 CTA。
- 加载状态与防重复点击。
- 错误提示产品化。
- 历史记录体验优化。
- Dashboard 产品化引导。
- 固定左侧 Sidebar。
- 历史列表和选择区折叠。
- 修改原因卡片展示优化。

核心边界：

- 只优化前端体验和演示可用性。
- 不改变 AI 调用逻辑。
- 不改变数据库核心结构。
- 不新增商业化功能。

未做内容：

- 不做登录注册。
- 不做支付、会员、订单。
- 不做 PDF/Word 导出。
- 不做招聘网站爬取。
- 不做管理员后台。

### v0.3-multi-user

完成多用户基础能力：

- 用户注册。
- 用户登录。
- JWT Bearer Token 鉴权。
- `/auth/me` 当前用户接口。
- 前端登录页、注册页、退出登录。
- token 保存到 localStorage。
- API 请求自动携带 Authorization。
- 未登录路由拦截。
- 登录/注册页独立布局。
- 用户数据隔离：
  - `/resume-profiles`
  - `/projects`
  - `/job-descriptions`
  - `/match-reports`
  - `/resume-versions`
  - Markdown 导出
  - `/truth-check-results`
  - `/interview-question-results`

核心边界：

- 将原 Demo 固定 `user_id = 1` 逐步替换为当前登录用户。
- 用户之间的简历、项目、JD、报告、版本、真实性检测、面试追问互不可见。
- 继续使用 SQLite 和轻量迁移方式。

未做内容：

- 不做 refresh token。
- 不做邮箱验证。
- 不做找回密码。
- 不做第三方登录。
- 不做支付、会员、订单。
- 不做复杂权限系统。

### v0.4-ai-usage-quota

完成 AI 使用次数、调用日志、成本字段预留与基础额度：

- 新增 `ai_usage_logs` 表。
- 新增 `GET /usage/summary`。
- 五个 AI 调用点接入日志与额度检查：
  - JD 分析。
  - 匹配报告。
  - 定制简历生成。
  - 真实性风险检测。
  - 面试追问预测。
- 支持 `AI_MONTHLY_CALL_LIMIT`。
- 超过额度返回 `429 Monthly AI quota exceeded.`。
- 超额时不调用模型。
- 前端新增 `/usage` 页面。
- Sidebar 新增“用量统计”入口。

核心边界：

- 按用户统计 AI 调用次数。
- 记录功能类型、模型、成功/失败、错误信息、token usage 和 estimated cost 字段。
- token usage 或成本拿不到时允许为空。
- 为商业化做数据基础，但不做真实计费。

未做内容：

- 不做支付。
- 不做会员套餐。
- 不做订单。
- 不做管理员后台。
- 不做发票。
- 不做复杂账单系统。

### v0.5-account-center

完成个人中心与账户设置基础能力：

- 新增 `/account` 个人中心页面。
- 新增 `GET /account/me`。
- 新增 `PATCH /account/me`。
- 个人中心展示：
  - `email`
  - `display_name`
  - `status`
  - `created_at`
  - `updated_at`
  - `usage_summary`
- 支持修改当前用户自己的 `display_name`。
- 修改昵称后页面和 Sidebar 同步更新。
- 展示 V0.4 用量概览。
- 可跳转 `/usage` 查看详细用量。
- 商业化入口仅做静态预留说明。

核心边界：

- 只做账户展示和昵称修改。
- 复用 V0.4 `usage_summary`。
- 不新增账户设置表。
- 不允许修改 email、status、password_hash、角色或额度字段。

未做内容：

- 不做支付。
- 不做会员套餐。
- 不做订单。
- 不做管理员后台。
- 不做密码修改。
- 不做邮箱验证。
- 不做找回密码。
- 不做头像上传。

## 3. 当前最新稳定版本说明

当前最新稳定版本为：`v0.5-account-center`。

该版本已经具备：

- 可演示的完整求职辅助主流程。
- 产品化基础交互体验。
- 多用户注册登录和数据隔离。
- AI 用量统计和基础月额度。
- 个人中心和昵称设置。

该版本适合：

- 课程项目展示。
- Demo 答辩。
- 小范围体验测试。
- 后续商业化功能规划的基础版本。

## 4. 当前技术栈

- 前端：Vue 3
- 后端：FastAPI
- 数据库：SQLite
- 鉴权：JWT Bearer Token
- AI 接口：OpenAI-compatible API
- 默认 AI 供应商配置：DeepSeek API
- Prompt 管理：`prompts/` 目录
- 导出能力：Markdown 导出
- 测试：pytest、npm build

## 5. 当前已具备的产品能力

用户与账户：

- 注册。
- 登录。
- 退出登录。
- 当前用户信息。
- 个人中心。
- 修改昵称。
- 用户数据隔离。

求职辅助主流程：

- 通用简历输入。
- 项目库管理。
- 岗位 JD 输入与分析。
- 匹配度报告。
- 定制简历生成。
- 真实性风险检测。
- 面试追问预测。
- Markdown 导出。

AI 与额度：

- 统一 AIClient。
- OpenAI-compatible 接口。
- AI 调用日志。
- 月度调用额度。
- 用量统计页面。
- 额度耗尽提示。

产品体验：

- Dashboard 流程引导。
- 空状态和下一步 CTA。
- 加载状态和防重复点击。
- 友好错误提示。
- 历史版本选择。
- 折叠区与详情弹窗。

## 6. 后续 V0.6 推荐方向

推荐 V0.6 做“管理后台基础版”，继续为商业化做准备，但仍不直接实现支付和真实会员扣费。

建议功能：

- 管理后台基础页面。
- 用户列表。
- 查看用户注册时间、状态和基础资料。
- 查看用户 AI 用量。
- 查看用户最近调用记录。
- 账号状态管理，例如启用 / 禁用。
- 管理员登录入口可以先复用现有用户体系，后续再扩展角色权限。

V0.6 建议边界：

- 不做支付。
- 不做真实会员扣费。
- 不做订单系统。
- 不做发票。
- 不做复杂权限系统。
- 不做多租户组织管理。
- 不做招聘网站爬取。
- 不做 PDF/Word 导出。

V0.6 设计原则：

- 后台能力先保持只读和轻量管理。
- 不破坏 V0.3 用户隔离。
- 不破坏 V0.4 用量统计。
- 不破坏 V0.5 个人中心体验。
- 对管理员能力预留扩展点，但不要过早实现复杂商业系统。
