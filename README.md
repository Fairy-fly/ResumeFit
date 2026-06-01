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
