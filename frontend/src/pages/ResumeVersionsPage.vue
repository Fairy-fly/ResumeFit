<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { listMatchReports, type MatchReportRead } from "../api/analyses";
import {
  createInterviewQuestionResult,
  listInterviewQuestionResults,
  type InterviewQuestionResultRead,
  type QuestionDifficulty
} from "../api/interviewQuestions";
import { listJobDescriptions, type JobDescriptionRead } from "../api/jobDescriptions";
import { listProjects, type ProjectRead } from "../api/projects";
import { listResumeProfiles, type ResumeProfileRead } from "../api/resumeProfiles";
import {
  downloadResumeVersionMarkdown,
  generateResumeVersion,
  listResumeVersions,
  type ResumeVersionRead
} from "../api/resumeVersions";
import {
  createTruthCheckResult,
  listTruthCheckResults,
  type EvidenceStatus,
  type RiskLevel,
  type RiskType,
  type TruthCheckResultRead
} from "../api/truthChecks";

const resumes = ref<ResumeProfileRead[]>([]);
const projects = ref<ProjectRead[]>([]);
const jobDescriptions = ref<JobDescriptionRead[]>([]);
const matchReports = ref<MatchReportRead[]>([]);
const resumeVersions = ref<ResumeVersionRead[]>([]);
const selectedResumeId = ref<number | null>(null);
const selectedProjectIds = ref<number[]>([]);
const selectedJobDescriptionId = ref<number | null>(null);
const selectedMatchReportId = ref<number | null>(null);
const selectedResumeVersionId = ref<number | null>(null);
const resumeVersion = ref<ResumeVersionRead | null>(null);
const truthCheck = ref<TruthCheckResultRead | null>(null);
const truthChecks = ref<TruthCheckResultRead[]>([]);
const interviewQuestionResult = ref<InterviewQuestionResultRead | null>(null);
const interviewQuestionResults = ref<InterviewQuestionResultRead[]>([]);
const isLoading = ref(false);
const isLoadingVersions = ref(false);
const isLoadingTruthChecks = ref(false);
const isLoadingInterviewQuestions = ref(false);
const isGenerating = ref(false);
const isCheckingTruth = ref(false);
const isGeneratingInterviewQuestions = ref(false);
const isExportingMarkdown = ref(false);
const errorMessage = ref("");
const truthErrorMessage = ref("");
const interviewErrorMessage = ref("");
const copyMessage = ref("");
const exportMessage = ref("");
const exportErrorMessage = ref("");

const riskLevelLabels: Record<RiskLevel, string> = {
  low: "低风险",
  medium: "中风险",
  high: "高风险"
};

const riskTypeLabels: Record<RiskType, string> = {
  fabricated_experience: "疑似编造经历",
  exaggerated_skill: "技能掌握程度夸大",
  unsupported_metric: "缺少证据的量化成果",
  unsupported_claim: "缺少证据的能力描述",
  role_exaggeration: "个人角色夸大",
  project_scope_exaggeration: "项目规模夸大",
  uncertain_statement: "不确定内容确定化",
  interview_risk: "面试追问风险"
};

const evidenceStatusLabels: Record<EvidenceStatus, string> = {
  supported: "有证据",
  partially_supported: "部分支持",
  unsupported: "缺少证据",
  uncertain: "不确定"
};

const difficultyLabels: Record<QuestionDifficulty, string> = {
  easy: "基础",
  medium: "中等",
  hard: "较难"
};

const analyzedJobDescriptions = computed(() =>
  jobDescriptions.value.filter((jobDescription) => jobDescription.status === "analyzed")
);

const selectedMatchReport = computed(() =>
  matchReports.value.find((matchReport) => matchReport.id === selectedMatchReportId.value) ?? null
);

const selectedResumeVersion = computed(() =>
  resumeVersions.value.find((version) => version.id === selectedResumeVersionId.value) ?? null
);

const canGenerate = computed(
  () =>
    selectedResumeId.value !== null &&
    selectedProjectIds.value.length > 0 &&
    selectedJobDescriptionId.value !== null &&
    selectedMatchReportId.value !== null
);

const canCheckTruth = computed(() => selectedResumeVersionId.value !== null);

const canGenerateInterviewQuestions = computed(() => selectedResumeVersionId.value !== null);

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

  return "请求失败，请检查选择内容、AI 配置或后端服务状态。";
}

function findResumeTitle(resumeProfileId: number): string {
  return resumes.value.find((resume) => resume.id === resumeProfileId)?.title ?? `简历 #${resumeProfileId}`;
}

function findJobTitle(jobDescriptionId: number | null): string {
  if (jobDescriptionId === null) {
    return "未关联 JD";
  }

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
  exportMessage.value = "";
  exportErrorMessage.value = "";
}

async function loadTruthChecksForVersion(resumeVersionId: number): Promise<void> {
  isLoadingTruthChecks.value = true;
  truthErrorMessage.value = "";

  try {
    truthChecks.value = await listTruthCheckResults(resumeVersionId);
    truthCheck.value = truthChecks.value[0] ?? null;
  } catch (error) {
    truthChecks.value = [];
    truthCheck.value = null;
    truthErrorMessage.value = messageFromError(error);
  } finally {
    isLoadingTruthChecks.value = false;
  }
}

async function loadInterviewQuestionsForVersion(resumeVersionId: number): Promise<void> {
  isLoadingInterviewQuestions.value = true;
  interviewErrorMessage.value = "";

  try {
    interviewQuestionResults.value = await listInterviewQuestionResults(resumeVersionId);
    interviewQuestionResult.value = interviewQuestionResults.value[0] ?? null;
  } catch (error) {
    interviewQuestionResults.value = [];
    interviewQuestionResult.value = null;
    interviewErrorMessage.value = messageFromError(error);
  } finally {
    isLoadingInterviewQuestions.value = false;
  }
}

async function refreshResumeVersions(preferredResumeVersionId?: number): Promise<void> {
  isLoadingVersions.value = true;
  truthErrorMessage.value = "";
  interviewErrorMessage.value = "";

  try {
    resumeVersions.value = await listResumeVersions();
    const preferredId = preferredResumeVersionId ?? selectedResumeVersionId.value;
    const nextId =
      resumeVersions.value.find((version) => version.id === preferredId)?.id ?? resumeVersions.value[0]?.id ?? null;
    selectedResumeVersionId.value = nextId;

    if (nextId !== null) {
      await Promise.all([loadTruthChecksForVersion(nextId), loadInterviewQuestionsForVersion(nextId)]);
      return;
    }

    truthChecks.value = [];
    truthCheck.value = null;
    interviewQuestionResults.value = [];
    interviewQuestionResult.value = null;
  } catch (error) {
    truthErrorMessage.value = messageFromError(error);
  } finally {
    isLoadingVersions.value = false;
  }
}

async function loadOptions(): Promise<void> {
  isLoading.value = true;
  errorMessage.value = "";
  truthErrorMessage.value = "";
  interviewErrorMessage.value = "";
  copyMessage.value = "";
  exportMessage.value = "";
  exportErrorMessage.value = "";

  try {
    const [loadedResumes, loadedProjects, loadedJobDescriptions, loadedMatchReports, loadedResumeVersions] =
      await Promise.all([
        listResumeProfiles(),
        listProjects(),
        listJobDescriptions(),
        listMatchReports(),
        listResumeVersions()
      ]);
    resumes.value = loadedResumes;
    projects.value = loadedProjects;
    jobDescriptions.value = loadedJobDescriptions;
    matchReports.value = loadedMatchReports;
    resumeVersions.value = loadedResumeVersions;

    if (loadedMatchReports.length > 0) {
      applyMatchReport(loadedMatchReports[0]);
    } else {
      selectedResumeId.value = loadedResumes[0]?.id ?? null;
      selectedJobDescriptionId.value =
        loadedJobDescriptions.find((jobDescription) => jobDescription.status === "analyzed")?.id ?? null;
    }

    selectedResumeVersionId.value = loadedResumeVersions[0]?.id ?? null;
    if (selectedResumeVersionId.value !== null) {
      await Promise.all([
        loadTruthChecksForVersion(selectedResumeVersionId.value),
        loadInterviewQuestionsForVersion(selectedResumeVersionId.value)
      ]);
    }
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
  exportMessage.value = "";
  exportErrorMessage.value = "";
  resumeVersion.value = null;

  try {
    resumeVersion.value = await generateResumeVersion({
      resume_profile_id: selectedResumeId.value,
      project_ids: selectedProjectIds.value,
      job_description_id: selectedJobDescriptionId.value,
      match_report_id: selectedMatchReportId.value
    });
    await refreshResumeVersions(resumeVersion.value.id);
  } catch (error) {
    errorMessage.value = messageFromError(error);
  } finally {
    isGenerating.value = false;
  }
}

async function handleTruthCheck(): Promise<void> {
  if (!canCheckTruth.value || isCheckingTruth.value || selectedResumeVersionId.value === null) {
    return;
  }

  isCheckingTruth.value = true;
  truthErrorMessage.value = "";

  try {
    const created = await createTruthCheckResult({
      resume_version_id: selectedResumeVersionId.value
    });
    truthCheck.value = created;
    truthChecks.value = [created, ...truthChecks.value.filter((item) => item.id !== created.id)];
  } catch (error) {
    truthErrorMessage.value = messageFromError(error);
  } finally {
    isCheckingTruth.value = false;
  }
}

async function handleInterviewQuestions(): Promise<void> {
  if (
    !canGenerateInterviewQuestions.value ||
    isGeneratingInterviewQuestions.value ||
    selectedResumeVersionId.value === null
  ) {
    return;
  }

  isGeneratingInterviewQuestions.value = true;
  interviewErrorMessage.value = "";

  try {
    const created = await createInterviewQuestionResult({
      resume_version_id: selectedResumeVersionId.value
    });
    interviewQuestionResult.value = created;
    interviewQuestionResults.value = [
      created,
      ...interviewQuestionResults.value.filter((item) => item.id !== created.id)
    ];
  } catch (error) {
    interviewErrorMessage.value = messageFromError(error);
  } finally {
    isGeneratingInterviewQuestions.value = false;
  }
}

function handleSelectResumeVersion(resumeVersionId: number): void {
  selectedResumeVersionId.value = resumeVersionId;
  void Promise.all([loadTruthChecksForVersion(resumeVersionId), loadInterviewQuestionsForVersion(resumeVersionId)]);
}

function handleRefreshVersions(): void {
  void refreshResumeVersions();
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

async function exportMarkdown(): Promise<void> {
  if (!resumeVersion.value || isExportingMarkdown.value) {
    return;
  }

  isExportingMarkdown.value = true;
  exportMessage.value = "";
  exportErrorMessage.value = "";

  try {
    const { blob, filename } = await downloadResumeVersionMarkdown(resumeVersion.value.id);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    exportMessage.value = "Markdown 文件已开始下载。";
  } catch (error) {
    exportErrorMessage.value = messageFromError(error);
  } finally {
    isExportingMarkdown.value = false;
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
        <div class="action-row">
          <button class="secondary-button" type="button" @click="copyMarkdown">复制 Markdown</button>
          <button class="secondary-button" type="button" :disabled="isExportingMarkdown" @click="exportMarkdown">
            {{ isExportingMarkdown ? "导出中..." : "导出 Markdown" }}
          </button>
        </div>
      </div>

      <p v-if="copyMessage" class="copy-message">{{ copyMessage }}</p>
      <p v-if="exportMessage" class="copy-message">{{ exportMessage }}</p>
      <p v-if="exportErrorMessage" class="error-message">{{ exportErrorMessage }}</p>

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

    <section class="truth-section" aria-labelledby="truth-check-title">
      <div class="section-header">
        <div>
          <h2 id="truth-check-title">真实性风险检测</h2>
          <p class="muted-text">选择一个已生成版本，检查是否存在夸大、缺证据或不确定表达。</p>
        </div>
        <button class="secondary-button" type="button" :disabled="isLoadingVersions" @click="handleRefreshVersions">
          {{ isLoadingVersions ? "加载中..." : "刷新版本" }}
        </button>
      </div>

      <section class="selector-section" aria-labelledby="resume-version-selector-title">
        <h3 id="resume-version-selector-title">选择简历版本</h3>
        <p v-if="resumeVersions.length === 0" class="muted-text">还没有已生成的定制简历。</p>
        <label v-for="version in resumeVersions" :key="version.id" class="option-item">
          <input
            type="radio"
            name="resume-version"
            :checked="selectedResumeVersionId === version.id"
            @change="handleSelectResumeVersion(version.id)"
          />
          <span>
            <strong>{{ version.title }}</strong>
            <small>{{ version.version_type }} · {{ findJobTitle(version.job_description_id) }} · {{ formatDate(version.created_at) }}</small>
          </span>
        </label>
      </section>

      <div v-if="selectedResumeVersion" class="summary-section">
        <dl>
          <div>
            <dt>当前检测版本</dt>
            <dd>{{ selectedResumeVersion.title }}</dd>
          </div>
          <div>
            <dt>关联岗位</dt>
            <dd>{{ findJobTitle(selectedResumeVersion.job_description_id) }}</dd>
          </div>
          <div>
            <dt>历史检测</dt>
            <dd>{{ truthChecks.length }} 次</dd>
          </div>
        </dl>
      </div>

      <p v-if="isLoadingTruthChecks" class="muted-text">正在加载历史检测结果...</p>
      <p v-if="truthErrorMessage" class="error-message">{{ truthErrorMessage }}</p>

      <button class="primary-button" type="button" :disabled="!canCheckTruth || isCheckingTruth" @click="handleTruthCheck">
        {{ isCheckingTruth ? "检测中..." : "检测真实性风险" }}
      </button>

      <article v-if="truthCheck" class="truth-result-panel">
        <div class="truth-result-header">
          <div>
            <h3>检测结果</h3>
            <p class="muted-text">模型：{{ truthCheck.model_name }} · {{ formatDate(truthCheck.created_at) }}</p>
          </div>
          <span class="risk-badge" :class="`risk-${truthCheck.overall_risk_level}`">
            {{ riskLevelLabels[truthCheck.overall_risk_level] }}
          </span>
        </div>

        <p class="truth-summary">{{ truthCheck.summary }}</p>

        <section class="risk-list" aria-labelledby="risky-statements-title">
          <h4 id="risky-statements-title">风险表达</h4>
          <p v-if="truthCheck.risky_statements.length === 0" class="muted-text">暂无明显风险表达。</p>
          <article v-for="item in truthCheck.risky_statements" :key="`${item.statement}-${item.risk_type}`" class="risk-item">
            <div class="risk-item-header">
              <strong>{{ item.statement }}</strong>
              <div class="risk-tags">
                <span :class="`risk-${item.risk_level}`">{{ riskLevelLabels[item.risk_level] }}</span>
                <span>{{ riskTypeLabels[item.risk_type] }}</span>
                <span>{{ evidenceStatusLabels[item.evidence_status] }}</span>
              </div>
            </div>
            <p>{{ item.reason }}</p>
            <div class="rewrite-box">
              <strong>更稳妥改法</strong>
              <p>{{ item.safer_rewrite }}</p>
            </div>
          </article>
        </section>

        <div class="truth-grid">
          <section class="truth-card">
            <h4>整体改写建议</h4>
            <ul>
              <li v-for="item in truthCheck.safer_rewrites" :key="item">{{ item }}</li>
              <li v-if="truthCheck.safer_rewrites.length === 0">暂无额外建议。</li>
            </ul>
          </section>

          <section class="truth-card">
            <h4>缺失证据</h4>
            <ul>
              <li v-for="item in truthCheck.missing_evidence" :key="item">{{ item }}</li>
              <li v-if="truthCheck.missing_evidence.length === 0">暂无明显缺失证据。</li>
            </ul>
          </section>

          <section class="truth-card wide">
            <h4>面试追问风险点</h4>
            <ul>
              <li v-for="item in truthCheck.interview_risk_points" :key="item">{{ item }}</li>
              <li v-if="truthCheck.interview_risk_points.length === 0">暂无明显追问风险点。</li>
            </ul>
          </section>
        </div>
      </article>
    </section>

    <section class="interview-section" aria-labelledby="interview-question-title">
      <div class="section-header">
        <div>
          <h2 id="interview-question-title">面试追问预测</h2>
          <p class="muted-text">基于当前选择的简历版本、JD、项目和真实性风险，生成保守可解释的追问准备。</p>
        </div>
      </div>

      <div v-if="selectedResumeVersion" class="summary-section">
        <dl>
          <div>
            <dt>当前预测版本</dt>
            <dd>{{ selectedResumeVersion.title }}</dd>
          </div>
          <div>
            <dt>关联岗位</dt>
            <dd>{{ findJobTitle(selectedResumeVersion.job_description_id) }}</dd>
          </div>
          <div>
            <dt>历史预测</dt>
            <dd>{{ interviewQuestionResults.length }} 次</dd>
          </div>
        </dl>
      </div>
      <p v-else class="muted-text">请先在上方选择一个已生成的定制简历版本。</p>

      <p v-if="isLoadingInterviewQuestions" class="muted-text">正在加载历史追问预测...</p>
      <p v-if="interviewErrorMessage" class="error-message">{{ interviewErrorMessage }}</p>

      <button
        class="primary-button"
        type="button"
        :disabled="!canGenerateInterviewQuestions || isGeneratingInterviewQuestions"
        @click="handleInterviewQuestions"
      >
        {{ isGeneratingInterviewQuestions ? "生成中..." : "生成面试追问" }}
      </button>

      <article v-if="interviewQuestionResult" class="interview-result-panel">
        <div class="section-header">
          <div>
            <h3>追问预测结果</h3>
            <p class="muted-text">
              模型：{{ interviewQuestionResult.model_name }} · {{ formatDate(interviewQuestionResult.created_at) }}
            </p>
          </div>
        </div>

        <p class="truth-summary">{{ interviewQuestionResult.summary }}</p>

        <section class="question-list" aria-labelledby="interview-questions-list-title">
          <h4 id="interview-questions-list-title">可能追问</h4>
          <p v-if="interviewQuestionResult.questions.length === 0" class="muted-text">暂无追问预测。</p>
          <article
            v-for="item in interviewQuestionResult.questions"
            :key="`${item.question}-${item.related_resume_section}`"
            class="question-item"
          >
            <div class="question-item-header">
              <strong>{{ item.question }}</strong>
              <span class="difficulty-badge">{{ difficultyLabels[item.difficulty] }}</span>
            </div>

            <div class="question-grid">
              <section class="question-card">
                <h5>为什么会问</h5>
                <p>{{ item.reason }}</p>
              </section>
              <section class="question-card">
                <h5>关联简历内容</h5>
                <p>{{ item.related_resume_section }}</p>
              </section>
              <section class="question-card wide">
                <h5>建议回答</h5>
                <p>{{ item.suggested_answer }}</p>
              </section>
              <section class="question-card">
                <h5>回答策略</h5>
                <p>{{ item.answer_strategy }}</p>
              </section>
              <section class="question-card">
                <h5>风险提醒</h5>
                <p>{{ item.risk_reminder }}</p>
              </section>
            </div>
          </article>
        </section>
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
.section-header,
.truth-result-header,
.risk-item-header,
.question-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.version-form,
.selector-section,
.summary-section,
.result-section,
.truth-section,
.truth-result-panel,
.interview-section,
.interview-result-panel,
.risk-list,
.question-list,
.question-item {
  display: grid;
  gap: 16px;
}

.selector-section h2,
.summary-section h2,
.markdown-panel h3,
.explanation-panel h3,
.truth-section h2,
.truth-section h3,
.truth-section h4,
.truth-card h4,
.interview-section h2,
.interview-section h3,
.interview-section h4,
.question-card h5 {
  margin: 0;
}

.selector-section h2,
.summary-section h2,
.truth-section h2,
.interview-section h2 {
  font-size: 20px;
}

.selector-section h3,
.truth-result-panel h3,
.interview-result-panel h3 {
  font-size: 18px;
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

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.summary-section,
.truth-section,
.interview-section,
.truth-result-panel,
.interview-result-panel,
.markdown-panel,
.explanation-panel {
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

.explanation-panel ul,
.truth-card ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 20px;
}

.explanation-panel li {
  display: grid;
  gap: 6px;
}

.explanation-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.explanation-title span,
.risk-tags span,
.risk-badge,
.difficulty-badge {
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  padding: 4px 8px;
}

.explanation-title span {
  background: #fff4e5;
  color: #9a4c00;
}

.truth-result-header h3,
.truth-result-header p,
.truth-summary,
.risk-item p,
.rewrite-box p,
.question-card p,
.explanation-panel p,
.explanation-panel small {
  margin: 0;
}

.truth-summary,
.risk-item p,
.rewrite-box p,
.truth-card li,
.question-card p,
.explanation-panel p,
.explanation-panel small {
  color: #4d5564;
  line-height: 1.6;
}

.risk-badge {
  display: inline-flex;
  white-space: nowrap;
}

.risk-low {
  background: #e9f8ef;
  color: #176b3a;
}

.risk-medium {
  background: #fff4e5;
  color: #9a4c00;
}

.risk-high {
  background: #ffeceb;
  color: #b42318;
}

.risk-item {
  display: grid;
  gap: 12px;
  border: 1px solid #edf0f4;
  border-radius: 8px;
  padding: 14px;
}

.question-item {
  border: 1px solid #edf0f4;
  border-radius: 8px;
  padding: 14px;
}

.question-item-header strong {
  color: #1d1f24;
}

.difficulty-badge {
  background: #eef2ff;
  color: #243b99;
  white-space: nowrap;
}

.risk-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}

.risk-tags span:not(.risk-low):not(.risk-medium):not(.risk-high) {
  background: #eef2ff;
  color: #243b99;
}

.rewrite-box {
  display: grid;
  gap: 6px;
  border-radius: 8px;
  background: #f6f7f9;
  padding: 12px;
}

.truth-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.truth-card {
  display: grid;
  gap: 12px;
  border: 1px solid #edf0f4;
  border-radius: 8px;
  padding: 14px;
}

.question-card {
  display: grid;
  gap: 8px;
  border: 1px solid #edf0f4;
  border-radius: 8px;
  padding: 12px;
}

.question-card.wide {
  grid-column: 1 / -1;
}

.truth-card.wide {
  grid-column: 1 / -1;
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
  .section-header,
  .truth-result-header,
  .risk-item-header,
  .question-item-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .risk-tags {
    justify-content: flex-start;
  }

  .action-row {
    justify-content: flex-start;
  }

  .truth-grid {
    grid-template-columns: 1fr;
  }

  .question-grid {
    grid-template-columns: 1fr;
  }
}
</style>
