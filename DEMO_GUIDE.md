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
- FastAPI docs：`http://localhost:8000/docs`
- 后端健康检查：`http://localhost:8000/health`

## 4. 推荐演示顺序

1. 首页 Dashboard
2. 通用简历输入
3. 项目库管理
4. 岗位 JD 分析
5. 匹配度报告
6. 定制简历生成
7. 真实性风险检测
8. 面试追问预测
9. Markdown 导出

## 5. 每个页面应该演示什么

| 页面 | 演示重点 |
| --- | --- |
| `/` | 展示完整 8 步流程、数据统计和功能入口 |
| `/resume` | 保存一份通用简历，作为事实来源 |
| `/projects` | 添加真实项目经历，展示技术栈、角色和贡献 |
| `/jobs` | 粘贴岗位 JD，生成结构化 JD 分析 |
| `/analysis` | 选择简历、项目和已分析 JD，生成匹配报告 |
| `/versions` | 生成定制简历、检测真实性风险、预测面试追问、导出 Markdown |
| `http://localhost:8000/docs` | 展示 FastAPI 自动生成的后端接口文档 |

## 6. 每一步应该点击什么

### Step 1：首页 Dashboard

操作：

1. 打开 `http://localhost:5173/`。
2. 展示首页的“8 步 Demo 流程”。
3. 展示当前数据统计卡片。
4. 点击“通用简历”或侧边栏“通用简历”进入下一步。

预期结果：

- 页面展示 ResumeFit 演示流程。
- 能看到简历数量、项目数量、岗位 JD 数量、匹配报告数量、简历版本数量。

### Step 2：通用简历输入

操作：

1. 打开 `/resume`。
2. 输入简历标题，例如“后端开发通用简历”。
3. 在正文中输入 Markdown 简历内容。
4. 点击“保存简历”。

预期结果：

- 页面显示保存成功。
- 下方简历列表出现刚保存的简历。
- 刷新页面后数据仍然存在。

### Step 3：项目库管理

操作：

1. 打开 `/projects`。
2. 输入项目名称、项目类型、我的角色、技术栈、项目描述、个人贡献和作品链接。
3. 点击“保存项目”。

预期结果：

- 页面显示保存成功。
- 项目列表中出现项目名称、类型、技术栈和贡献描述。

### Step 4：岗位 JD 分析

操作：

1. 打开 `/jobs`。
2. 输入公司名称和岗位名称。
3. 粘贴岗位 JD 原文。
4. 点击“保存并分析”。

预期结果：

- 页面展示岗位类型、必备技能、加分技能、岗位职责、关键词和简历侧重点建议。
- JD 列表中该岗位状态变为已分析。

### Step 5：匹配度报告

操作：

1. 打开 `/analysis`。
2. 选择一份通用简历。
3. 勾选一个或多个项目经历。
4. 选择一个已分析 JD。
5. 点击“生成匹配报告”。

预期结果：

- 页面展示匹配分数。
- 能看到优势、不足、缺失关键词、修改建议和真实性提醒。

### Step 6：定制简历生成

操作：

1. 打开 `/versions`。
2. 在匹配报告区域选择刚生成的报告。
3. 确认页面自动带出简历、项目和 JD。
4. 点击“生成定制简历”。

预期结果：

- 页面展示 Markdown 简历正文。
- 页面展示修改原因 `change_explanations`。
- 可以点击“复制 Markdown”。

### Step 7：真实性风险检测

操作：

1. 在 `/versions` 页面找到“真实性风险检测”区域。
2. 选择刚生成的简历版本。
3. 点击“检测真实性风险”。

预期结果：

- 页面展示总体风险等级。
- 页面展示风险表达、风险原因、证据状态、更稳妥改法和面试追问风险点。

### Step 8：面试追问预测

操作：

1. 在 `/versions` 页面找到“面试追问预测”区域。
2. 选择同一个简历版本。
3. 点击“生成面试追问”。

预期结果：

- 页面展示面试问题。
- 每个问题包含为什么会问、关联简历内容、难度、建议回答、回答策略和风险提醒。

### Step 9：Markdown 导出

操作：

1. 在 `/versions` 页面找到生成后的 Markdown 简历。
2. 点击“导出 Markdown”。

预期结果：

- 浏览器下载 `.md` 文件。
- 文件名包含 ResumeFit、岗位名称和日期。
- 文件内容与页面中的 Markdown 简历一致。

## 7. 如果 AI 调用失败，如何说明或处理

AI 调用失败时，不要现场临时修改代码，可以按以下方式说明：

1. 先说明 AI 接口依赖网络和 `.env` 中的 `AI_API_KEY`。
2. 如果后端返回 `AI_API_KEY is not configured.`，说明当前环境没有配置真实密钥。
3. 如果返回网络错误或 AI 响应不是 JSON，说明外部模型服务不可用或返回格式异常。
4. 展示后端错误提示，说明系统没有崩溃，而是给出了明确错误。
5. 展示 `prompts/` 目录，说明 Prompt 已经独立管理并要求稳定 JSON。
6. 展示 `python -m pytest` 通过截图，说明测试中使用 mock AI 验证了核心流程。
7. 可以继续演示已经保存的历史结果，或说明重新配置 API Key 后可以继续生成。

## 8. 演示前准备建议

- 提前配置 `.env`，不要把真实 API Key 提交到仓库。
- 提前准备一份简历正文、一段项目描述和一份岗位 JD。
- 提前跑一次完整流程，确保数据库中有可展示数据。
- 准备 pytest 和 npm build 通过截图。
- 准备 FastAPI docs 截图，展示接口结构。
