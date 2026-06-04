# ResumeFit 项目验收检查表

## 1. 启动检查

- [ ] 后端可以正常启动。
  - 命令：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
  - 预期：终端显示 Uvicorn running。
- [ ] 后端健康检查正常。
  - 命令：`Invoke-RestMethod http://localhost:8000/health`
  - 预期：返回 `{"status":"ok"}`。
- [ ] 前端可以正常启动。
  - 命令：`npm run dev`
  - 预期：Vite 输出本地访问地址。
- [ ] 浏览器可以访问前端首页。
  - 地址：`http://localhost:5173/`
  - 预期：首页展示 ResumeFit Demo 流程。

## 2. 数据库检查

- [ ] SQLite 数据库可以正常创建。
  - 预期：后端启动后自动创建所需表。
- [ ] 默认 Demo 用户存在。
  - 预期：Demo 阶段使用 `user_id = 1`。
- [ ] 核心表结构存在。
  - `users`
  - `resume_profiles`
  - `projects`
  - `job_descriptions`
  - `job_analyses`
  - `match_reports`
  - `resume_versions`
  - `truth_check_results`
  - `interview_question_results`
- [ ] 如本地旧 SQLite 表结构不兼容，可以删除 `backend/resumefit.db` 后重启后端重建。

## 3. 页面访问检查

- [ ] 首页 Dashboard 可访问：`/`
- [ ] 通用简历页面可访问：`/resume`
- [ ] 项目库页面可访问：`/projects`
- [ ] 岗位 JD 页面可访问：`/jobs`
- [ ] 匹配分析页面可访问：`/analysis`
- [ ] 简历版本页面可访问：`/versions`
- [ ] FastAPI docs 可访问：`http://localhost:8000/docs`

## 4. 功能流程检查

- [ ] 可以保存通用简历。
- [ ] 可以查询通用简历列表。
- [ ] 可以保存项目经历。
- [ ] 可以查询项目列表。
- [ ] 可以保存岗位 JD。
- [ ] 配置 AI Key 后可以生成 JD 分析。
- [ ] 可以选择简历、项目和已分析 JD 生成匹配报告。
- [ ] 可以基于匹配报告生成定制简历。
- [ ] 可以复制 Markdown 简历。
- [ ] 可以导出 Markdown 文件。
- [ ] 可以对 ResumeVersion 进行真实性风险检测。
- [ ] 可以生成面试追问预测。

## 5. AI 调用检查

- [ ] `.env` 中使用占位符或本地真实值，真实 API Key 不提交。
- [ ] `AI_PROVIDER`、`AI_BASE_URL`、`AI_API_KEY`、`AI_MODEL` 从环境变量读取。
- [ ] 未配置 `AI_API_KEY` 时，后端返回明确错误提示。
- [ ] AI 返回非 JSON 或网络异常时，后端返回清晰错误。
- [ ] 测试中使用 mock AI，不真实调用 DeepSeek。
- [ ] Prompt 文件均位于 `prompts/` 目录。

## 6. 测试与构建检查

- [ ] 后端测试通过。
  - 命令：
    ```powershell
    cd backend
    .\.venv\Scripts\Activate.ps1
    python -m pytest
    ```
- [ ] 前端构建通过。
  - 命令：
    ```powershell
    cd frontend
    npm run build
    ```
- [ ] 建议保留 pytest 通过截图。
- [ ] 建议保留 npm build 通过截图。

## 7. 安全与提交检查

- [ ] 仓库中没有真实 API Key。
- [ ] `.env` 未提交。
- [ ] `node_modules/` 未提交。
- [ ] `.venv/` 未提交。
- [ ] `dist/` 等构建产物未提交，除非项目明确要求。
- [ ] `frontend/tsconfig.tsbuildinfo` 等构建缓存不作为本次验收材料提交。
- [ ] 未新增登录、支付、会员、爬取、PDF/Word 导出等 MVP 范围外功能。
- [ ] 未修改 AI 核心逻辑。
- [ ] 未修改数据库核心结构。

## 8. Git 检查

- [ ] 查看当前变更：
  ```powershell
  git status --short
  ```
- [ ] 确认只包含本次需要提交的文档变更。
- [ ] 如需提交，提交信息建议：
  ```text
  docs: add acceptance and defense materials
  ```
- [ ] 提交后再次确认工作区干净：
  ```powershell
  git status --short
  ```

## 9. README 完整性检查

- [ ] README 包含项目简介。
- [ ] README 包含功能列表。
- [ ] README 包含技术栈。
- [ ] README 包含启动方式。
- [ ] README 包含 Demo 演示顺序。
- [ ] README 包含测试命令。
- [ ] README 包含注意事项。
- [ ] README 链接到新增答辩与验收文档。
