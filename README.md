# ResumeFit

## 项目简介

ResumeFit 是一款基于大语言模型的智能简历定制与求职辅助平台。当前阶段目标是先完成可演示 Demo，验证核心求职辅助链路；后续再逐步演进为可商业化的软件产品。

## 产品定位

ResumeFit 面向正在求职、转岗、实习申请或希望提升简历匹配度的个人用户。系统帮助用户把一份通用简历、项目经历和目标岗位 JD 结合起来，完成岗位分析、匹配度评分、定制简历生成、真实性风险提示和面试追问预测。

产品原则：

- 先 Demo：优先跑通从输入简历到生成岗位定制版本的核心闭环。
- 后商业化：架构预留用户体系、版本管理、导出能力、模型切换和数据库升级空间。
- 不编造经历：系统只能基于用户提供的信息改写、组织和强调，不能创造不存在的工作、项目、成果、学历或证书。
- 可替换 AI：MVP 默认使用 DeepSeek API，但 AI 服务层必须遵循 OpenAI-compatible 结构，避免与单一供应商强绑定。

## 功能列表

1. 通用简历输入
2. 项目库管理
3. 岗位 JD 分析
4. 简历匹配度评分
5. 岗位定制简历生成
6. 真实性风险检测
7. 面试追问预测
8. 多版本简历管理
9. Markdown 导出

## 技术栈

- 前端：Vue 3
- 后端：FastAPI
- 数据库：SQLite
- AI 接口：OpenAI-compatible API
- Prompt 管理：`prompts/` 目录

## 启动方式

### 0. 环境要求

- Python 3.11+
- Node.js 18.18+ 或 Node.js 20 LTS+
- PowerShell

### 1. 配置环境变量

在项目根目录复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

`.env` 中的 `AI_API_KEY` 只填写本地真实值，不要提交到仓库。

JD 分析模块默认使用 DeepSeek 的 OpenAI-compatible 接口，配置项如下：

```text
AI_PROVIDER=deepseek
AI_BASE_URL=https://api.deepseek.com
AI_API_KEY=your_deepseek_api_key_here
AI_MODEL=deepseek-chat
```

如果没有配置真实 `AI_API_KEY`，后端会在调用分析接口时返回明确错误提示。

### 2. 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

如果 PowerShell 阻止激活虚拟环境，可在当前终端临时放宽执行策略：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

健康检查：

```powershell
Invoke-RestMethod http://localhost:8000/health
```

### 3. 启动前端

新开一个 PowerShell 终端：

```powershell
cd frontend
npm install
npm run dev
```

默认前端地址：

```text
http://localhost:5173
```

### 4. 运行后端测试

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest
```

### 5. 验证前端构建

```powershell
cd frontend
npm install
npm run build
```

## 测试命令

后端自动测试：

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

前端构建验证：

```powershell
cd frontend
npm run build
```

验收前建议同时保留 `python -m pytest` 和 `npm run build` 的通过截图，用于答辩 PPT 或项目报告。

## Demo 演示顺序

建议从首页开始演示。打开 `http://localhost:5173/` 后，首页会展示 8 步流程、当前数据统计和各功能入口。

1. 在首页确认流程和统计数据。
2. 进入 `/resume`，填写通用简历。
3. 进入 `/projects`，添加真实项目经历。
4. 进入 `/jobs`，粘贴岗位 JD 并生成岗位分析。
5. 进入 `/analysis`，选择简历、项目和已分析 JD，生成匹配度报告。
6. 进入 `/versions`，选择匹配报告并生成 Markdown 定制简历。
7. 在 `/versions` 完成真实性风险检测。
8. 在 `/versions` 生成面试追问预测。
9. 在 `/versions` 导出 Markdown 文件。

首页统计接口只返回数量，不返回简历正文、项目内容或 JD 原文：

```powershell
Invoke-RestMethod http://localhost:8000/dashboard/summary
```

## 项目验收与答辩材料

- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)：项目总结，适合放入课程报告或项目说明。
- [DEFENSE_SCRIPT.md](DEFENSE_SCRIPT.md)：答辩讲稿，适合现场口头汇报。
- [DEMO_GUIDE.md](DEMO_GUIDE.md)：Demo 演示步骤，适合演示前准备和现场备用。
- [SCREENSHOT_CHECKLIST.md](SCREENSHOT_CHECKLIST.md)：PPT 或报告建议截图清单。
- [PPT_OUTLINE.md](PPT_OUTLINE.md)：12 页左右答辩 PPT 大纲。
- [ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md)：提交前验收检查表。
- [V0.4_ACCEPTANCE_CHECKLIST.md](V0.4_ACCEPTANCE_CHECKLIST.md)：AI 用量与基础额度验收清单。
- [V0.5_ACCEPTANCE_CHECKLIST.md](V0.5_ACCEPTANCE_CHECKLIST.md)：个人中心与账户设置验收清单。
- [V0.6_ACCEPTANCE_CHECKLIST.md](V0.6_ACCEPTANCE_CHECKLIST.md)：管理后台基础版验收清单。

## 通用简历输入模块测试

### API 测试

启动后端后，保存一份通用简历：

```powershell
Invoke-RestMethod http://localhost:8000/resume-profiles `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"title":"后端开发通用简历","raw_markdown":"# 我的简历"}'
```

查询已保存简历列表：

```powershell
Invoke-RestMethod http://localhost:8000/resume-profiles
```

### 页面测试

1. 启动后端。
2. 启动前端。
3. 打开 `http://localhost:5173/resume`。
4. 输入简历标题和简历正文。
5. 点击“保存简历”。
6. 确认页面下方出现已保存简历。
7. 刷新页面，确认简历列表仍然存在。

## 项目库模块测试

### API 测试

启动后端后，保存一个项目：

```powershell
Invoke-RestMethod http://localhost:8000/projects `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"name":"ResumeFit Demo","project_type":"Web 应用","role":"独立开发","tech_stack":["Vue 3","FastAPI","SQLite"],"description":"智能简历定制平台 Demo","user_contribution":"负责项目库模块设计与实现","work_url":"https://example.com"}'
```

查询已保存项目列表：

```powershell
Invoke-RestMethod http://localhost:8000/projects
```

### 页面测试

1. 启动后端。
2. 启动前端。
3. 打开 `http://localhost:5173/projects`。
4. 输入项目名称、项目类型、我的角色、技术栈、项目描述、个人贡献和作品链接。
5. 点击“保存项目”。
6. 确认页面下方出现已保存项目。
7. 刷新页面，确认项目列表仍然存在。

### Demo SQLite 重置

如果你已经在旧字段结构下启动过后端，SQLite 中的 `projects` 表不会自动增加新字段。Demo 阶段可以删除本地数据库后重启后端，让应用重新创建表：

```powershell
Remove-Item backend/resumefit.db -ErrorAction SilentlyContinue
```

## 岗位 JD 分析模块测试

### API 测试

启动后端并确认 `.env` 中已配置真实 `AI_API_KEY` 后，先保存一个 JD：

```powershell
Invoke-RestMethod http://localhost:8000/job-descriptions `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"company_name":"示例公司","job_title":"后端开发工程师","raw_text":"负责 FastAPI 服务开发，熟悉 SQL、缓存和云服务。"}'
```

再调用分析接口：

```powershell
Invoke-RestMethod http://localhost:8000/job-descriptions/1/analyze -Method Post
```

查询已保存 JD 列表：

```powershell
Invoke-RestMethod http://localhost:8000/job-descriptions
```

### 页面测试

1. 启动后端。
2. 启动前端。
3. 打开 `http://localhost:5173/jobs`。
4. 输入公司名称、岗位名称和 JD 原文。
5. 点击“保存并分析”。
6. 确认页面显示岗位概览、必备技能、加分技能、关键词、岗位职责和简历侧重点。
7. 刷新页面，确认已保存 JD 列表仍然存在。

### Demo SQLite 重置

如果你已经在旧结构下创建过 `job_descriptions` 或 `job_analyses` 表，Demo 阶段可以删除本地数据库后重启后端：

```powershell
Remove-Item backend/resumefit.db -ErrorAction SilentlyContinue
```

## 简历与岗位匹配度报告模块测试

### API 测试

启动后端并确认 `.env` 中已配置真实 `AI_API_KEY` 后，先确保已经存在：

- 至少一份通用简历。
- 至少一个项目。
- 一个已完成分析的 JD。

生成匹配报告：

```powershell
Invoke-RestMethod http://localhost:8000/match-reports `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"resume_profile_id":1,"project_ids":[1],"job_description_id":1}'
```

返回结果会包含匹配分数、优势、不足、缺失关键词、修改建议和真实性提醒。测试或演示时如果 JD 还没有分析，接口会提示先完成 JD 分析。

### 页面测试

1. 启动后端。
2. 启动前端。
3. 确认 `/resume` 中已有简历，`/projects` 中已有项目，`/jobs` 中已有已分析 JD。
4. 打开 `http://localhost:5173/analysis`。
5. 选择一份简历、一个或多个项目、一个已分析 JD。
6. 点击“生成匹配报告”。
7. 确认页面显示匹配分数、优势、不足、缺失关键词、修改建议和真实性提醒。

### Demo SQLite 重置

如果你已经在旧结构下创建过 `match_reports` 表，Demo 阶段可以删除本地数据库后重启后端：

```powershell
Remove-Item backend/resumefit.db -ErrorAction SilentlyContinue
```

## 定制简历生成模块测试

### API 测试

启动后端并确认 `.env` 中已配置真实 `AI_API_KEY` 后，先确保已经存在：

- 至少一份通用简历。
- 至少一个项目。
- 一个已完成分析的 JD。
- 一个与所选简历、项目和 JD 一致的匹配报告。

生成定制简历：

```powershell
Invoke-RestMethod http://localhost:8000/resume-versions/generate `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"resume_profile_id":1,"project_ids":[1],"job_description_id":1,"match_report_id":1}'
```

返回结果会包含 Markdown 简历正文、修改原因、使用模型、版本类型和关联 ID。接口只生成 Markdown，不会导出 PDF 或 Word。

导出某个简历版本为 Markdown 文件：

```powershell
Invoke-WebRequest http://localhost:8000/resume-versions/1/export/markdown `
  -OutFile ResumeFit_export.md
```

接口会返回 `text/markdown` 内容，并通过 `Content-Disposition` 提供 `.md` 下载文件名。导出只读取已保存的 `ResumeVersion.content_markdown`，不会调用 AI。

### 页面测试

1. 启动后端。
2. 启动前端。
3. 确认 `/resume` 中已有简历，`/projects` 中已有项目，`/jobs` 中已有已分析 JD，`/analysis` 中已有匹配报告。
4. 打开 `http://localhost:5173/versions`。
5. 选择一个匹配报告，页面会带出对应简历、项目和 JD。
6. 点击“生成定制简历”。
7. 确认页面显示 Markdown 简历和修改原因。
8. 点击“复制 Markdown”，确认复制成功。
9. 点击“导出 Markdown”，确认浏览器下载 `.md` 文件。

### Demo SQLite 重置

如果你已经在旧结构下创建过 `resume_versions` 表，Demo 阶段可以删除本地数据库后重启后端：

```powershell
Remove-Item backend/resumefit.db -ErrorAction SilentlyContinue
```

## 真实性风险检测模块测试

### API 测试

启动后端并确认 `.env` 中已配置真实 `AI_API_KEY` 后，先确保已经存在一份已生成的定制简历版本。

查询已生成版本：

```powershell
Invoke-RestMethod http://localhost:8000/resume-versions
```

生成真实性风险检测结果：

```powershell
Invoke-RestMethod http://localhost:8000/truth-check-results `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"resume_version_id":1}'
```

查询某个版本的历史检测结果：

```powershell
Invoke-RestMethod "http://localhost:8000/truth-check-results?resume_version_id=1"
```

返回结果会包含总体风险等级、风险表达、风险类型、风险原因、证据状态、更稳妥改法、缺失证据、面试追问风险点和总结。`interview_risk_points` 只提示风险点，不生成完整面试追问问题。

### 页面测试

1. 启动后端。
2. 启动前端。
3. 确认 `/versions` 中已有至少一个定制简历版本。
4. 打开 `http://localhost:5173/versions`。
5. 在“真实性风险检测”区域选择一个简历版本。
6. 点击“检测真实性风险”。
7. 确认页面显示风险等级、风险表达、风险原因、证据状态、更稳妥改法和面试追问风险点。

### Demo SQLite 重置

如果你已经在旧结构下启动过后端，SQLite 中可能没有 `truth_check_results` 表。Demo 阶段可以删除本地数据库后重启后端：

```powershell
Remove-Item backend/resumefit.db -ErrorAction SilentlyContinue
```

## 面试追问预测模块测试

### API 测试

启动后端并确认 `.env` 中已配置真实 `AI_API_KEY` 后，先确保已经存在一份已生成的定制简历版本。真实性风险检测结果不是必须项；如果存在，后端会读取最新一次检测结果作为追问预测上下文。

查询已生成版本：

```powershell
Invoke-RestMethod http://localhost:8000/resume-versions
```

生成面试追问预测结果：

```powershell
Invoke-RestMethod http://localhost:8000/interview-question-results `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"resume_version_id":1}'
```

查询某个版本的历史追问预测：

```powershell
Invoke-RestMethod "http://localhost:8000/interview-question-results?resume_version_id=1"
```

返回结果会包含面试问题、为什么会问、关联简历内容、难度、建议回答、回答策略、风险提醒和总结。

### 页面测试

1. 启动后端。
2. 启动前端。
3. 确认 `/versions` 中已有至少一个定制简历版本。
4. 打开 `http://localhost:5173/versions`。
5. 在“真实性风险检测”区域选择一个简历版本。
6. 在“面试追问预测”区域点击“生成面试追问”。
7. 确认页面显示问题、原因、关联内容、难度、建议回答、回答策略和风险提醒。

### Demo SQLite 重置

如果你已经在旧结构下启动过后端，SQLite 中可能没有 `interview_question_results` 表。Demo 阶段可以删除本地数据库后重启后端：

```powershell
Remove-Item backend/resumefit.db -ErrorAction SilentlyContinue
```

## 注意事项

- 不要提交真实 `.env` 或真实 `AI_API_KEY`。
- `.env.example` 中只能保留占位符，例如 `AI_API_KEY=your_deepseek_api_key_here`。
- AI 调用依赖网络和模型服务，如果现场调用失败，可展示错误提示、Prompt 文件和 mock 测试通过结果。
- V0.3 已完成多用户基础版：注册、登录、JWT 鉴权、前端登录状态和核心业务数据用户隔离均已接入。
- 如果本地 SQLite 表结构和最新模型不一致，Demo 阶段可以删除 `backend/resumefit.db` 后重启后端重建。
- 不要提交 `.venv/`、`node_modules/`、`dist/`、`.pytest_cache/`、`__pycache__/` 或 `frontend/tsconfig.tsbuildinfo` 等环境和构建缓存。
- MVP 不包含 PDF/Word 导出、支付、会员、招聘网站爬取、自动投递、手机 APP 或企业后台。

## V0.3 多用户基础版说明

V0.3 已支持多用户注册登录。后端使用 JWT Bearer Token 鉴权，前端将 `access_token` 保存到 `localStorage`，并在 API 请求中自动携带：

```text
Authorization: Bearer <access_token>
```

当前已经完成用户数据隔离。两个用户之间的以下数据互不可见，也不能通过 ID 越权访问：

- 通用简历 `/resume-profiles`
- 项目经历 `/projects`
- 岗位 JD `/job-descriptions`
- 匹配报告 `/match-reports`
- 简历版本 `/resume-versions`
- Markdown 导出 `/resume-versions/{id}/export/markdown`
- 真实性风险检测 `/truth-check-results`
- 面试追问预测 `/interview-question-results`

后端 `.env` 需要增加：

```text
JWT_SECRET_KEY=change_me_for_local_dev_secret_please_replace
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

请把 `JWT_SECRET_KEY` 改成本地开发用的随机字符串，不要提交真实密钥。

### Auth API

- `POST /auth/register`：注册用户，返回 `access_token`、`token_type` 和 `user`
- `POST /auth/login`：登录用户，返回 `access_token`、`token_type` 和 `user`
- `GET /auth/me`：读取当前登录用户，需要请求头 `Authorization: Bearer <token>`

Swagger 测试步骤：

1. 启动后端后打开 `http://localhost:8000/docs`。
2. 调用 `POST /auth/register`，填写 `email`、`password`、`display_name`。
3. 复制返回的 `access_token`。
4. 在 Swagger 右上角点击 Authorize，填写 `Bearer <access_token>`。
5. 调用 `GET /auth/me`，应返回当前用户信息。
6. 也可以调用 `POST /auth/login` 验证密码登录流程。

### V0.3 验收结果

- `backend pytest`：`66 passed, 3 warnings`
- `frontend npm run build`：passed
- 双账号完整流程验收通过：用户 A 和用户 B 的简历、项目、JD、报告、版本、真实性检测、面试追问和 Markdown 导出均已验证隔离。

### 当前稳定标签

- `v0.1-demo-mvp`
- `v0.2-product-experience`
- `v0.3-multi-user`

## V0.4 AI 用量与基础额度说明

V0.4 增加 AI 使用次数、调用日志、成本字段预留和基础月额度。当前阶段仍不包含支付、会员套餐、订单、管理员后台或发票。

新增能力：

- 记录每个用户的 AI 调用日志。
- 记录功能类型：`jd_analysis`、`match_report`、`resume_generation`、`truth_check`、`interview_question`。
- 记录模型、成功/失败、错误信息和创建时间。
- token usage 字段可为空，后续可根据供应商返回补齐。
- `estimated_cost` 字段先做成本估算预留。
- 超过本月额度时阻止 AI 调用，并返回明确错误。
- 新增 `/usage` 页面，展示本月调用次数、剩余额度、功能分布和最近调用记录。

`.env` 配置：

```text
AI_MONTHLY_CALL_LIMIT=100
AI_INPUT_TOKEN_PRICE_PER_1K=0
AI_OUTPUT_TOKEN_PRICE_PER_1K=0
```

用量 API：

- `GET /usage/summary`：需要登录，返回当前用户的 AI 用量统计。

注意：额度单位是“AI 调用次数”，不是会员套餐或付费订单。V0.4 只为后续商业化打基础。

## V0.5 个人中心与账户设置

V0.5 在 V0.3 多用户基础和 V0.4 用量统计基础上，新增个人中心能力，用于展示当前登录用户的账户信息、基础用量概览和昵称设置。本阶段仍不包含支付、会员套餐、订单或管理员后台。

### 已完成能力

- 新增前端页面 `/account`，需要登录后访问。
- 侧边栏新增“个人中心”入口。
- 新增后端账户接口：
  - `GET /account/me`：返回当前用户账户信息和 `usage_summary`。
  - `PATCH /account/me`：只允许修改当前用户自己的 `display_name`。
- 个人中心展示：
  - `email`
  - `display_name`
  - `status`
  - `created_at`
  - `updated_at`
  - `usage_summary`
- 支持修改昵称；保存成功后页面数据和 Sidebar 当前用户昵称会同步更新。
- 展示 V0.4 用量概览，包括本月额度、本月已用、剩余额度和最近 AI 调用记录。
- 提供“查看详细用量”入口，可跳转 `/usage`。
- 商业化区域仅为静态预留说明，不包含支付、会员套餐、订单或真实购买入口。

### V0.5 验收结果

- backend pytest：`78 passed, 3 warnings`
- frontend npm run build：passed
- `/account` 未登录访问会跳转 `/login`
- 昵称修改后 `/auth/me` 和 Sidebar 均能显示新昵称
- 账户接口只返回和修改当前登录用户的数据

### 当前稳定标签

- `v0.1-demo-mvp`
- `v0.2-product-experience`
- `v0.3-multi-user`
- `v0.4-ai-usage-quota`

## V0.6 管理后台基础版

V0.6 新增轻量管理后台，用于后续商业化运营准备。本阶段只做用户列表、用户详情、全站 AI 用量概览和账号状态管理，不包含支付、会员套餐、订单、发票、复杂 RBAC、操作审计或删除用户。

### 已完成能力

- `users` 表新增 `role` 字段，取值为 `user` / `admin`。
- 新增 `get_current_admin_user` 后端权限依赖，非 admin 访问后台接口返回 `403`。
- `/auth/me`、注册和登录返回的用户信息包含 `role`。
- 新增后端接口：
  - `GET /admin/users`：用户列表，支持分页和按 email / display_name 搜索。
  - `GET /admin/users/{user_id}`：用户详情，返回基础账户信息和用量概览。
  - `PATCH /admin/users/{user_id}/status`：启用 / 禁用用户。
  - `GET /admin/usage/summary`：全站 AI 用量概览。
- 新增前端 `/admin` 页面。
- Sidebar 仅 admin 用户显示“管理后台”入口。
- 禁用用户后，该用户不能登录，已有 token 也不能继续调用业务接口。

### 管理员账号设置

V0.6 不提供公开“注册为管理员”入口，也不自动创建默认管理员账号。演示或本地开发时，建议先正常注册一个账号，再在 SQLite 中手动设置：

```powershell
cd backend
.\.venv\Scripts\python.exe -c "from app.core.database import SessionLocal; from app.models.user import User; db=SessionLocal(); user=db.query(User).filter(User.email=='admin@example.com').first(); user.role='admin'; db.commit(); db.close()"
```

### V0.6 验证命令

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

当前后端测试结果：

- backend pytest：`84 passed, 3 warnings`

```powershell
cd frontend
npm run build
```

当前前端构建结果：

- frontend npm run build：passed

## MVP 不做什么

MVP 阶段不包含以下能力：

- 支付系统
- 会员系统
- 招聘网站爬取
- 手机 APP
- 企业后台
- PDF/Word 高保真导出
- 多租户企业权限体系

这些能力只在架构上预留扩展位置，不进入第一阶段 Demo 范围。

## 文档索引

- [PRODUCT_REQUIREMENTS.md](PRODUCT_REQUIREMENTS.md)：产品需求、用户场景与功能边界。
- [MVP_PLAN.md](MVP_PLAN.md)：Demo 阶段开发计划与优先级。
- [ARCHITECTURE.md](ARCHITECTURE.md)：系统架构、模块划分与演进方向。
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)：MVP 数据模型与后续数据库升级建议。
- [PROMPT_GUIDE.md](PROMPT_GUIDE.md)：Prompt 目录规范、输入输出约束与安全原则。
- [AGENTS.md](AGENTS.md)：AI 开发助手与协作代理的项目规则。
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)：项目验收总结。
- [DEFENSE_SCRIPT.md](DEFENSE_SCRIPT.md)：学生答辩讲稿。
- [DEMO_GUIDE.md](DEMO_GUIDE.md)：现场演示流程。
- [SCREENSHOT_CHECKLIST.md](SCREENSHOT_CHECKLIST.md)：答辩截图清单。
- [PPT_OUTLINE.md](PPT_OUTLINE.md)：答辩 PPT 大纲。
- [ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md)：提交前验收检查表。

## 推荐启动顺序

1. 明确 MVP 页面与 API 边界。
2. 建立 FastAPI 项目结构与 SQLite 模型。
3. 建立 Vue 3 Demo 页面。
4. 接入 OpenAI-compatible AI service。
5. 将 Prompt 拆分到 `prompts/`。
6. 跑通 JD 分析、匹配度评分、简历生成、风险检测和面试问题预测。
7. 增加 Markdown 导出和多版本保存。
