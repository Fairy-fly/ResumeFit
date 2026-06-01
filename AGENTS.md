# Agents

本文档定义 ResumeFit 项目中 AI 开发助手、代码生成代理和自动化协作工具必须遵守的规则。

## 1. 项目定位

ResumeFit 当前处于 Demo 优先阶段。任何开发代理都应优先保证核心链路清晰、代码可维护、AI 能力可替换，而不是过早实现商业化复杂功能。

核心目标：

- 快速验证产品闭环。
- 保持架构可演进。
- 保护用户真实经历和隐私。
- 避免供应商锁定。

## 2. 绝对禁止

### 2.1 不允许编造用户经历

任何 AI 逻辑、Prompt、测试数据或示例输出都不得诱导系统编造用户经历。

禁止编造：

- 工作经历
- 项目经历
- 公司名称
- 岗位名称
- 学历
- 证书
- 技术经验
- 业务成果
- 量化指标
- 获奖经历

允许做：

- 改写用户已提供的信息。
- 调整表达顺序。
- 突出与 JD 相关的真实经历。
- 将模糊描述改成更清晰但不新增事实的表达。
- 对缺失信息提出补充问题。

### 2.2 不允许硬编码 API Key

严禁在任何代码、Prompt、文档示例、测试文件或配置模板中写入真实 API Key。

必须使用：

- 环境变量。
- `.env.example` 中的占位符。
- 安全配置读取逻辑。

允许示例：

```text
AI_API_KEY=your_api_key_here
```

禁止示例：

```text
AI_API_KEY=<real_secret_key_value>
```

### 2.3 不允许把业务逻辑写在一个大文件里

后端业务逻辑不得堆在 `main.py` 或单个 service 文件中。前端业务逻辑不得全部堆在一个 Vue 组件中。

必须按职责拆分：

- API 路由
- 数据模型
- 请求响应 Schema
- Repository
- Service
- AI Client
- Prompt Loader
- 前端页面
- 前端 API Client
- 可复用组件

## 3. MVP 范围约束

MVP 阶段不要实现：

- 支付系统
- 会员系统
- 招聘网站爬取
- 手机 APP
- 企业后台
- 自动投递
- 多租户管理
- 复杂管理员权限

如果代码中需要预留扩展点，只能以清晰接口、TODO 或文档说明的形式保留，不要实现完整商业化模块。

## 4. AI 接口规则

MVP 默认使用 DeepSeek API，但必须按 OpenAI-compatible API 抽象。

命名规则：

- 使用 `AIClient`，不要使用 `DeepSeekClient` 作为核心抽象。
- 使用 `AI_BASE_URL`，不要使用供应商绑定名称作为唯一配置。
- 使用 `AI_MODEL`，不要把模型名写死在业务代码中。

AI 调用必须集中在 service 或 client 层，不允许前端直接调用模型供应商 API。

## 5. Prompt 规则

所有 Prompt 必须放在 `prompts/` 目录。

禁止：

- 在业务代码中散落大段 Prompt。
- 在 Prompt 中鼓励夸大经历。
- 在 Prompt 中要求模型输出无法追溯的虚假成果。

必须：

- 明确真实性约束。
- 明确输出格式。
- 说明信息不足时应如何处理。
- 尽量输出结构化 JSON，方便后端解析。

## 6. 数据规则

必须预留并尊重以下核心数据结构：

- `User`
- `ResumeProfile`
- `Project`
- `JobDescription`
- `JobAnalysis`
- `MatchReport`
- `ResumeVersion`
- `InterviewQuestion`

用户原始资料和 AI 生成结果应分开存储。AI 原始输出建议保留，便于调试和审计。

## 7. 隐私与安全

简历、项目经历和 JD 都可能包含敏感信息。

开发代理必须：

- 避免在日志中输出完整简历。
- 避免提交 `.env`。
- 避免把用户隐私写入测试快照。
- 对 AI 请求失败进行安全错误提示。
- 不把 API Key 返回给前端。

## 8. 代码质量规则

开发时应遵守：

- 小步提交。
- 每个模块职责清晰。
- 公共逻辑抽成函数或 service。
- API 返回结构稳定。
- 错误处理清楚。
- 命名表达业务含义。

不应为了 Demo 速度牺牲基本结构。Demo 可以功能少，但不能把后续维护变成灾难。

## 9. 文档维护规则

当新增核心功能、数据表、AI Prompt 或架构约束时，应同步更新相关文档：

- `README.md`
- `PRODUCT_REQUIREMENTS.md`
- `MVP_PLAN.md`
- `ARCHITECTURE.md`
- `DATABASE_SCHEMA.md`
- `PROMPT_GUIDE.md`
- `AGENTS.md`

## 10. 协作原则

开发代理应主动识别当前任务属于：

- 产品规划
- 架构设计
- 数据建模
- 前端实现
- 后端实现
- Prompt 设计
- 测试验证
- 文档维护

在没有用户明确要求时，不要跨越任务边界。例如，用户只要求创建规划文档时，不应创建业务代码。
