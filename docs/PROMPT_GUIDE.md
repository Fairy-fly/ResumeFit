# Prompt Guide

ResumeFit 的 Prompt 统一放在 `prompts/` 目录，后端通过 Prompt Loader 加载。业务代码不散落大段 Prompt，方便版本管理、审查和替换模型。

## Prompt 文件

| 文件 | 用途 |
| --- | --- |
| `prompts/jd_analyzer_v1.md` | JD 结构化分析 |
| `prompts/match_scorer_v1.md` | 简历、项目与 JD 的匹配度分析 |
| `prompts/resume_writer_v1.md` | 岗位定制简历生成 |
| `prompts/truth_checker_v1.md` | 真实性风险检测 |
| `prompts/interview_question_v1.md` | 面试追问预测 |
| `prompts/shared/authenticity_rules.md` | 通用真实性约束 |
| `prompts/shared/output_format_rules.md` | 结构化输出规则 |

仓库中保留了一些早期 prompt 文件用于兼容和对照，实际使用时应优先查看当前 service 加载的版本化 prompt。

## 真实性约束

所有 AI 能力都必须遵守：

- 不编造工作经历、项目经历、公司名称、岗位名称、学历、证书、技术掌握程度和量化成果。
- 可以改写用户提供的信息，但不能新增事实。
- 信息不足时，应提醒用户补充证据或保守表达。
- 建议回答必须真实、可解释、可追溯。
- 风险检测和面试追问应指出证据缺口，而不是教用户编造。

## 输出格式

后端期望 AI 尽量返回结构化 JSON。这样可以：

- 进行 schema 校验。
- 将结果稳定保存到数据库。
- 在前端按字段展示。
- 方便测试和回归。

如果 AI 返回非 JSON、空结果或 schema 不匹配，后端会返回清晰错误，前端会转换成友好的用户提示。

## AIClient 抽象

项目使用 `AIClient` 作为统一 AI 调用入口：

- 默认可接入 DeepSeek。
- 配置使用 `AI_BASE_URL`、`AI_API_KEY`、`AI_MODEL`。
- 兼容 OpenAI-style chat completion。
- 测试中 mock `AIClient`，不真实调用模型。

不要在前端直接调用模型供应商 API，也不要在业务 service 之外散落供应商特定调用。

## 调试建议

- 优先检查 Prompt 是否明确要求 JSON。
- 检查真实性规则是否被组合进上下文。
- 检查 service 是否传入了必要的简历、项目、JD、分析报告和历史结果。
- 不要在日志中输出完整简历或敏感资料。
- 不要提交真实 API Key。
