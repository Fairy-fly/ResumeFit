# ResumeFit Demo 演示流程

## 1. 启动后端命令

在项目根目录打开 PowerShell：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

如果已经创建过虚拟环境，可以从激活环境开始：

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端健康检查：

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## 2. 启动前端命令

新开一个 PowerShell：

```powershell
cd frontend
npm install
npm run dev
```

## 3. 浏览器访问地址

- 前端页面：`http://localhost:5173`
- 登录页：`http://localhost:5173/login`
- 注册页：`http://localhost:5173/register`
- FastAPI docs：`http://localhost:8000/docs`
- 后端健康检查：`http://localhost:8000/health`

V0.3 起，业务页面需要登录后访问。前端会把登录后的 `access_token` 保存到 `localStorage`，并自动在 API 请求中携带 `Authorization: Bearer <token>`。

## 4. 推荐演示顺序

1. 注册或登录用户 A
2. 首页 Dashboard
3. 通用简历输入
4. 项目库管理
5. 岗位 JD 分析
6. 匹配度报告
7. 定制简历生成
8. 真实性风险检测
9. 面试追问预测
10. Markdown 导出
11. 退出用户 A，登录用户 B，展示用户隔离

## 5. 每个页面应该演示什么

| 页面 | 演示重点 |
| --- | --- |
| `/login` | 登录已有账号，验证认证页不显示业务 Sidebar |
| `/register` | 注册新账号，注册成功后进入 Dashboard |
| `/` | 展示完整 8 步流程、数据统计和功能入口 |
| `/resume` | 保存一份通用简历，作为事实来源 |
| `/projects` | 添加真实项目经历，展示技术栈、角色和贡献 |
| `/jobs` | 粘贴岗位 JD，生成结构化 JD 分析 |
| `/analysis` | 选择简历、项目和已分析 JD，生成匹配报告 |
| `/versions` | 生成定制简历、检测真实性风险、预测面试追问、导出 Markdown |
| `http://localhost:8000/docs` | 展示 FastAPI 自动生成的后端接口文档 |

## 6. 每一步应该点击什么

### Step 1：注册或登录用户 A

操作：

1. 打开 `http://localhost:5173/register`。
2. 输入邮箱、显示名、密码和确认密码。
3. 点击注册。

预期结果：

- 注册成功后进入 Dashboard。
- 侧边栏显示当前用户。
- 刷新页面后仍保持登录状态。

### Step 2：首页 Dashboard

操作：

1. 打开 `http://localhost:5173/`。
2. 展示首页的“8 步 Demo 流程”。
3. 展示当前数据统计卡片。
4. 点击“通用简历”或侧边栏“通用简历”进入下一步。

预期结果：

- 页面展示 ResumeFit 演示流程。
- 能看到简历数量、项目数量、岗位 JD 数量、匹配报告数量、简历版本数量。

### Step 3：通用简历输入

操作：

1. 打开 `/resume`。
2. 输入简历标题，例如“后端开发通用简历”。
3. 在正文中输入 Markdown 简历内容。
4. 点击“保存简历”。

预期结果：

- 页面显示保存成功。
- 下方简历列表出现刚保存的简历。
- 刷新页面后数据仍然存在。

### Step 4：项目库管理

操作：

1. 打开 `/projects`。
2. 输入项目名称、项目类型、我的角色、技术栈、项目描述、个人贡献和作品链接。
3. 点击“保存项目”。

预期结果：

- 页面显示保存成功。
- 项目列表中出现项目名称、类型、技术栈和贡献描述。

### Step 5：岗位 JD 分析

操作：

1. 打开 `/jobs`。
2. 输入公司名称和岗位名称。
3. 粘贴岗位 JD 原文。
4. 点击“保存并分析”。

预期结果：

- 页面展示岗位类型、必备技能、加分技能、岗位职责、关键词和简历侧重点建议。
- JD 列表中该岗位状态变为已分析。

### Step 6：匹配度报告

操作：

1. 打开 `/analysis`。
2. 选择一份通用简历。
3. 勾选一个或多个项目经历。
4. 选择一个已分析 JD。
5. 点击“生成匹配报告”。

预期结果：

- 页面展示匹配分数。
- 能看到优势、不足、缺失关键词、修改建议和真实性提醒。

### Step 7：定制简历生成

操作：

1. 打开 `/versions`。
2. 在匹配报告区域选择刚生成的报告。
3. 确认页面自动带出简历、项目和 JD。
4. 点击“生成定制简历”。

预期结果：

- 页面展示 Markdown 简历正文。
- 页面展示修改原因 `change_explanations`。
- 可以点击“复制 Markdown”。

### Step 8：真实性风险检测

操作：

1. 在 `/versions` 页面找到“真实性风险检测”区域。
2. 选择刚生成的简历版本。
3. 点击“检测真实性风险”。

预期结果：

- 页面展示总体风险等级。
- 页面展示风险表达、风险原因、证据状态、更稳妥改法和面试追问风险点。

### Step 9：面试追问预测

操作：

1. 在 `/versions` 页面找到“面试追问预测”区域。
2. 选择同一个简历版本。
3. 点击“生成面试追问”。

预期结果：

- 页面展示面试问题。
- 每个问题包含为什么会问、关联简历内容、难度、建议回答、回答策略和风险提醒。

### Step 10：Markdown 导出

操作：

1. 在 `/versions` 页面找到生成后的 Markdown 简历。
2. 点击“导出 Markdown”。

预期结果：

- 浏览器下载 `.md` 文件。
- 文件名包含 ResumeFit、岗位名称和日期。
- 文件内容与页面中的 Markdown 简历一致。

### Step 11：双账号用户隔离演示

操作：

1. 在侧边栏退出用户 A。
2. 注册或登录用户 B。
3. 依次打开 `/resume`、`/projects`、`/jobs`、`/analysis`、`/versions`。
4. 确认用户 B 看不到用户 A 的简历、项目、JD、匹配报告、简历版本、真实性检测历史和面试追问历史。
5. 用户 B 创建自己的简历、项目、JD，并生成自己的匹配报告、简历版本和 Markdown 导出。
6. 退出用户 B，再登录用户 A。

预期结果：

- 用户 B 只能看到和操作自己的数据。
- 用户 B 不能通过页面导出用户 A 的 Markdown 简历。
- 重新登录用户 A 后，用户 A 的数据仍然存在，且看不到用户 B 的数据。

## 7. 如果 AI 调用失败，如何说明或处理

AI 调用失败时，不要现场临时修改代码，可以按以下方式说明：

1. 先说明 AI 接口依赖网络和 `.env` 中的 `AI_API_KEY`。
2. 如果后端返回 `AI_API_KEY is not configured.`，说明当前环境没有配置真实密钥。
3. 如果返回网络错误或 AI 响应不是 JSON，说明外部模型服务不可用或返回格式异常。
4. 展示后端错误提示，说明系统没有崩溃，而是给出了明确错误。
5. 展示 `prompts/` 目录，说明 Prompt 已经独立管理并要求稳定 JSON。
6. 展示 `python -m pytest` 通过截图，说明测试中使用 mock AI 验证了核心流程。
7. 可以继续演示已经保存的历史结果，或说明重新配置 API Key 后可以继续生成。

## 8. V0.3 验收结果与稳定标签

V0.3 多用户基础版已完成验收：

- 后端测试：`backend pytest`，结果为 `66 passed, 3 warnings`。
- 前端构建：`frontend npm run build`，结果为 passed。
- 双账号完整流程验收通过：用户 A 与用户 B 的简历、项目、JD、报告、版本、真实性检测、面试追问和 Markdown 导出互相隔离。

当前稳定标签：

- `v0.1-demo-mvp`
- `v0.2-product-experience`
- `v0.3-multi-user`

## 9. V0.5 个人中心演示

V0.5 新增 `/account` 个人中心页面，用于展示当前登录用户的账户信息、基础用量概览和昵称设置。

### 演示步骤

1. 启动后端和前端，并使用已有账号登录。
2. 在左侧 Sidebar 点击“个人中心”。
3. 确认页面展示：
   - 邮箱 `email`
   - 昵称 `display_name`
   - 账号状态 `status`
   - 创建时间 `created_at`
   - 更新时间 `updated_at`
   - 用量概览 `usage_summary`
4. 修改昵称并点击保存。
5. 确认页面昵称更新，左侧 Sidebar 当前用户名称也同步更新。
6. 点击“查看详细用量”，确认跳转到 `/usage`。
7. 说明“会员与额度管理后续开放”只是静态预留，不包含支付、会员套餐或订单功能。

### API 演示

登录后可在 FastAPI docs 中测试账户接口：

- 后端 Swagger 地址：`http://localhost:8000/docs`
- `GET /account/me`：查看当前用户账户信息和 `usage_summary`。
- `PATCH /account/me`：只修改当前用户 `display_name`。

V0.5 验收结果：

- backend pytest：`78 passed, 3 warnings`
- frontend npm run build：passed
- `/account` 未登录访问会跳转 `/login`
- 昵称修改后 `/auth/me` 和 Sidebar 均显示新昵称

当前稳定标签：

- `v0.1-demo-mvp`
- `v0.2-product-experience`
- `v0.3-multi-user`
- `v0.4-ai-usage-quota`

## 9. 演示前准备建议

- 提前配置 `.env`，不要把真实 API Key 提交到仓库。
- 提前准备一份简历正文、一段项目描述和一份岗位 JD。
- 提前跑一次完整流程，确保数据库中有可展示数据。
- 准备 pytest 和 npm build 通过截图。
- 准备 FastAPI docs 截图，展示接口结构。
## V0.7 DOCX 导出演示补充

V0.7 在 `/versions` 页面新增“导出 DOCX”按钮，适合在 Demo 最后展示“生成可投递文件”的能力。

推荐演示步骤：

1. 登录一个已有数据的用户账号。
2. 打开 `/versions`。
3. 从历史版本中选择一个已生成的 ResumeVersion。
4. 先展示 Markdown 简历内容。
5. 点击“导出 Markdown”，说明原有 `.md` 导出能力仍然保留。
6. 点击“导出 DOCX”。
7. 预期浏览器下载 `.docx` 文件。
8. 打开下载文件，确认标题、项目段落、技能等核心文本来自页面中的 Markdown 简历。

讲解要点：

- DOCX 导出接口为 `GET /resume-versions/{id}/export/docx`。
- 后端使用 `python-docx` 基于 `ResumeVersion.content_markdown` 生成 DOCX。
- 文件以内存流返回，不长期保存到公开目录。
- DOCX 导出不调用 AI，不消耗 AI 月额度。
- DOCX 导出沿用 V0.3 用户隔离，用户不能导出其他人的 ResumeVersion。
- PDF 导出暂未实现，作为后续版本规划。

V0.7 验收结果：

- 后端测试：`88 passed, 3 warnings`
- 前端 `npm run build`：通过

## V0.8 DOCX 模板导出演示补充

V0.8 在 `/versions` 页面为 DOCX 导出增加模板选择，适合在演示最后说明 ResumeFit 已经从单一 DOCX 导出升级为多版式导出。

推荐演示步骤：

1. 登录一个已有 ResumeVersion 的账号。
2. 打开 `/versions`。
3. 在历史版本中选择一份已生成的简历版本。
4. 确认 Markdown 预览区显示当前选中版本内容。
5. 在“导出 DOCX”旁选择模板：`Standard`、`Modern` 或 `Compact`。
6. 点击“导出 DOCX”。
7. 确认浏览器下载 `.docx` 文件。
8. 分别选择 `Modern` 和 `Compact` 再导出一次，说明三种模板来自同一份真实简历内容，只调整 Word 版式。

讲解要点：

- 接口仍然是 `GET /resume-versions/{id}/export/docx`，通过 `template` query 参数选择模板。
- 不传模板时默认 `standard`。
- 非法模板会返回 `422`。
- DOCX 模板导出不调用 AI，不消耗 AI 月额度。
- 导出仍然沿用用户隔离，用户只能导出自己的 ResumeVersion。
- Markdown 导出继续保留，PDF 导出暂未实现。

V0.8 验收结果：

- 后端测试：`92 passed, 3 warnings`
- 前端 `npm run build`：通过
