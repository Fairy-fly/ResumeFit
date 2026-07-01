# Database Schema

ResumeFit 默认使用 SQLite。数据库文件在本地开发时通常为 `backend/resumefit.db`，该文件不应提交到 Git。

## users

用户表，支持多用户登录、状态管理和基础角色。

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `email` | 登录邮箱，唯一 |
| `password_hash` | 密码哈希，不保存明文密码 |
| `display_name` | 显示名称 |
| `role` | `user` 或 `admin` |
| `status` | `active` 或 `disabled` |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

## resume_profiles

通用简历表。

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `user_id` | 所属用户 |
| `title` | 简历标题 |
| `raw_markdown` | 原始简历 Markdown / 文本 |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

## projects

项目经历表。

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `user_id` | 所属用户 |
| `name` | 项目名称 |
| `project_type` | 项目类型 |
| `role` | 用户角色 |
| `tech_stack_json` | 技术栈 JSON |
| `description` | 项目描述 |
| `user_contribution` | 个人贡献 |
| `work_url` | 作品或项目链接 |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

## job_descriptions

岗位 JD 表。

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `user_id` | 所属用户 |
| `company_name` | 公司名称 |
| `title` | 岗位名称 |
| `raw_text` | JD 原文 |
| `status` | 分析状态 |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

## job_analyses

JD 分析结果表。该表通过 `job_description_id` 关联 JD，再由 JD 归属用户。

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `job_description_id` | 关联 JD |
| `required_skills_json` | 必备技能 |
| `preferred_skills_json` | 加分技能 |
| `responsibilities_json` | 岗位职责 |
| `keywords_json` | 关键词 |
| `resume_focus_json` | 简历侧重点建议 |
| `raw_ai_output_json` | AI 原始结构化输出 |
| `model_name` | 使用模型 |
| `created_at` | 创建时间 |

## match_reports

匹配度报告表。

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `user_id` | 所属用户 |
| `resume_profile_id` | 关联简历 |
| `job_description_id` | 关联 JD |
| `project_ids_json` | 参与匹配的项目 ID |
| `score` | 匹配分数 |
| `strengths_json` | 优势 |
| `gaps_json` | 差距 |
| `suggestions_json` | 修改建议 |
| `raw_ai_output_json` | AI 原始输出 |
| `model_name` | 使用模型 |
| `created_at` | 创建时间 |

## resume_versions

定制简历版本表。

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `user_id` | 所属用户 |
| `resume_profile_id` | 关联简历 |
| `job_description_id` | 关联 JD |
| `match_report_id` | 关联匹配报告 |
| `title` | 版本标题 |
| `version_type` | 版本类型 |
| `content_markdown` | 定制简历 Markdown 内容 |
| `change_explanations_json` | 修改原因 |
| `raw_ai_output_json` | AI 原始输出 |
| `model_name` | 使用模型 |
| `created_at` | 创建时间 |

## truth_check_results

真实性风险检测结果表。

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `user_id` | 所属用户 |
| `resume_version_id` | 关联简历版本 |
| `summary` | 总结 |
| `risk_items_json` | 风险项 |
| `raw_ai_output_json` | AI 原始输出 |
| `model_name` | 使用模型 |
| `created_at` | 创建时间 |

## interview_question_results

面试追问预测结果表。

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `user_id` | 所属用户 |
| `resume_version_id` | 关联简历版本 |
| `questions_json` | 追问问题数组 |
| `summary` | 本次预测总结 |
| `raw_ai_output_json` | AI 原始输出 |
| `model_name` | 使用模型 |
| `created_at` | 创建时间 |

## ai_usage_logs

AI 调用日志表，用于统计用户用量和月度额度。

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `user_id` | 所属用户 |
| `feature` | 功能类型，如 `jd_analysis`、`match_report` |
| `model` | 使用模型 |
| `success` | 是否成功 |
| `error_message` | 错误信息 |
| `input_tokens` | 输入 token，可为空 |
| `output_tokens` | 输出 token，可为空 |
| `total_tokens` | 总 token，可为空 |
| `estimated_cost` | 估算成本，可为空 |
| `created_at` | 创建时间 |

## 数据隔离规则

- 创建数据时，后端使用 JWT 当前用户 ID 写入 `user_id`。
- 查询数据时，repository 层按 `user_id` 过滤。
- 跨表生成流程会校验简历、项目、JD、匹配报告和简历版本均属于当前用户。
- 管理后台不返回 `password_hash`、token 或用户敏感简历正文。
