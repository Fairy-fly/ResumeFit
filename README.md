# ResumeFit

ResumeFit 是一个 AI 简历优化系统。它面向求职场景，支持用户输入通用简历、项目经历和目标岗位 JD，系统会生成岗位分析、匹配度报告、岗位定制简历，并提供真实性风险检测、面试追问预测、多版本管理以及 Markdown / DOCX 导出。

项目采用 Vue 3 + Vite 前端、FastAPI 后端、SQLite 本地数据库和 OpenAI-compatible AI 接口。默认 AI Provider 可接入 DeepSeek，测试中通过 mock `AIClient` 避免真实模型调用。

## 解决的问题

- 通用简历和岗位 JD 匹配度低，用户需要反复手动改写。
- 项目经历分散，难以快速筛选和组织成岗位相关表达。
- AI 生成内容容易夸大或编造经历，需要真实性约束和风险提示。
- 面试中常被追问项目细节、数据来源和技术掌握程度，需要提前准备。
- 多个岗位对应多个简历版本，缺少版本管理和可投递文件导出。

## 核心功能

- 用户注册、登录、JWT 鉴权和多用户数据隔离。
- 通用简历录入与历史详情查看。
- 项目库管理，沉淀真实项目、角色、技术栈和个人贡献。
- 岗位 JD 保存与 AI 结构化分析。
- 简历、项目和 JD 的匹配度报告生成。
- 岗位定制简历生成与修改原因说明。
- 真实性风险检测，提醒夸大、缺证据和不确定表达。
- 面试追问预测，生成追问问题、原因、建议回答和风险提醒。
- 简历版本管理，支持历史版本切换、复制和导出。
- Markdown 导出、DOCX 导出和 DOCX 模板选择。
- AI 调用日志、月度额度、用量统计和基础管理后台。
- 个人中心，支持查看账户信息和修改昵称。

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3, Vite, TypeScript, Vue Router |
| 后端 | FastAPI, SQLAlchemy, Pydantic, SQLite |
| AI | OpenAI-compatible API, DeepSeek, 统一 `AIClient` 抽象 |
| 导出 | Markdown response, python-docx |
| 鉴权 | JWT Bearer Token, bcrypt password hash |
| 测试 | pytest, mock AIClient |

## 项目结构

```text
ResumeFit/
+-- backend/
|   +-- app/
|   |   +-- api/routes/       # FastAPI routes
|   |   +-- ai/               # AIClient and prompt loader
|   |   +-- core/             # config, database, security
|   |   +-- models/           # SQLAlchemy models
|   |   +-- repositories/     # data access layer
|   |   +-- schemas/          # Pydantic schemas
|   |   +-- services/         # business logic
|   +-- tests/                # pytest tests
|   +-- requirements.txt
+-- frontend/
|   +-- src/
|   |   +-- api/              # frontend API clients
|   |   +-- auth/             # token/session state
|   |   +-- components/       # shared and version components
|   |   +-- pages/            # page views
|   |   +-- router/           # Vue Router
|   +-- package.json
+-- prompts/                  # AI prompts and shared rules
+-- docs/                     # GitHub-facing project docs
+-- screenshots/              # screenshot placeholders
+-- .env.example
+-- README.md
```

## 本地运行步骤

### 1. 准备环境变量

```powershell
cd D:\cxdownload\ResumeFit
Copy-Item .env.example .env
```

编辑 `.env`，把 `AI_API_KEY` 替换为你自己的本地开发密钥。不要提交 `.env`。

### 2. 启动后端

```powershell
cd D:\cxdownload\ResumeFit\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端地址：

- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`

### 3. 启动前端

```powershell
cd D:\cxdownload\ResumeFit\frontend
npm install
npm run dev
```

前端地址：

- `http://localhost:5173`

## 环境变量说明

| 变量 | 示例值 | 说明 |
| --- | --- | --- |
| `APP_NAME` | `ResumeFit` | 应用名称 |
| `ENVIRONMENT` | `development` | 运行环境 |
| `DATABASE_URL` | `sqlite:///./resumefit.db` | SQLite 数据库连接 |
| `CORS_ORIGINS` | `http://localhost:5173` | 前端跨域来源 |
| `JWT_SECRET_KEY` | `change_me_for_local_dev_secret` | JWT 本地开发密钥，占位即可 |
| `JWT_ALGORITHM` | `HS256` | JWT 签名算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Access token 有效期 |
| `AI_PROVIDER` | `deepseek` | AI provider 标识 |
| `AI_BASE_URL` | `https://api.deepseek.com` | OpenAI-compatible base URL |
| `AI_API_KEY` | `your_api_key_here` | AI API Key，占位符 |
| `AI_MODEL` | `deepseek-chat` | 模型名称 |
| `AI_TIMEOUT_SECONDS` | `60` | AI 请求超时时间 |
| `AI_MONTHLY_CALL_LIMIT` | `100` | 用户月度 AI 调用额度 |
| `VITE_API_BASE_URL` | `http://localhost:8000` | 前端 API 地址 |

## 数据库说明

默认使用 SQLite，本地数据库文件位于后端工作目录下的 `resumefit.db`。应用启动时会创建所需表，并包含轻量迁移逻辑。

核心数据包括：

- `users`: 用户、角色、状态和登录信息。
- `resume_profiles`: 通用简历。
- `projects`: 项目库。
- `job_descriptions`: 岗位 JD。
- `job_analyses`: JD 结构化分析结果。
- `match_reports`: 匹配度报告。
- `resume_versions`: 定制简历版本。
- `truth_check_results`: 真实性风险检测结果。
- `interview_question_results`: 面试追问预测结果。
- `ai_usage_logs`: AI 调用日志和用量统计。

详细说明见 [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)。

## AI Prompt 模块说明

Prompt 统一放在 `prompts/` 目录，并通过后端 Prompt Loader 读取。业务代码不直接散落大段 Prompt。

设计原则：

- 强调真实经历，不允许编造项目、公司、学历、证书或量化成果。
- 信息不足时要求保守表达，并提示需要补充证据。
- 尽量输出结构化 JSON，方便后端解析、校验和存储。
- AI 调用通过统一 `AIClient`，默认兼容 DeepSeek，也便于替换其他 OpenAI-compatible provider。

详细说明见 [docs/PROMPT_GUIDE.md](docs/PROMPT_GUIDE.md)。

## 演示流程

1. 注册并登录账号。
2. 在 Dashboard 查看当前流程和下一步建议。
3. 在 `/resume` 输入通用简历。
4. 在 `/projects` 添加项目经历。
5. 在 `/jobs` 粘贴岗位 JD 并生成 JD 分析。
6. 在 `/analysis` 生成匹配度报告。
7. 在 `/versions` 生成岗位定制简历。
8. 查看修改原因、复制 Markdown、导出 Markdown 或 DOCX。
9. 运行真实性风险检测。
10. 生成面试追问预测。
11. 在 `/usage` 查看 AI 用量。
12. 在 `/account` 查看账户信息和用量概览。

完整演示说明见 [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md)。

## 截图占位

后续可以把截图放入 `screenshots/` 目录，并在这里替换为真实图片：

| 页面 | 截图文件建议 |
| --- | --- |
| 首页 / Dashboard | `screenshots/dashboard.png` |
| 简历输入页 | `screenshots/resume-input.png` |
| 项目库页面 | `screenshots/project-library.png` |
| JD 分析页 | `screenshots/jd-analysis.png` |
| 匹配度报告页 | `screenshots/match-report.png` |
| 定制简历生成页 | `screenshots/resume-generation.png` |
| 真实性风险检测页 | `screenshots/truth-check.png` |
| 面试追问预测页 | `screenshots/interview-questions.png` |

截图清单见 [screenshots/README.md](screenshots/README.md)。

## 测试

后端：

```powershell
cd D:\cxdownload\ResumeFit\backend
.\.venv\Scripts\python.exe -m pytest
```

前端：

```powershell
cd D:\cxdownload\ResumeFit\frontend
npm run build
```

测试要求：

- AI 相关测试使用 mock，不真实调用 DeepSeek。
- 不提交 `.env`、SQLite 数据库、虚拟环境、`node_modules` 或构建缓存。

## 项目亮点

- 完整 AI 简历优化闭环：JD 分析、匹配报告、定制生成、真实性检测、面试追问和导出。
- 严格真实性约束：Prompt 和服务层都强调不编造用户经历。
- OpenAI-compatible 抽象：默认接入 DeepSeek，但不绑定供应商。
- 多用户基础能力：JWT 鉴权和用户数据隔离。
- 用量统计与额度：记录 AI 调用日志，为后续商业化扩展预留基础。
- 可投递文件导出：支持 Markdown 和 DOCX，并提供 DOCX 模板选择。
- 分层架构清晰：route、schema、repository、service、AI client 和 prompt 分离。
- 测试友好：AIClient 可 mock，避免测试依赖真实模型。

## 后续计划

- PDF 导出。
- 更丰富的 DOCX 模板和排版控制。
- PostgreSQL + Alembic 迁移。
- 部署配置与生产环境安全加固。
- Prompt 评测集和生成质量回归测试。
- 更完善的管理后台和用量运营能力。
- 更细粒度的 AI 成本估算和模型选择。

## GitHub About 推荐

Description:

```text
AI resume optimization system for JD analysis, resume tailoring, authenticity checks, interview question prediction, and Markdown/DOCX export.
```

Topics:

```text
ai-resume, resume-optimization, fastapi, vue, vite, sqlite, deepseek, openai-compatible, job-search, career-tools, pytest, llm
```
