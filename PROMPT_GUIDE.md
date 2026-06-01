# Prompt Guide

## 1. 目标

ResumeFit 的 Prompt 用于把用户真实资料、项目库和岗位 JD 转换为可解释、可追溯、可修改的求职辅助结果。

Prompt 必须服务以下原则：

- 不编造用户经历。
- 输出结构稳定。
- 便于后端解析和存储。
- 能提示不确定性和风险。
- 与具体 AI 供应商解耦。

## 2. Prompt 目录

所有 Prompt 文件放在项目根目录的 `prompts/` 下。

建议结构：

```text
prompts/
  job_analysis.md
  jd_analyzer_v1.md
  match_scorer_v1.md
  resume_writer_v1.md
  truth_checker_v1.md
  interview_question_v1.md
  match_report.md
  resume_generation.md
  risk_detection.md
  interview_questions.md
  shared/
    authenticity_rules.md
    output_format_rules.md
```

## 3. 通用规则

每个 Prompt 都应包含：

- 角色说明：模型当前扮演什么分析角色。
- 输入说明：会收到哪些上下文。
- 任务说明：需要完成什么。
- 真实性约束：不得虚构用户经历。
- 输出格式：优先 JSON 或 Markdown。
- 失败处理：信息不足时如何表达。

通用真实性约束示例：

```text
你不能编造用户没有提供的工作经历、项目经历、学历、证书、公司、职位、成果指标或技术经验。
如果信息不足，请明确标记为“信息不足”或提出需要用户补充的问题。
你可以优化表达、重组内容、突出重点，但不能创造事实。
```

## 4. Prompt 文件职责

### jd_analyzer_v1.md

用途：分析岗位 JD。

输入：

- 公司名称
- 岗位名称
- 原始 JD 文本

输出：

- 岗位名称
- 岗位类型
- 必备技能
- 加分技能
- 核心职责
- 关键词
- 简历优化方向

必须输出 JSON，便于存入 `JobAnalysis`。不得补写 JD 中没有出现的信息；信息不足时使用空数组或“信息不足”。

### match_scorer_v1.md

用途：评估用户简历与 JD 的匹配度。

输入：

- `ResumeProfile`
- `Project[]`
- `JobDescription`
- `JobAnalysis`

输出：

- 总分
- 匹配优势
- 能力缺口
- 缺失关键词
- 简历优化建议
- 真实性提醒

评分必须基于用户已提供材料，不能声称代表真实招聘结果，不能把缺失技能写成用户已经掌握。

### resume_writer_v1.md

用途：生成岗位定制 Markdown 简历，并输出结构化修改原因。

输入：

- `ResumeProfile`
- 用户选择的 `Project[]`
- `JobDescription`
- `JobAnalysis`
- `MatchReport`

输出：

- `markdown`：Markdown 简历正文
- `change_explanations`：每处修改原因，包含 `section`、`reason`、`source`、`uncertain`

要求：

- 不新增用户没有提供的经历、学历、公司、证书、项目成果、技能掌握情况或量化指标。
- 只能重组、压缩、突出、润色已提供内容。
- 对不确定内容必须标记 `uncertain: true`。
- 必须输出稳定 JSON，便于保存到 `ResumeVersion.change_explanations_json` 和 `content_markdown`。

### resume_generation.md

用途：生成岗位定制 Markdown 简历。

输入：

- 通用简历
- 项目库
- JD 分析
- 匹配报告

输出：

- Markdown 简历
- 使用了哪些原始材料
- 未使用哪些材料及原因
- 不确定信息提示

要求：

- 不新增事实。
- 不夸大年限。
- 不生成无法自证的指标。
- 不把 JD 关键词生硬堆砌进简历。

### truth_checker_v1.md

用途：检测已生成定制简历中的真实性风险。

输入：

- `ResumeVersion`
- 原始 `ResumeProfile`
- 本次选择的 `Project[]`
- `JobDescription`
- `JobAnalysis`
- `MatchReport`

输出：

- `overall_risk_level`
- `risky_statements`
- `safer_rewrites`
- `missing_evidence`
- `interview_risk_points`
- `summary`

要求：

- 不编造、不补写、不替用户验证外部事实。
- 检查夸大技能、缺少证据的量化成果、角色夸大、项目规模夸大、不确定内容确定化等问题。
- `interview_risk_points` 只提示风险点，不生成完整面试追问问题。
- 必须输出稳定 JSON，便于保存到 `TruthCheckResult`。

### interview_question_v1.md

用途：基于定制简历、岗位 JD、项目经历、匹配报告和可选真实性风险检测结果，预测面试官可能追问的问题。

输入：

- `ResumeVersion`
- 原始 `ResumeProfile`
- 本次选择的 `Project[]`
- `JobDescription`
- `JobAnalysis`
- `MatchReport`
- 最新 `TruthCheckResult`，如果存在

输出：

- `questions`
- `summary`

`questions` 每项包含：

- `question`
- `reason`
- `related_resume_section`
- `difficulty`
- `suggested_answer`
- `answer_strategy`
- `risk_reminder`

要求：

- 只能基于用户已提供资料预测追问。
- 不根据虚构经历生成问题。
- 建议回答必须保守、真实、可解释。
- 证据不足时必须提醒用户谨慎表达。
- 必须输出稳定 JSON，便于保存到 `InterviewQuestionResult`。

### risk_detection.md

用途：检测定制简历的真实性和面试风险。

输入：

- 原始简历资料
- 项目库
- 定制简历版本

输出：

- 风险等级
- 风险项
- 涉及简历片段
- 风险原因
- 修改建议

风险等级建议：

- low
- medium
- high

### interview_questions.md

用途：预测面试追问。

输入：

- JD
- JD 分析
- 定制简历
- 项目库

输出：

- 问题分类
- 追问问题
- 为什么会问
- 准备建议
- 难度

问题分类建议：

- project
- technical
- business
- metric
- behavior

## 5. 输出格式建议

对于结构化分析类 Prompt，建议要求模型输出 JSON：

```json
{
  "summary": "string",
  "items": [],
  "risks": [],
  "suggestions": []
}
```

后端应做 JSON 解析失败处理：

- 保存原始 AI 输出。
- 返回可读错误。
- 允许用户重试。
- 后续可增加输出修复 Prompt。

## 6. 模型兼容

Prompt 不应写死 DeepSeek、OpenAI、通义或智谱等供应商名称。

服务层负责：

- 选择模型。
- 设置 temperature。
- 设置 max tokens。
- 调用 OpenAI-compatible Chat Completions 接口。

Prompt 只描述任务，不依赖某个供应商的专有功能。

## 7. 推荐参数

MVP 建议：

- JD 分析：低 temperature，偏稳定。
- 匹配评分：低 temperature，偏一致。
- 简历生成：中低 temperature，允许表达优化但不放飞。
- 风险检测：低 temperature，偏严谨。
- 面试追问：中等 temperature，覆盖多样问题。

## 8. 安全与隐私

- Prompt 中不要包含 API Key。
- 日志中不要打印完整简历原文。
- 对用户隐私信息做最小必要传输。
- 后续商业化前应补充隐私政策、数据删除机制和用户授权说明。
