# Database Schema

## 1. 设计原则

MVP 使用 SQLite，数据结构应足够简单，同时为后续 PostgreSQL 和商业化能力预留空间。

原则：

- 所有核心业务对象都应带 `created_at` 和 `updated_at`。
- AI 生成结果应保留原始 JSON，方便后续调试和结构升级。
- 用户真实资料和 AI 生成内容要分开存储。
- 简历版本必须能追溯来源 JD、匹配报告和生成方式。
- V0.3 已进入多用户基础版，核心业务表必须通过 `user_id` 做数据隔离。

## 2. 实体总览

必须预留的数据结构：

- `User`
- `ResumeProfile`
- `Project`
- `JobDescription`
- `JobAnalysis`
- `MatchReport`
- `ResumeVersion`
- `TruthCheckResult`
- `InterviewQuestionResult`

建议关系：

```text
User 1..n ResumeProfile
User 1..n Project
User 1..n JobDescription
JobDescription 1..1 JobAnalysis
JobDescription 1..n MatchReport
ResumeProfile 1..n MatchReport
ResumeProfile 1..n ResumeVersion
JobDescription 1..n ResumeVersion
ResumeVersion 1..n TruthCheckResult
ResumeVersion 1..n InterviewQuestionResult
```

## 3. 表结构建议

### users

V0.3 已使用 `users` 表支持注册、登录、JWT 当前用户识别和数据隔离。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | 用户 ID |
| email | TEXT | 登录邮箱，唯一 |
| password_hash | TEXT | 密码哈希，不保存明文密码 |
| display_name | TEXT | 显示名称 |
| status | TEXT | active, disabled |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

认证相关配置不写入数据库，来自 `.env`：

```text
JWT_SECRET_KEY=change_me_for_local_dev_secret_please_replace
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

V0.5 个人中心继续复用 `users` 表，不新增账户设置表。`GET /account/me` 从当前登录用户读取 `email`、`display_name`、`status`、`created_at`、`updated_at`，并聚合 V0.4 `usage_summary`。`PATCH /account/me` 只更新当前用户的 `display_name`，不允许修改 `email`、`status`、`password_hash`、角色或额度字段。

### resume_profiles

通用简历资料，是生成定制简历的主要事实来源。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | 简历资料 ID |
| user_id | INTEGER | 关联 users.id |
| title | TEXT | 简历名称，例如“后端开发通用简历” |
| target_role | TEXT | 求职方向 |
| basic_info_json | TEXT | 基本信息 JSON |
| education_json | TEXT | 教育经历 JSON |
| work_experience_json | TEXT | 工作经历 JSON |
| skills_json | TEXT | 技能 JSON |
| summary | TEXT | 自我介绍或职业摘要 |
| raw_markdown | TEXT | 用户原始 Markdown 简历，可选 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### projects

项目库，记录用户真实项目经历。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | 项目 ID |
| user_id | INTEGER | 关联 users.id |
| name | TEXT | 项目名称 |
| project_type | TEXT | 项目类型，例如 Web 应用、AI 工具、数据分析 |
| role | TEXT | 用户在项目中的角色，例如独立开发、组长、组员、负责人 |
| tech_stack_json | TEXT | 技术栈 JSON |
| description | TEXT | 项目描述 |
| user_contribution | TEXT | 用户个人贡献 |
| evidence_links_json | TEXT | 作品链接或证明链接 JSON |
| resume_description | TEXT | 面向简历生成的项目描述，可为空 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### job_descriptions

目标岗位 JD。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | JD ID |
| user_id | INTEGER | 关联 users.id |
| title | TEXT | 岗位名称 |
| company_name | TEXT | 公司名称，可为空 |
| source_url | TEXT | 来源链接，可为空 |
| raw_text | TEXT | 原始 JD |
| status | TEXT | draft, analyzed, archived |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### job_analyses

JD 结构化分析结果。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | 分析 ID |
| job_description_id | INTEGER | 关联 job_descriptions.id |
| job_title | TEXT | AI 提取或输入中的岗位名称 |
| job_type | TEXT | 岗位类型，例如后端开发、前端开发、数据分析 |
| role_summary | TEXT | 岗位概述 |
| responsibilities_json | TEXT | 职责 JSON |
| required_skills_json | TEXT | 必备技能 JSON |
| preferred_skills_json | TEXT | 加分技能 JSON |
| keywords_json | TEXT | 关键词 JSON |
| seniority_level | TEXT | 级别判断 |
| domain | TEXT | 业务领域 |
| resume_focus_suggestions_json | TEXT | 简历突出建议 JSON |
| raw_ai_output_json | TEXT | AI 原始输出 |
| model_name | TEXT | 使用模型 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### match_reports

简历与 JD 的匹配报告。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | 匹配报告 ID |
| user_id | INTEGER | 关联 users.id |
| resume_profile_id | INTEGER | 关联 resume_profiles.id |
| job_description_id | INTEGER | 关联 job_descriptions.id |
| job_analysis_id | INTEGER | 关联 job_analyses.id |
| project_ids_json | TEXT | 本次用于匹配的项目 ID JSON |
| overall_score | INTEGER | 0 到 100 |
| skill_score | INTEGER | 技能匹配分，MVP v1 可为空 |
| project_score | INTEGER | 项目匹配分，MVP v1 可为空 |
| domain_score | INTEGER | 领域匹配分，MVP v1 可为空 |
| expression_score | INTEGER | 表达匹配分，MVP v1 可为空 |
| strengths_json | TEXT | 优势 JSON |
| gaps_json | TEXT | 短板 JSON |
| missing_keywords_json | TEXT | 缺失关键词 JSON |
| suggestions_json | TEXT | 优化建议 JSON |
| truthfulness_warnings_json | TEXT | 真实性提醒 JSON |
| raw_ai_output_json | TEXT | AI 原始输出 |
| model_name | TEXT | 使用模型 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### resume_versions

保存通用版本和岗位定制版本。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | 简历版本 ID |
| user_id | INTEGER | 关联 users.id |
| resume_profile_id | INTEGER | 关联 resume_profiles.id |
| job_description_id | INTEGER | 可选关联 job_descriptions.id |
| match_report_id | INTEGER | 可选关联 match_reports.id |
| title | TEXT | 版本标题 |
| version_type | TEXT | base, tailored, manual |
| content_markdown | TEXT | Markdown 简历内容 |
| generation_notes | TEXT | 生成说明 |
| change_explanations_json | TEXT | 修改原因 JSON，说明每处重组、压缩、突出或润色的原因 |
| risk_report_json | TEXT | 真实性风险结果 JSON |
| raw_ai_output_json | TEXT | AI 原始输出 |
| model_name | TEXT | 使用模型 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### truth_check_results

保存定制简历版本的真实性风险检测历史结果。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | 检测结果 ID |
| user_id | INTEGER | 关联 users.id |
| resume_version_id | INTEGER | 关联 resume_versions.id |
| overall_risk_level | TEXT | low, medium, high |
| risky_statements_json | TEXT | 风险表达 JSON |
| safer_rewrites_json | TEXT | 更稳妥改法 JSON |
| missing_evidence_json | TEXT | 缺失证据 JSON |
| interview_risk_points_json | TEXT | 面试追问风险点 JSON，不等同于面试追问模块 |
| summary | TEXT | 检测总结 |
| raw_ai_output_json | TEXT | AI 原始输出 |
| model_name | TEXT | 使用模型 |
| created_at | DATETIME | 创建时间 |

### interview_question_results

保存定制简历版本的面试追问预测历史结果。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | 预测结果 ID |
| user_id | INTEGER | 关联 users.id |
| resume_version_id | INTEGER | 关联 resume_versions.id |
| questions_json | TEXT | 面试追问列表 JSON |
| summary | TEXT | 本次预测总结 |
| raw_ai_output_json | TEXT | AI 原始输出 |
| model_name | TEXT | 使用模型 |
| created_at | DATETIME | 创建时间 |

## 4. 索引建议

MVP 建议索引：

```sql
CREATE INDEX idx_resume_profiles_user_id ON resume_profiles(user_id);
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_job_descriptions_user_id ON job_descriptions(user_id);
CREATE INDEX idx_job_analyses_job_description_id ON job_analyses(job_description_id);
CREATE INDEX idx_match_reports_resume_profile_id ON match_reports(resume_profile_id);
CREATE INDEX idx_match_reports_job_description_id ON match_reports(job_description_id);
CREATE INDEX idx_resume_versions_user_id ON resume_versions(user_id);
CREATE INDEX idx_resume_versions_job_description_id ON resume_versions(job_description_id);
CREATE INDEX idx_truth_check_results_resume_version_id ON truth_check_results(resume_version_id);
CREATE INDEX idx_interview_question_results_resume_version_id ON interview_question_results(resume_version_id);
```

## 5. JSON 字段说明

SQLite 中可以先用 TEXT 存 JSON，应用层负责序列化和反序列化。后续升级 PostgreSQL 时，可将部分字段迁移为 `JSONB`。

适合 JSON 的字段：

- 技能列表
- 项目技术栈
- JD 关键词
- AI 结构化输出
- 匹配优势和短板
- 风险检测报告

不适合 JSON 的字段：

- 高频查询条件
- 明确关系数据
- 后续需要独立权限或审计的数据

## 6. V0.3 用户隔离说明

V0.3 已实现基础多用户隔离。以下表通过 `user_id` 直接归属于用户：

- `resume_profiles`
- `projects`
- `job_descriptions`
- `match_reports`
- `resume_versions`
- `truth_check_results`
- `interview_question_results`

`job_analyses` 当前不直接保存 `user_id`，通过 `job_description_id -> job_descriptions.user_id` 校验归属。

后端读取和生成数据时必须遵守：

- 列表接口只返回当前登录用户的数据。
- 创建接口写入当前登录用户的 `user_id`。
- 跨表生成流程必须校验所有输入 ID 都属于当前用户。
- Markdown 导出必须通过 `resume_versions.user_id` 校验权限。
- 用户访问他人的资源时返回 `404`，避免泄露资源是否存在。

## 7. V0.4 AI 用量日志表

### 7.1 ai_usage_logs

V0.4 已新增 `ai_usage_logs`，用于记录 AI 调用次数、成功/失败、token usage 和估算成本，为后续额度与商业化做准备。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | INTEGER | 主键 |
| user_id | INTEGER | 所属用户 |
| feature_type | TEXT | 功能类型，例如 jd_analysis、match_report、resume_generation、truth_check、interview_question |
| model_name | TEXT | 使用模型 |
| status | TEXT | success 或 failed |
| error_message | TEXT | 失败原因，成功时为空 |
| input_tokens | INTEGER | 输入 token，供应商未返回时为空 |
| output_tokens | INTEGER | 输出 token，供应商未返回时为空 |
| total_tokens | INTEGER | 总 token，供应商未返回时为空 |
| estimated_cost | REAL | 估算成本，无法估算时为空 |
| created_at | DATETIME | 创建时间 |

V0.4 额度单位是“每月 AI 调用次数”，配置来自 `.env`：

```text
AI_MONTHLY_CALL_LIMIT=100
AI_INPUT_TOKEN_PRICE_PER_1K=0
AI_OUTPUT_TOKEN_PRICE_PER_1K=0
```

## 8. 后续商业化扩展表

商业化阶段可新增：

- `subscriptions`
- `payments`
- `export_jobs`
- `resume_templates`
- `application_records`
- `user_settings`
- `provider_configs`

这些表不进入 MVP。
