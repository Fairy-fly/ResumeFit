# Database Schema

## 1. 设计原则

MVP 使用 SQLite，数据结构应足够简单，同时为后续 PostgreSQL 和商业化能力预留空间。

原则：

- 所有核心业务对象都应带 `created_at` 和 `updated_at`。
- AI 生成结果应保留原始 JSON，方便后续调试和结构升级。
- 用户真实资料和 AI 生成内容要分开存储。
- 简历版本必须能追溯来源 JD、匹配报告和生成方式。
- MVP 可以先使用单用户模式，但仍预留 `User` 表。

## 2. 实体总览

必须预留的数据结构：

- `User`
- `ResumeProfile`
- `Project`
- `JobDescription`
- `JobAnalysis`
- `MatchReport`
- `ResumeVersion`
- `InterviewQuestion`

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
ResumeVersion 1..n InterviewQuestion
```

## 3. 表结构建议

### users

MVP 可只创建默认用户，后续接入登录系统。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | 用户 ID |
| email | TEXT | 后续登录使用，MVP 可为空 |
| display_name | TEXT | 显示名称 |
| status | TEXT | active, disabled |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

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
| overall_score | INTEGER | 0 到 100 |
| skill_score | INTEGER | 技能匹配分 |
| project_score | INTEGER | 项目匹配分 |
| domain_score | INTEGER | 领域匹配分 |
| expression_score | INTEGER | 表达匹配分 |
| strengths_json | TEXT | 优势 JSON |
| gaps_json | TEXT | 短板 JSON |
| suggestions_json | TEXT | 优化建议 JSON |
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
| risk_report_json | TEXT | 真实性风险结果 JSON |
| raw_ai_output_json | TEXT | AI 原始输出 |
| model_name | TEXT | 使用模型 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### interview_questions

面试追问预测。

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | 问题 ID |
| user_id | INTEGER | 关联 users.id |
| resume_version_id | INTEGER | 关联 resume_versions.id |
| job_description_id | INTEGER | 关联 job_descriptions.id |
| category | TEXT | project, technical, business, metric, behavior |
| question | TEXT | 问题内容 |
| reason | TEXT | 为什么会被问 |
| preparation_tip | TEXT | 准备建议 |
| difficulty | TEXT | easy, medium, hard |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

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
CREATE INDEX idx_interview_questions_resume_version_id ON interview_questions(resume_version_id);
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

## 6. 后续商业化扩展表

商业化阶段可新增：

- `subscriptions`
- `payments`
- `ai_usage_logs`
- `export_jobs`
- `resume_templates`
- `application_records`
- `user_settings`
- `provider_configs`

这些表不进入 MVP。
