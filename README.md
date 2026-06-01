# ResumeFit

ResumeFit 是一款基于大语言模型的智能简历定制与求职辅助平台。当前阶段目标是先完成可演示 Demo，验证核心求职辅助链路；后续再逐步演进为可商业化的软件产品。

## 产品定位

ResumeFit 面向正在求职、转岗、实习申请或希望提升简历匹配度的个人用户。系统帮助用户把一份通用简历、项目经历和目标岗位 JD 结合起来，完成岗位分析、匹配度评分、定制简历生成、真实性风险提示和面试追问预测。

产品原则：

- 先 Demo：优先跑通从输入简历到生成岗位定制版本的核心闭环。
- 后商业化：架构预留用户体系、版本管理、导出能力、模型切换和数据库升级空间。
- 不编造经历：系统只能基于用户提供的信息改写、组织和强调，不能创造不存在的工作、项目、成果、学历或证书。
- 可替换 AI：MVP 默认使用 DeepSeek API，但 AI 服务层必须遵循 OpenAI-compatible 结构，避免与单一供应商强绑定。

## 核心功能

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

## 本地启动

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

### 页面测试

1. 启动后端。
2. 启动前端。
3. 确认 `/resume` 中已有简历，`/projects` 中已有项目，`/jobs` 中已有已分析 JD，`/analysis` 中已有匹配报告。
4. 打开 `http://localhost:5173/versions`。
5. 选择一个匹配报告，页面会带出对应简历、项目和 JD。
6. 点击“生成定制简历”。
7. 确认页面显示 Markdown 简历和修改原因。
8. 点击“复制 Markdown”，确认复制成功。

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

## 推荐启动顺序

1. 明确 MVP 页面与 API 边界。
2. 建立 FastAPI 项目结构与 SQLite 模型。
3. 建立 Vue 3 Demo 页面。
4. 接入 OpenAI-compatible AI service。
5. 将 Prompt 拆分到 `prompts/`。
6. 跑通 JD 分析、匹配度评分、简历生成、风险检测和面试问题预测。
7. 增加 Markdown 导出和多版本保存。
