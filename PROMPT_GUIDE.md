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

### job_analysis.md

用途：分析岗位 JD。

输入：

- 原始 JD 文本

输出：

- 岗位概述
- 核心职责
- 必备技能
- 加分技能
- 业务领域
- 关键词
- 隐含要求
- 简历优化方向

建议输出 JSON，便于存入 `JobAnalysis`。

### match_report.md

用途：评估用户简历与 JD 的匹配度。

输入：

- `ResumeProfile`
- `Project[]`
- `JobDescription`
- `JobAnalysis`

输出：

- 总分
- 分项评分
- 匹配优势
- 能力缺口
- 项目匹配说明
- 简历优化建议

评分必须说明依据，不能声称代表真实招聘结果。

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

