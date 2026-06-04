<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { createMatchReport, type MatchReportRead } from "../api/analyses";
import { listJobDescriptions, type JobDescriptionRead } from "../api/jobDescriptions";
import { listProjects, type ProjectRead } from "../api/projects";
import { listResumeProfiles, type ResumeProfileRead } from "../api/resumeProfiles";
import EmptyState from "../components/common/EmptyState.vue";

const resumes = ref<ResumeProfileRead[]>([]);
const projects = ref<ProjectRead[]>([]);
const jobDescriptions = ref<JobDescriptionRead[]>([]);
const selectedResumeId = ref<number | null>(null);
const selectedProjectIds = ref<number[]>([]);
const selectedJobDescriptionId = ref<number | null>(null);
const report = ref<MatchReportRead | null>(null);
const isLoading = ref(false);
const isGenerating = ref(false);
const errorMessage = ref("");

const analyzedJobDescriptions = computed(() =>
  jobDescriptions.value.filter((jobDescription) => jobDescription.status === "analyzed")
);

const canGenerate = computed(
  () =>
    selectedResumeId.value !== null &&
    selectedProjectIds.value.length > 0 &&
    selectedJobDescriptionId.value !== null
);

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function previewText(value: string): string {
  const normalized = value.replace(/\s+/g, " ").trim();
  if (normalized.length <= 100) {
    return normalized;
  }

  return `${normalized.slice(0, 100)}...`;
}

function messageFromError(error: unknown): string {
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }

  return "匹配报告生成失败，请检查选择内容、AI 配置或后端服务状态。";
}

async function loadOptions(): Promise<void> {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const [loadedResumes, loadedProjects, loadedJobDescriptions] = await Promise.all([
      listResumeProfiles(),
      listProjects(),
      listJobDescriptions()
    ]);
    resumes.value = loadedResumes;
    projects.value = loadedProjects;
    jobDescriptions.value = loadedJobDescriptions;
    selectedResumeId.value = loadedResumes[0]?.id ?? null;
    selectedJobDescriptionId.value =
      loadedJobDescriptions.find((jobDescription) => jobDescription.status === "analyzed")?.id ?? null;
  } catch (error) {
    errorMessage.value = messageFromError(error);
  } finally {
    isLoading.value = false;
  }
}

function toggleProject(projectId: number): void {
  if (selectedProjectIds.value.includes(projectId)) {
    selectedProjectIds.value = selectedProjectIds.value.filter((id) => id !== projectId);
    return;
  }

  selectedProjectIds.value = [...selectedProjectIds.value, projectId];
}

async function handleSubmit(): Promise<void> {
  if (!canGenerate.value || isGenerating.value || selectedResumeId.value === null || selectedJobDescriptionId.value === null) {
    return;
  }

  isGenerating.value = true;
  errorMessage.value = "";
  report.value = null;

  try {
    report.value = await createMatchReport({
      resume_profile_id: selectedResumeId.value,
      project_ids: selectedProjectIds.value,
      job_description_id: selectedJobDescriptionId.value
    });
  } catch (error) {
    errorMessage.value = messageFromError(error);
  } finally {
    isGenerating.value = false;
  }
}

onMounted(() => {
  void loadOptions();
});
</script>

<template>
  <section class="analysis-page">
    <div class="page-header">
      <h1 class="page-title">匹配度报告</h1>
      <button class="secondary-button" type="button" :disabled="isLoading" @click="loadOptions">
        {{ isLoading ? "加载中..." : "刷新数据" }}
      </button>
    </div>

    <form class="analysis-form" @submit.prevent="handleSubmit">
      <section class="selector-section" aria-labelledby="resume-selector-title">
        <h2 id="resume-selector-title">选择通用简历</h2>
        <EmptyState
          v-if="!isLoading && resumes.length === 0"
          title="还没有通用简历"
          description="先填写一份通用简历，后续才能进行岗位匹配和定制生成。"
          action-text="去填写通用简历"
          action-to="/resume"
        />
        <label v-for="resume in resumes" :key="resume.id" class="option-item">
          <input v-model.number="selectedResumeId" type="radio" name="resume" :value="resume.id" />
          <span>
            <strong>{{ resume.title }}</strong>
            <small>{{ previewText(resume.raw_markdown) }}</small>
          </span>
        </label>
      </section>

      <section class="selector-section" aria-labelledby="project-selector-title">
        <h2 id="project-selector-title">选择项目经历</h2>
        <EmptyState
          v-if="!isLoading && projects.length === 0"
          title="还没有项目经历"
          description="添加项目经历后，系统才能结合真实项目判断岗位匹配度。"
          action-text="去添加项目经历"
          action-to="/projects"
        />
        <label v-for="project in projects" :key="project.id" class="option-item">
          <input
            type="checkbox"
            :checked="selectedProjectIds.includes(project.id)"
            @change="toggleProject(project.id)"
          />
          <span>
            <strong>{{ project.name }}</strong>
            <small>{{ project.project_type }} · {{ project.role }}</small>
          </span>
        </label>
      </section>

      <section class="selector-section" aria-labelledby="job-selector-title">
        <h2 id="job-selector-title">选择已分析 JD</h2>
        <EmptyState
          v-if="!isLoading && analyzedJobDescriptions.length === 0"
          title="还没有已分析 JD"
          description="粘贴目标岗位 JD 并完成分析后，才能生成匹配度报告。"
          action-text="去粘贴并分析 JD"
          action-to="/jobs"
        />
        <label v-for="jobDescription in analyzedJobDescriptions" :key="jobDescription.id" class="option-item">
          <input v-model.number="selectedJobDescriptionId" type="radio" name="job-description" :value="jobDescription.id" />
          <span>
            <strong>{{ jobDescription.job_title }}</strong>
            <small>{{ jobDescription.company_name }} · {{ formatDate(jobDescription.updated_at) }}</small>
          </span>
        </label>
      </section>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <p
        v-if="!isLoading && !report && resumes.length > 0 && projects.length > 0 && analyzedJobDescriptions.length > 0"
        class="muted-text"
      >
        选择一份简历、至少一个项目和一个已分析 JD 后，点击下方按钮生成匹配报告。
      </p>

      <button class="primary-button" type="submit" :disabled="!canGenerate || isGenerating">
        {{ isGenerating ? "生成中..." : "生成匹配报告" }}
      </button>
    </form>

    <section v-if="report" class="report-section" aria-labelledby="report-title">
      <div class="section-header">
        <div>
          <h2 id="report-title">匹配结果</h2>
          <p class="muted-text">模型：{{ report.model_name }} · {{ formatDate(report.created_at) }}</p>
        </div>
        <div class="score-badge" aria-label="匹配分数">{{ report.score }}</div>
      </div>

      <div class="report-grid">
        <article class="report-card">
          <h3>优势</h3>
          <ul>
            <li v-for="item in report.strengths" :key="item">{{ item }}</li>
            <li v-if="report.strengths.length === 0">暂无明显优势。</li>
          </ul>
        </article>

        <article class="report-card">
          <h3>不足</h3>
          <ul>
            <li v-for="item in report.weaknesses" :key="item">{{ item }}</li>
            <li v-if="report.weaknesses.length === 0">暂无明显不足。</li>
          </ul>
        </article>

        <article class="report-card">
          <h3>缺失关键词</h3>
          <div class="tag-list">
            <span v-for="keyword in report.missing_keywords" :key="keyword">{{ keyword }}</span>
            <span v-if="report.missing_keywords.length === 0">暂无</span>
          </div>
        </article>

        <article class="report-card">
          <h3>修改建议</h3>
          <ul>
            <li v-for="item in report.recommended_changes" :key="item">{{ item }}</li>
            <li v-if="report.recommended_changes.length === 0">暂无建议。</li>
          </ul>
        </article>

        <article class="report-card wide">
          <h3>真实性提醒</h3>
          <ul>
            <li v-for="item in report.truthfulness_warnings" :key="item">{{ item }}</li>
            <li v-if="report.truthfulness_warnings.length === 0">暂无真实性风险提醒。</li>
          </ul>
        </article>
      </div>
    </section>
  </section>
</template>

<style scoped>
.analysis-page {
  display: grid;
  gap: 24px;
  max-width: 1100px;
}

.page-header,
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.analysis-form,
.selector-section,
.report-section {
  display: grid;
  gap: 16px;
}

.selector-section h2,
.report-card h3 {
  margin: 0;
}

.selector-section h2 {
  font-size: 20px;
}

.option-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  color: #343944;
  cursor: pointer;
  padding: 14px;
}

.option-item input {
  margin-top: 4px;
}

.option-item span {
  display: grid;
  gap: 5px;
}

.option-item small {
  color: #667085;
  line-height: 1.5;
}

.primary-button,
.secondary-button {
  width: fit-content;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

.primary-button {
  background: #243b99;
  color: #ffffff;
  padding: 12px 18px;
}

.secondary-button {
  background: #e6e9f2;
  color: #263044;
  padding: 9px 14px;
}

.primary-button:disabled,
.secondary-button:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.score-badge {
  display: grid;
  place-items: center;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #243b99;
  color: #ffffff;
  font-size: 28px;
  font-weight: 800;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.report-card {
  display: grid;
  gap: 12px;
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.report-card.wide {
  grid-column: 1 / -1;
}

.report-card h3 {
  color: #1d1f24;
  font-size: 18px;
}

.report-card ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 20px;
}

.report-card li {
  color: #4d5564;
  line-height: 1.6;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-list span {
  border-radius: 999px;
  background: #eef2ff;
  color: #243b99;
  font-size: 13px;
  font-weight: 700;
  padding: 5px 9px;
}

.muted-text {
  color: #667085;
  margin: 0;
}

.error-message {
  margin: 0;
  color: #b42318;
  font-weight: 600;
}

@media (max-width: 760px) {
  .page-header,
  .section-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .report-grid {
    grid-template-columns: 1fr;
  }
}
</style>
