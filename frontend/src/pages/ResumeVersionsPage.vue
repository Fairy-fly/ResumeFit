<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { listMatchReports, type MatchReportRead } from "../api/analyses";
import {
  createInterviewQuestionResult,
  listInterviewQuestionResults,
  type InterviewQuestionResultRead
} from "../api/interviewQuestions";
import { listJobDescriptions, type JobDescriptionRead } from "../api/jobDescriptions";
import { listProjects, type ProjectRead } from "../api/projects";
import { listResumeProfiles, type ResumeProfileRead } from "../api/resumeProfiles";
import {
  downloadResumeVersionDocx,
  downloadResumeVersionMarkdown,
  generateResumeVersion,
  listResumeVersions,
  type ResumeVersionDocxTemplate,
  type ResumeVersionRead
} from "../api/resumeVersions";
import {
  createTruthCheckResult,
  listTruthCheckResults,
  type TruthCheckResultRead
} from "../api/truthChecks";
import InterviewQuestionPanel from "../components/versions/InterviewQuestionPanel.vue";
import ResumeVersionPreview from "../components/versions/ResumeVersionPreview.vue";
import TruthCheckPanel from "../components/versions/TruthCheckPanel.vue";
import VersionContextSelector from "../components/versions/VersionContextSelector.vue";
import VersionHistorySelector from "../components/versions/VersionHistorySelector.vue";
import { getFriendlyErrorMessage } from "../utils/errors";

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
const isExportingDocx = ref(false);
const selectedDocxTemplate = ref<ResumeVersionDocxTemplate>("standard");
const errorMessage = ref("");
const truthErrorMessage = ref("");
const interviewErrorMessage = ref("");
const copyMessage = ref("");
const exportMessage = ref("");
const exportErrorMessage = ref("");
const isMatchReportSelectorOpen = ref(true);
const isVersionHistoryOpen = ref(false);
const isTruthCheckPanelOpen = ref(false);
const isInterviewQuestionPanelOpen = ref(false);
let truthCheckLoadRequestId = 0;
let interviewQuestionLoadRequestId = 0;

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

const canCheckTruth = computed(() => selectedResumeVersion.value !== null);

const canGenerateInterviewQuestions = computed(() => selectedResumeVersion.value !== null);

function sortByCreatedAtDesc<T extends { created_at: string }>(items: T[]): T[] {
  return [...items].sort(
    (first, second) => new Date(second.created_at).getTime() - new Date(first.created_at).getTime()
  );
}

function clearTruthCheckState(): void {
  truthCheckLoadRequestId += 1;
  truthChecks.value = [];
  truthCheck.value = null;
  isLoadingTruthChecks.value = false;
  isTruthCheckPanelOpen.value = false;
}

function clearInterviewQuestionState(): void {
  interviewQuestionLoadRequestId += 1;
  interviewQuestionResults.value = [];
  interviewQuestionResult.value = null;
  isLoadingInterviewQuestions.value = false;
  isInterviewQuestionPanelOpen.value = false;
}

function applyMatchReport(matchReport: MatchReportRead): void {
  selectedMatchReportId.value = matchReport.id;
  selectedResumeId.value = matchReport.resume_profile_id;
  selectedProjectIds.value = [...matchReport.project_ids];
  selectedJobDescriptionId.value = matchReport.job_description_id;
  copyMessage.value = "";
  exportMessage.value = "";
  exportErrorMessage.value = "";
}

function upsertResumeVersion(version: ResumeVersionRead): void {
  resumeVersions.value = sortByCreatedAtDesc([
    version,
    ...resumeVersions.value.filter((existingVersion) => existingVersion.id !== version.id)
  ]);
  selectedResumeVersionId.value = version.id;
}

async function loadTruthChecksForVersion(
  resumeVersionId: number,
  options: { clearBeforeLoad?: boolean } = {}
): Promise<void> {
  const requestId = ++truthCheckLoadRequestId;
  const shouldClearBeforeLoad = options.clearBeforeLoad ?? true;
  isLoadingTruthChecks.value = true;
  truthErrorMessage.value = "";
  if (shouldClearBeforeLoad) {
    truthChecks.value = [];
    truthCheck.value = null;
  }

  try {
    const loadedTruthChecks = sortByCreatedAtDesc(await listTruthCheckResults(resumeVersionId));
    if (requestId !== truthCheckLoadRequestId || selectedResumeVersionId.value !== resumeVersionId) {
      return;
    }
    truthChecks.value = loadedTruthChecks;
    truthCheck.value = loadedTruthChecks[0] ?? null;
    isTruthCheckPanelOpen.value = loadedTruthChecks.length > 0;
  } catch (error) {
    if (requestId !== truthCheckLoadRequestId || selectedResumeVersionId.value !== resumeVersionId) {
      return;
    }
    if (shouldClearBeforeLoad) {
      truthChecks.value = [];
      truthCheck.value = null;
      isTruthCheckPanelOpen.value = false;
    }
    truthErrorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    if (requestId === truthCheckLoadRequestId && selectedResumeVersionId.value === resumeVersionId) {
      isLoadingTruthChecks.value = false;
    }
  }
}

async function loadInterviewQuestionsForVersion(
  resumeVersionId: number,
  options: { clearBeforeLoad?: boolean } = {}
): Promise<void> {
  const requestId = ++interviewQuestionLoadRequestId;
  const shouldClearBeforeLoad = options.clearBeforeLoad ?? true;
  isLoadingInterviewQuestions.value = true;
  interviewErrorMessage.value = "";
  if (shouldClearBeforeLoad) {
    interviewQuestionResults.value = [];
    interviewQuestionResult.value = null;
  }

  try {
    const loadedInterviewQuestionResults = sortByCreatedAtDesc(await listInterviewQuestionResults(resumeVersionId));
    if (requestId !== interviewQuestionLoadRequestId || selectedResumeVersionId.value !== resumeVersionId) {
      return;
    }
    interviewQuestionResults.value = loadedInterviewQuestionResults;
    interviewQuestionResult.value = loadedInterviewQuestionResults[0] ?? null;
    isInterviewQuestionPanelOpen.value = loadedInterviewQuestionResults.length > 0;
  } catch (error) {
    if (requestId !== interviewQuestionLoadRequestId || selectedResumeVersionId.value !== resumeVersionId) {
      return;
    }
    if (shouldClearBeforeLoad) {
      interviewQuestionResults.value = [];
      interviewQuestionResult.value = null;
      isInterviewQuestionPanelOpen.value = false;
    }
    interviewErrorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    if (requestId === interviewQuestionLoadRequestId && selectedResumeVersionId.value === resumeVersionId) {
      isLoadingInterviewQuestions.value = false;
    }
  }
}

async function refreshResumeVersions(preferredResumeVersionId?: number): Promise<void> {
  isLoadingVersions.value = true;
  truthErrorMessage.value = "";
  interviewErrorMessage.value = "";

  try {
    resumeVersions.value = sortByCreatedAtDesc(await listResumeVersions());
    const preferredId = preferredResumeVersionId ?? selectedResumeVersionId.value;
    const nextId =
      resumeVersions.value.find((version) => version.id === preferredId)?.id ?? resumeVersions.value[0]?.id ?? null;
    selectedResumeVersionId.value = nextId;

    if (nextId !== null) {
      await Promise.all([loadTruthChecksForVersion(nextId), loadInterviewQuestionsForVersion(nextId)]);
      return;
    }

    isVersionHistoryOpen.value = false;
    isMatchReportSelectorOpen.value = true;
    clearTruthCheckState();
    clearInterviewQuestionState();
  } catch (error) {
    truthErrorMessage.value = getFriendlyErrorMessage(error);
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
    resumeVersions.value = sortByCreatedAtDesc(loadedResumeVersions);
    isMatchReportSelectorOpen.value = resumeVersions.value.length === 0;
    isVersionHistoryOpen.value = resumeVersions.value.length > 0;

    if (loadedMatchReports.length > 0) {
      applyMatchReport(loadedMatchReports[0]);
    } else {
      selectedResumeId.value = loadedResumes[0]?.id ?? null;
      selectedJobDescriptionId.value =
        loadedJobDescriptions.find((jobDescription) => jobDescription.status === "analyzed")?.id ?? null;
    }

    selectedResumeVersionId.value = resumeVersions.value[0]?.id ?? null;
    if (selectedResumeVersionId.value !== null) {
      await Promise.all([
        loadTruthChecksForVersion(selectedResumeVersionId.value),
        loadInterviewQuestionsForVersion(selectedResumeVersionId.value)
      ]);
    } else {
      clearTruthCheckState();
      clearInterviewQuestionState();
    }
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
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

  try {
    const createdResumeVersion = await generateResumeVersion({
      resume_profile_id: selectedResumeId.value,
      project_ids: selectedProjectIds.value,
      job_description_id: selectedJobDescriptionId.value,
      match_report_id: selectedMatchReportId.value
    });
    upsertResumeVersion(createdResumeVersion);
    await refreshResumeVersions(createdResumeVersion.id);
    isVersionHistoryOpen.value = true;
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
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
  const resumeVersionId = selectedResumeVersionId.value;

  try {
    const created = await createTruthCheckResult({
      resume_version_id: resumeVersionId
    });
    if (selectedResumeVersionId.value === resumeVersionId) {
      truthChecks.value = sortByCreatedAtDesc([
        created,
        ...truthChecks.value.filter((item) => item.id !== created.id)
      ]);
      truthCheck.value = truthChecks.value[0] ?? null;
      isTruthCheckPanelOpen.value = true;
      await loadTruthChecksForVersion(resumeVersionId, { clearBeforeLoad: false });
    }
  } catch (error) {
    if (selectedResumeVersionId.value === resumeVersionId) {
      truthErrorMessage.value = getFriendlyErrorMessage(error);
    }
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
  const resumeVersionId = selectedResumeVersionId.value;

  try {
    const created = await createInterviewQuestionResult({
      resume_version_id: resumeVersionId
    });
    if (selectedResumeVersionId.value === resumeVersionId) {
      interviewQuestionResults.value = sortByCreatedAtDesc([
        created,
        ...interviewQuestionResults.value.filter((item) => item.id !== created.id)
      ]);
      interviewQuestionResult.value = interviewQuestionResults.value[0] ?? null;
      isInterviewQuestionPanelOpen.value = true;
      await loadInterviewQuestionsForVersion(resumeVersionId, { clearBeforeLoad: false });
    }
  } catch (error) {
    if (selectedResumeVersionId.value === resumeVersionId) {
      interviewErrorMessage.value = getFriendlyErrorMessage(error);
    }
  } finally {
    isGeneratingInterviewQuestions.value = false;
  }
}

function handleSelectResumeVersion(version: ResumeVersionRead): void {
  selectedResumeVersionId.value = version.id;
  copyMessage.value = "";
  exportMessage.value = "";
  exportErrorMessage.value = "";
  clearTruthCheckState();
  clearInterviewQuestionState();
  void Promise.all([loadTruthChecksForVersion(version.id), loadInterviewQuestionsForVersion(version.id)]);
}

function handleRefreshVersions(): void {
  void refreshResumeVersions();
}

function handleStartGenerationFromHistory(): void {
  isMatchReportSelectorOpen.value = true;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function copyMarkdown(): Promise<void> {
  if (!selectedResumeVersion.value) {
    return;
  }

  copyMessage.value = "";

  try {
    await navigator.clipboard.writeText(selectedResumeVersion.value.content_markdown);
    copyMessage.value = "Markdown 已复制。";
  } catch {
    copyMessage.value = "复制失败，请手动选择 Markdown 内容复制。";
  }
}

async function exportMarkdown(): Promise<void> {
  if (!selectedResumeVersion.value || isExportingMarkdown.value) {
    return;
  }

  isExportingMarkdown.value = true;
  exportMessage.value = "";
  exportErrorMessage.value = "";

  try {
    const { blob, filename } = await downloadResumeVersionMarkdown(selectedResumeVersion.value.id);
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
    exportErrorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    isExportingMarkdown.value = false;
  }
}

async function exportDocx(): Promise<void> {
  if (!selectedResumeVersion.value || isExportingDocx.value) {
    return;
  }

  isExportingDocx.value = true;
  exportMessage.value = "";
  exportErrorMessage.value = "";

  try {
    const { blob, filename } = await downloadResumeVersionDocx(
      selectedResumeVersion.value.id,
      selectedDocxTemplate.value
    );
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    exportMessage.value = "DOCX 文件已开始下载。";
  } catch (error) {
    exportErrorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    isExportingDocx.value = false;
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

    <VersionContextSelector
      :resumes="resumes"
      :projects="projects"
      :analyzed-job-descriptions="analyzedJobDescriptions"
      :match-reports="matchReports"
      :selected-resume-id="selectedResumeId"
      :selected-project-ids="selectedProjectIds"
      :selected-job-description-id="selectedJobDescriptionId"
      :selected-match-report-id="selectedMatchReportId"
      :selected-match-report="selectedMatchReport"
      :can-generate="canGenerate"
      :is-loading="isLoading"
      :is-generating="isGenerating"
      :error-message="errorMessage"
      v-model:match-report-selector-open="isMatchReportSelectorOpen"
      @apply-match-report="applyMatchReport"
      @select-resume="selectedResumeId = $event"
      @toggle-project="toggleProject"
      @select-job-description="selectedJobDescriptionId = $event"
      @generate="handleGenerate"
    />

    <ResumeVersionPreview
      v-if="selectedResumeVersion"
      :key="selectedResumeVersion.id"
      :resume-version="selectedResumeVersion"
      :is-exporting-markdown="isExportingMarkdown"
      :is-exporting-docx="isExportingDocx"
      :selected-docx-template="selectedDocxTemplate"
      :copy-message="copyMessage"
      :export-message="exportMessage"
      :export-error-message="exportErrorMessage"
      @update:docx-template="selectedDocxTemplate = $event"
      @copy="copyMarkdown"
      @export="exportMarkdown"
      @export-docx="exportDocx"
    />

    <VersionHistorySelector
      :resume-versions="resumeVersions"
      :job-descriptions="jobDescriptions"
      :selected-resume-version-id="selectedResumeVersionId"
      :selected-resume-version="selectedResumeVersion"
      :is-loading="isLoading || isLoadingVersions"
      :is-loading-versions="isLoadingVersions"
      :truth-checks-count="truthChecks.length"
      :interview-question-results-count="interviewQuestionResults.length"
      v-model:is-open="isVersionHistoryOpen"
      @refresh="handleRefreshVersions"
      @select="handleSelectResumeVersion"
      @start-generation="handleStartGenerationFromHistory"
    />

    <TruthCheckPanel
      :selected-resume-version="selectedResumeVersion"
      :truth-check="truthCheck"
      :truth-checks="truthChecks"
      :is-loading-truth-checks="isLoadingTruthChecks"
      :is-checking-truth="isCheckingTruth"
      :truth-error-message="truthErrorMessage"
      :can-check-truth="canCheckTruth"
      v-model:is-open="isTruthCheckPanelOpen"
      @check="handleTruthCheck"
    />

    <InterviewQuestionPanel
      :selected-resume-version="selectedResumeVersion"
      :interview-question-result="interviewQuestionResult"
      :interview-question-results="interviewQuestionResults"
      :is-loading-interview-questions="isLoadingInterviewQuestions"
      :is-generating-interview-questions="isGeneratingInterviewQuestions"
      :interview-error-message="interviewErrorMessage"
      :can-generate-interview-questions="canGenerateInterviewQuestions"
      v-model:is-open="isInterviewQuestionPanelOpen"
      @generate="handleInterviewQuestions"
    />
  </section>
</template>

<style>
.versions-page {
  display: grid;
  gap: 24px;
  max-width: 1100px;
}

.versions-page .page-header,
.versions-page .section-header,
.versions-page .truth-result-header,
.versions-page .risk-item-header,
.versions-page .question-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.versions-page .version-form,
.versions-page .selector-section,
.versions-page .summary-section,
.versions-page .result-section,
.versions-page .truth-section,
.versions-page .truth-result-panel,
.versions-page .interview-section,
.versions-page .interview-result-panel,
.versions-page .risk-list,
.versions-page .question-list,
.versions-page .question-item {
  display: grid;
  gap: 16px;
}

.versions-page .selector-section h2,
.versions-page .summary-section h2,
.versions-page .markdown-panel h3,
.versions-page .explanation-panel h3,
.versions-page .truth-section h2,
.versions-page .truth-section h3,
.versions-page .truth-section h4,
.versions-page .truth-card h4,
.versions-page .interview-section h2,
.versions-page .interview-section h3,
.versions-page .interview-section h4,
.versions-page .question-card h5 {
  margin: 0;
}

.versions-page .selector-section h2,
.versions-page .summary-section h2,
.versions-page .truth-section h2,
.versions-page .interview-section h2 {
  font-size: 20px;
}

.versions-page .selector-section h3,
.versions-page .truth-result-panel h3,
.versions-page .interview-result-panel h3 {
  font-size: 18px;
}

.versions-page .context-selector-group {
  display: grid;
  gap: 12px;
}

.versions-page .context-selector-group h3 {
  margin: 0;
  color: #1d1f24;
  font-size: 18px;
}

.versions-page .option-item {
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

.versions-page .option-item input {
  margin-top: 4px;
}

.versions-page .option-item span {
  display: grid;
  gap: 5px;
}

.versions-page .option-item small {
  color: #667085;
  line-height: 1.5;
}

.versions-page .version-history-item {
  transition:
    background 0.15s ease,
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.versions-page .version-history-item.is-selected {
  border-color: #243b99;
  background: #f5f7ff;
  box-shadow: inset 4px 0 0 #243b99;
}

.versions-page .version-history-content {
  display: grid;
  flex: 1;
  gap: 5px;
  min-width: 0;
}

.versions-page .version-history-title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.versions-page .selected-badge {
  display: inline-flex;
  border-radius: 999px;
  background: #243b99;
  color: #ffffff;
  font-size: 12px;
  font-weight: 800;
  line-height: 1;
  padding: 5px 8px;
}

.versions-page .action-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.versions-page .docx-template-select {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #667085;
  font-size: 13px;
  font-weight: 700;
}

.versions-page .docx-template-select select {
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  background: #ffffff;
  color: #343944;
  font: inherit;
  min-height: 38px;
  padding: 0 10px;
}

.versions-page .docx-template-select select:disabled {
  background: #f2f4f7;
  color: #98a2b3;
  cursor: not-allowed;
}

.versions-page .summary-section,
.versions-page .truth-section,
.versions-page .interview-section,
.versions-page .truth-result-panel,
.versions-page .interview-result-panel,
.versions-page .markdown-panel,
.versions-page .explanation-panel {
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.versions-page .summary-section dl {
  display: grid;
  gap: 10px;
  margin: 0;
}

.versions-page .summary-section dl div {
  display: grid;
  gap: 4px;
}

.versions-page .summary-section dt {
  color: #667085;
  font-size: 13px;
  font-weight: 700;
}

.versions-page .summary-section dd {
  margin: 0;
  color: #343944;
  line-height: 1.5;
}

.versions-page .primary-button,
.versions-page .secondary-button {
  width: fit-content;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

.versions-page .primary-button {
  background: #243b99;
  color: #ffffff;
  padding: 12px 18px;
}

.versions-page .secondary-button {
  background: #e6e9f2;
  color: #263044;
  padding: 9px 14px;
}

.versions-page .primary-button:disabled,
.versions-page .secondary-button:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.versions-page .markdown-panel pre {
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

.versions-page .explanation-panel ul,
.versions-page .truth-card ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 20px;
}

.versions-page .explanation-panel li {
  display: grid;
  gap: 6px;
}

.versions-page .explanation-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.versions-page .explanation-card {
  display: grid;
  gap: 10px;
  border: 1px solid #edf0f4;
  border-radius: 8px;
  background: #fbfcff;
  padding: 14px;
}

.versions-page .explanation-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.versions-page .explanation-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.versions-page .explanation-title span,
.versions-page .risk-tags span,
.versions-page .risk-badge,
.versions-page .difficulty-badge {
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  padding: 4px 8px;
}

.versions-page .explanation-title span {
  background: #fff4e5;
  color: #9a4c00;
}

.versions-page .explanation-tag {
  border-radius: 999px;
  background: #fff4e5;
  color: #9a4c00;
  font-size: 12px;
  font-weight: 800;
  padding: 4px 8px;
}

.versions-page .truth-result-header h3,
.versions-page .truth-result-header p,
.versions-page .truth-summary,
.versions-page .risk-item p,
.versions-page .rewrite-box p,
.versions-page .question-card p,
.versions-page .explanation-panel p,
.versions-page .explanation-panel small {
  margin: 0;
}

.versions-page .truth-summary,
.versions-page .risk-item p,
.versions-page .rewrite-box p,
.versions-page .truth-card li,
.versions-page .question-card p,
.versions-page .explanation-panel p,
.versions-page .explanation-panel small {
  color: #4d5564;
  line-height: 1.6;
}

.versions-page .risk-badge {
  display: inline-flex;
  white-space: nowrap;
}

.versions-page .risk-low {
  background: #e9f8ef;
  color: #176b3a;
}

.versions-page .risk-medium {
  background: #fff4e5;
  color: #9a4c00;
}

.versions-page .risk-high {
  background: #ffeceb;
  color: #b42318;
}

.versions-page .risk-item {
  display: grid;
  gap: 12px;
  border: 1px solid #edf0f4;
  border-radius: 8px;
  padding: 14px;
}

.versions-page .question-item {
  border: 1px solid #edf0f4;
  border-radius: 8px;
  padding: 14px;
}

.versions-page .question-item-header strong {
  color: #1d1f24;
}

.versions-page .difficulty-badge {
  background: #eef2ff;
  color: #243b99;
  white-space: nowrap;
}

.versions-page .risk-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}

.versions-page .risk-tags span:not(.risk-low):not(.risk-medium):not(.risk-high) {
  background: #eef2ff;
  color: #243b99;
}

.versions-page .rewrite-box {
  display: grid;
  gap: 6px;
  border-radius: 8px;
  background: #f6f7f9;
  padding: 12px;
}

.versions-page .truth-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.versions-page .question-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.versions-page .truth-card {
  display: grid;
  gap: 12px;
  border: 1px solid #edf0f4;
  border-radius: 8px;
  padding: 14px;
}

.versions-page .question-card {
  display: grid;
  gap: 8px;
  border: 1px solid #edf0f4;
  border-radius: 8px;
  padding: 12px;
}

.versions-page .question-card.wide {
  grid-column: 1 / -1;
}

.versions-page .truth-card.wide {
  grid-column: 1 / -1;
}

.versions-page .muted-text,
.versions-page .section-header p {
  color: #667085;
  margin: 0;
}

.versions-page .error-message {
  margin: 0;
  color: #b42318;
  font-weight: 600;
}

.versions-page .copy-message {
  margin: 0;
  color: #176b3a;
  font-weight: 700;
}

@media (max-width: 760px) {
  .versions-page .page-header,
  .versions-page .section-header,
  .versions-page .truth-result-header,
  .versions-page .risk-item-header,
  .versions-page .question-item-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .versions-page .risk-tags {
    justify-content: flex-start;
  }

  .versions-page .action-row {
    justify-content: flex-start;
  }

  .versions-page .truth-grid {
    grid-template-columns: 1fr;
  }

  .versions-page .question-grid {
    grid-template-columns: 1fr;
  }

  .versions-page .explanation-grid {
    grid-template-columns: 1fr;
  }
}
</style>
