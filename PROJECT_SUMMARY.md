# ResumeFit 项目总结

## 1. 项目名称

ResumeFit：基于大语言模型的智能简历定制与求职辅助平台。

## 2. 项目背景

在求职过程中，很多同学或求职者通常只有一份通用简历。但不同岗位 JD 对技能关键词、项目经历、职责表达和业务理解的关注点并不相同。如果完全手动修改，每次投递都需要重新分析岗位要求、筛选项目经历、调整简历表达，成本较高。

同时，使用 AI 改简历时也容易出现另一个问题：为了提高匹配度，模型可能把用户没有提供的经历、成果或技能写进简历，导致后续面试无法自洽。因此 ResumeFit 的核心思路不是替用户编造经历，而是基于用户真实材料做结构化整理、岗位化表达和风险提示。

## 3. 项目痛点

- 通用简历难以针对不同岗位突出重点。
- 求职者不容易快速看出 JD 中的核心技能、职责和关键词。
- 手动调整简历耗时，且不同版本难以管理。
- AI 生成内容可能夸大或编造经历，带来真实性风险。
- 面试前缺少基于简历和岗位的追问准备。

## 4. 项目目标

ResumeFit 的 Demo 阶段目标是跑通完整求职辅助闭环：

1. 用户录入通用简历和真实项目经历。
2. 用户粘贴目标岗位 JD。
3. 系统分析 JD 并生成结构化结果。
4. 系统评估简历与岗位的匹配度。
5. 系统生成一版 Markdown 定制简历。
6. 系统检测生成简历中的真实性风险。
7. 系统预测面试可能追问的问题。
8. 用户可以导出 Markdown 简历文件。

## 5. 目标用户

- 准备实习、校招或社招投递的学生和求职者。
- 有真实项目经历，但不知道如何针对 JD 调整表达的人。
- 希望在改简历的同时控制真实性风险的人。
- 希望提前准备面试追问的人。

当前 Demo 暂不面向企业 HR、猎头机构、批量招聘平台或自动投递场景。

## 6. 核心功能

| 功能 | 说明 |
| --- | --- |
| 首页 Dashboard | 展示完整 Demo 流程、数据统计和功能入口 |
| 通用简历输入 | 保存简历标题和 Markdown 正文 |
| 项目库管理 | 保存项目名称、类型、角色、技术栈、描述、贡献和链接 |
| 岗位 JD 分析 | 调用 AI 提取岗位类型、技能、职责、关键词和简历侧重点 |
| 匹配度报告 | 根据简历、项目和 JD 分析生成分数、优势、不足和建议 |
| 定制简历生成 | 生成 Markdown 简历，并保存修改原因 |
| 真实性风险检测 | 检查夸大、缺证据和不确定表达等风险 |
| 面试追问预测 | 生成可能追问、提问原因、建议回答和风险提醒 |
| Markdown 导出 | 将已生成的简历版本导出为 `.md` 文件 |

## 7. 技术栈

- 前端：Vue 3、TypeScript、Vite、Vue Router
- 后端：FastAPI、Pydantic、SQLAlchemy
- 数据库：SQLite
- AI 接口：OpenAI-compatible API，MVP 默认配置 DeepSeek
- Prompt 管理：`prompts/` 目录
- 测试：pytest、前端 `npm run build`

## 8. 系统架构

项目采用前后端分离架构：

```text
Vue 3 前端
  -> src/api 统一请求后端
  -> pages 展示各业务页面

FastAPI 后端
  -> api/routes 处理 HTTP 请求
  -> schemas 定义请求和响应结构
  -> services 编排业务流程和 AI 调用
  -> repositories 封装数据库读写
  -> models 定义 SQLite 表结构
  -> ai/AIClient 封装 OpenAI-compatible 模型调用

SQLite
  -> 保存用户资料、项目、JD、AI 分析结果和简历版本

prompts/
  -> 保存 JD 分析、匹配评分、简历生成、风险检测和面试追问 Prompt
```

这种结构避免把业务逻辑集中在一个大文件里，也方便后续升级模型供应商、数据库或导出能力。

## 9. 数据流流程

核心数据流如下：

```text
通用简历 ResumeProfile
        +
项目经历 Project[]
        +
岗位 JD JobDescription
        |
        v
JD 分析 JobAnalysis
        |
        v
匹配报告 MatchReport
        |
        v
定制简历 ResumeVersion
        |
        +--> 真实性风险检测 TruthCheckResult
        |
        +--> 面试追问预测 InterviewQuestionResult
        |
        v
Markdown 导出
```

其中用户原始资料和 AI 生成结果分开存储，便于追溯生成来源，也便于后续做版本管理和审计。

## 10. AI 调用流程

AI 调用集中在后端 service 层，不由前端直接访问模型供应商。

1. 前端提交用户选择或输入的数据。
2. 后端 route 接收请求并调用对应 service。
3. service 从 repository 读取 SQLite 中的上下文数据。
4. service 通过 PromptLoader 读取 `prompts/` 中的 Prompt。
5. service 调用统一 `AIClient`。
6. `AIClient` 使用 OpenAI-compatible `chat/completions` 格式请求模型。
7. 后端解析 AI 返回的稳定 JSON。
8. 解析后的结果保存到数据库，并返回给前端展示。

AI 配置来自环境变量：

```text
AI_PROVIDER=deepseek
AI_BASE_URL=https://api.deepseek.com
AI_API_KEY=your_deepseek_api_key_here
AI_MODEL=deepseek-chat
```

## 11. 项目亮点

- 完整闭环：从简历输入、JD 分析、匹配报告、定制简历到风险检测、面试追问和导出。
- 结构清晰：后端按 route、schema、service、repository、model 分层。
- AI 可替换：使用 OpenAI-compatible 抽象，不和 DeepSeek 强绑定。
- Prompt 独立管理：核心 Prompt 放在 `prompts/` 目录，便于迭代。
- 注重真实性：多处约束“不编造经历、不夸大成果、不把未提供技能写成已掌握”。
- 结果可追溯：AI 原始 JSON、修改原因、匹配报告和风险检测结果均可保存。
- 适合 Demo：页面流程清晰，首页提供完整演示路径。

## 12. 已完成模块

1. 首页 Dashboard 演示流程与统计。
2. 通用简历输入模块。
3. 项目库管理模块。
4. 岗位 JD 分析模块。
5. 简历与岗位匹配度报告模块。
6. 定制简历生成模块。
7. 真实性风险检测模块。
8. 面试追问预测模块。
9. Markdown 导出模块。

## 13. 可扩展方向

- 用户登录与云端同步。
- PostgreSQL 替换 SQLite。
- PDF/Word 导出。
- 更多简历模板。
- 多模型供应商配置界面。
- 简历版本对比。
- 求职进度管理。
- 更完整的权限、会员和支付系统。
- 招聘网站数据接入，但需要在隐私和合规基础上谨慎设计。

## 14. 总结

ResumeFit 当前完成了一个可演示的智能简历定制 Demo。项目重点不在于把功能做得很复杂，而在于证明一条清晰的产品链路：用户提供真实资料，系统分析岗位需求，生成匹配报告和定制简历，再通过真实性风险检测和面试追问帮助用户更稳妥地准备投递与面试。

从工程角度看，项目使用 Vue 3、FastAPI、SQLite 和 OpenAI-compatible AI service，结构清晰，功能边界明确，后续可以继续向商业化软件演进。
