<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { listMatchReports, type MatchReportRead } from "../api/analyses";
import { listJobDescriptions, type JobDescriptionRead } from "../api/jobDescriptions";
import { listProjects, type ProjectRead } from "../api/projects";
import { listResumeProfiles, type ResumeProfileRead } from "../api/resumeProfiles";
import { generateResumeVersion, type ResumeVersionRead } from "../api/resumeVersions";

const resumes = ref<ResumeProfileRead[]>([]);
const projects = ref<ProjectRead[]>([]);
const jobDescriptions = ref<JobDescriptionRead[]>([]);
const matchReports = ref<MatchReportRead[]>([]);
const selectedResumeId = ref<number | null>(null);
const selectedProjectIds = ref<number[]>([]);
const selectedJobDescriptionId = ref<number | null>(null);
const selectedMatchReportId = ref<number | null>(null);
const resumeVersion = ref<ResumeVersionRead | null>(null);
const isLoading = ref(false);
const isGenerating = ref(false);
const errorMessage = ref("");
const copyMessage = ref("");

const analyzedJobDescriptions = computed(() =>
  jobDescriptions.value.filter((jobDescription) => jobDescription.status === "analyzed")
);

const selectedMatchReport = computed(() =>
  matchReports.value.find((matchReport) => matchReport.id === selectedMatchReportId.value) ?? null
);

const canGenerate = computed(
  () =>
    selectedResumeId.value !== null &&
    selectedProjectIds.value.length > 0 &&
    selectedJobDescriptionId.value !== null &&
    selectedMatchReportId.value !== null
);

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function previewText(value: string): string {
  const normalized = value.replace(/\s+/g, " ").trim();
  if (normalized.length <= 90) {
    return normalized;
  }

  return `${normalized.slice(0, 90)}...`;
}

function messageFromError(error: unknown): string {
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }

  return "定制简历生成失败，请检查选择内容、AI 配置或后端服务状态。";
}

function findResumeTitle(resumeProfileId: number): string {
  return resumes.value.find((resume) => resume.id === resumeProfileId)?.title ?? `简历 #${resumeProfileId}`;
}

function findJobTitle(jobDescriptionId: number): string {
  const jobDescription = jobDescriptions.value.find((job) => job.id === jobDescriptionId);
  if (!jobDescription) {
    return `JD #${jobDescriptionId}`;
  }

  return `${jobDescription.company_name ?? "未填写公司"} · ${jobDescription.job_title}`;
}

function findProjectNames(projectIds: number[]): string {
  const names = projectIds.map((projectId) => {
    return projects.value.find((project) => project.id === projectId)?.name ?? `项目 #${projectId}`;
  });
  return names.join("、");
}

function applyMatchReport(matchReport: MatchReportRead): void {
  selectedMatchReportId.value = matchReport.id;
  selectedResumeId.value = matchReport.resume_profile_id;
  selectedProjectIds.value = [...matchReport.project_ids];
  selectedJobDescriptionId.value = matchReport.job_description_id;
  resumeVersion.value = null;
  copyMessage.value = "";
}

async function loadOptions(): Promise<void> {
  isLoading.value = true;
  errorMessage.value = "";
  copyMessage.value = "";

  try {
    const [loadedResumes, loadedProjects, loadedJobDescriptions, loadedMatchReports] = await Promise.all([
      listResumeProfiles(),
      listProjects(),
      listJobDescriptions(),
      listMatchReports()
    ]);
    resumes.value = loadedResumes;
    projects.value = loadedProjects;
    jobDescriptions.value = loadedJobDescriptions;
    matchReports.value = loadedMatchReports;

    if (loadedMatchReports.length > 0) {
      applyMatchReport(loadedMatchReports[0]);
      return;
    }

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

async function handleGenerate(): Promise<void> {
  if (
    !canGenerate.value ||
    isGenerating.value ||
    selectedResumeId.value === null ||
    selectedJobDescriptionId.value === null ||
    selectedMatchReportId.value === null
  ) {
    return;
  }

  isGenerating.value = true;
  errorMessage.value = "";
  copyMessage.value = "";
  resumeVersion.value = null;

  try {
    resumeVersion.value = await generateResumeVersion({
      resume_profile_id: selectedResumeId.value,
      project_ids: selectedProjectIds.value,
      job_description_id: selectedJobDescriptionId.value,
      match_report_id: selectedMatchReportId.value
    });
  } catch (error) {
    errorMessage.value = messageFromError(error);
  } finally {
    isGenerating.value = false;
  }
}

async function copyMarkdown(): Promise<void> {
  if (!resumeVersion.value) {
    return;
  }

  copyMessage.value = "";

  try {
    await navigator.clipboard.writeText(resumeVersion.value.content_markdown);
    copyMessage.value = "Markdown 已复制。";
  } catch {
    copyMessage.value = "复制失败，请手动选择 Markdown 内容复制。";
  }
}

onMounted(() => {
  void loadOptions();
});
</script>

<template>
  <section class="versions-page">
    <div class="page-header">
      <h1 class="page-title">定制简历</h1>
      <button class="secondary-button" type="button" :disabled="isLoading" @click="loadOptions">
        {{ isLoading ? "加载中..." : "刷新数据" }}
      </button>
    </div>

    <form class="version-form" @submit.prevent="handleGenerate">
      <section class="selector-section" aria-labelledby="match-report-selector-title">
        <h2 id="match-report-selector-title">选择匹配报告</h2>
        <p v-if="matchReports.length === 0" class="muted-text">还没有可用的匹配报告，请先在分析页面生成报告。</p>
        <label v-for="matchReport in matchReports" :key="matchReport.id" class="option-item">
          <input
            type="radio"
            name="match-report"
            :checked="selectedMatchReportId === matchReport.id"
            @change="applyMatchReport(matchReport)"
          />
          <span>
            <strong>报告 #{{ matchReport.id }} · {{ matchReport.score }} 分</strong>
            <small>
              {{ findResumeTitle(matchReport.resume_profile_id) }} ·
              {{ findJobTitle(matchReport.job_description_id) }} ·
              {{ formatDate(matchReport.created_at) }}
            </small>
          </span>
        </label>
      </section>

      <section class="selector-section" aria-labelledby="resume-selector-title">
        <h2 id="resume-selector-title">通用简历</h2>
        <p v-if="resumes.length === 0" class="muted-text">还没有可用的通用简历。</p>
        <label v-for="resume in resumes" :key="resume.id" class="option-item">
          <input v-model.number="selectedResumeId" type="radio" name="resume" :value="resume.id" />
          <span>
            <strong>{{ resume.title }}</strong>
            <small>{{ previewText(resume.raw_markdown) }}</small>
          </span>
        </label>
      </section>

      <section class="selector-section" aria-labelledby="project-selector-title">
        <h2 id="project-selector-title">项目经历</h2>
        <p v-if="projects.length === 0" class="muted-text">还没有可用的项目经历。</p>
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
        <h2 id="job-selector-title">已分析 JD</h2>
        <p v-if="analyzedJobDescriptions.length === 0" class="muted-text">还没有已分析的 JD，请先在 JD 页面完成分析。</p>
        <label v-for="jobDescription in analyzedJobDescriptions" :key="jobDescription.id" class="option-item">
          <input v-model.number="selectedJobDescriptionId" type="radio" name="job-description" :value="jobDescription.id" />
          <span>
            <strong>{{ jobDescription.job_title }}</strong>
            <small>{{ jobDescription.company_name }} · {{ formatDate(jobDescription.updated_at) }}</small>
          </span>
        </label>
      </section>

      <section v-if="selectedMatchReport" class="summary-section" aria-labelledby="selected-context-title">
        <h2 id="selected-context-title">当前上下文</h2>
        <dl>
          <div>
            <dt>简历</dt>
            <dd>{{ findResumeTitle(selectedMatchReport.resume_profile_id) }}</dd>
          </div>
          <div>
            <dt>项目</dt>
            <dd>{{ findProjectNames(selectedMatchReport.project_ids) }}</dd>
          </div>
          <div>
            <dt>岗位</dt>
            <dd>{{ findJobTitle(selectedMatchReport.job_description_id) }}</dd>
          </div>
        </dl>
      </section>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <button class="primary-button" type="submit" :disabled="!canGenerate || isGenerating">
        {{ isGenerating ? "生成中..." : "生成定制简历" }}
      </button>
    </form>

    <section v-if="resumeVersion" class="result-section" aria-labelledby="resume-version-title">
      <div class="section-header">
        <div>
          <h2 id="resume-version-title">{{ resumeVersion.title }}</h2>
          <p class="muted-text">
            模型：{{ resumeVersion.model_name }} · {{ resumeVersion.version_type }} ·
            {{ formatDate(resumeVersion.created_at) }}
          </p>
        </div>
        <button class="secondary-button" type="button" @click="copyMarkdown">复制 Markdown</button>
      </div>

      <p v-if="copyMessage" class="copy-message">{{ copyMessage }}</p>

      <article class="markdown-panel">
        <h3>Markdown 简历</h3>
        <pre>{{ resumeVersion.content_markdown }}</pre>
      </article>

      <article class="explanation-panel">
        <h3>修改原因</h3>
        <ul>
          <li v-for="item in resumeVersion.change_explanations" :key="`${item.section}-${item.reason}`">
            <div class="explanation-title">
              <strong>{{ item.section }}</strong>
              <span v-if="item.uncertain">uncertain</span>
            </div>
            <p>{{ item.reason }}</p>
            <small>来源：{{ item.source }}</small>
          </li>
          <li v-if="resumeVersion.change_explanations.length === 0">暂无修改说明。</li>
        </ul>
      </article>
    </section>
  </section>
</template>

<style scoped>
.versions-page {
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

.version-form,
.selector-section,
.summary-section,
.result-section {
  display: grid;
  gap: 16px;
}

.selector-section h2,
.summary-section h2,
.markdown-panel h3,
.explanation-panel h3 {
  margin: 0;
}

.selector-section h2,
.summary-section h2 {
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

.summary-section {
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.summary-section dl {
  display: grid;
  gap: 10px;
  margin: 0;
}

.summary-section dl div {
  display: grid;
  gap: 4px;
}

.summary-section dt {
  color: #667085;
  font-size: 13px;
  font-weight: 700;
}

.summary-section dd {
  margin: 0;
  color: #343944;
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

.markdown-panel,
.explanation-panel {
  display: grid;
  gap: 12px;
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.markdown-panel pre {
  overflow-x: auto;
  max-height: 520px;
  margin: 0;
  border-radius: 8px;
  background: #f6f7f9;
  color: #1d1f24;
  font: 14px/1.7 "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  padding: 16px;
  white-space: pre-wrap;
}

.explanation-panel ul {
  display: grid;
  gap: 12px;
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.explanation-panel li {
  display: grid;
  gap: 6px;
  border-bottom: 1px solid #edf0f4;
  padding-bottom: 12px;
}

.explanation-panel li:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.explanation-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.explanation-title span {
  border-radius: 999px;
  background: #fff4e5;
  color: #9a4c00;
  font-size: 12px;
  font-weight: 800;
  padding: 4px 8px;
}

.explanation-panel p,
.explanation-panel small {
  margin: 0;
  color: #4d5564;
  line-height: 1.6;
}

.explanation-panel small {
  color: #667085;
}

.muted-text,
.section-header p {
  color: #667085;
  margin: 0;
}

.error-message {
  margin: 0;
  color: #b42318;
  font-weight: 600;
}

.copy-message {
  margin: 0;
  color: #176b3a;
  font-weight: 700;
}

@media (max-width: 760px) {
  .page-header,
  .section-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
