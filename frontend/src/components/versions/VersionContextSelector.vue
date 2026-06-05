<script setup lang="ts">
import { ref } from "vue";

import type { MatchReportRead } from "../../api/analyses";
import type { JobDescriptionRead } from "../../api/jobDescriptions";
import type { ProjectRead } from "../../api/projects";
import type { ResumeProfileRead } from "../../api/resumeProfiles";
import CollapsibleSection from "../common/CollapsibleSection.vue";
import EmptyState from "../common/EmptyState.vue";
import LoadingButton from "../common/LoadingButton.vue";

const props = defineProps<{
  resumes: ResumeProfileRead[];
  projects: ProjectRead[];
  analyzedJobDescriptions: JobDescriptionRead[];
  matchReports: MatchReportRead[];
  selectedResumeId: number | null;
  selectedProjectIds: number[];
  selectedJobDescriptionId: number | null;
  selectedMatchReportId: number | null;
  selectedMatchReport: MatchReportRead | null;
  canGenerate: boolean;
  isLoading: boolean;
  isGenerating: boolean;
  errorMessage: string;
  matchReportSelectorOpen: boolean;
}>();

const emit = defineEmits<{
  (event: "apply-match-report", matchReport: MatchReportRead): void;
  (event: "select-resume", resumeId: number): void;
  (event: "toggle-project", projectId: number): void;
  (event: "select-job-description", jobDescriptionId: number): void;
  (event: "generate"): void;
  (event: "update:matchReportSelectorOpen", value: boolean): void;
}>();

const isGenerationContextOpen = ref(false);

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

function findResumeTitle(resumeProfileId: number): string {
  return props.resumes.find((resume) => resume.id === resumeProfileId)?.title ?? `简历 #${resumeProfileId}`;
}

function findJobTitle(jobDescriptionId: number | null): string {
  if (jobDescriptionId === null) {
    return "未关联 JD";
  }

  const jobDescription = props.analyzedJobDescriptions.find((job) => job.id === jobDescriptionId);
  if (!jobDescription) {
    return `JD #${jobDescriptionId}`;
  }

  return `${jobDescription.company_name ?? "未填写公司"} · ${jobDescription.job_title}`;
}

function findProjectNames(projectIds: number[]): string {
  const names = projectIds.map((projectId) => {
    return props.projects.find((project) => project.id === projectId)?.name ?? `项目 #${projectId}`;
  });
  return names.join("、");
}
</script>

<template>
  <form class="version-form" @submit.prevent="emit('generate')">
    <CollapsibleSection
      class="selector-section"
      title="选择匹配报告"
      :count="matchReports.length"
      :model-value="matchReportSelectorOpen"
      @update:model-value="emit('update:matchReportSelectorOpen', $event)"
    >
      <EmptyState
        v-if="!isLoading && matchReports.length === 0"
        title="还没有匹配报告"
        description="先完成简历、项目和岗位 JD 的匹配分析，才能生成定制简历。"
        action-text="去生成匹配报告"
        action-to="/analysis"
      />
      <label v-for="matchReport in matchReports" :key="matchReport.id" class="option-item">
        <input
          type="radio"
          name="match-report"
          :checked="selectedMatchReportId === matchReport.id"
          @change="emit('apply-match-report', matchReport)"
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
    </CollapsibleSection>

    <CollapsibleSection
      v-model="isGenerationContextOpen"
      class="selector-section"
      title="生成上下文 · 通用简历 / 项目经历 / 已分析 JD"
    >
      <section class="context-selector-group" aria-label="通用简历">
        <h3>通用简历</h3>
        <p v-if="resumes.length === 0" class="muted-text">还没有可用的通用简历。</p>
        <label v-for="resume in resumes" :key="resume.id" class="option-item">
          <input
            type="radio"
            name="resume"
            :value="resume.id"
            :checked="selectedResumeId === resume.id"
            @change="emit('select-resume', resume.id)"
          />
          <span>
            <strong>{{ resume.title }}</strong>
            <small>{{ previewText(resume.raw_markdown) }}</small>
          </span>
        </label>
      </section>

      <section class="context-selector-group" aria-label="项目经历">
        <h3>项目经历</h3>
        <p v-if="projects.length === 0" class="muted-text">还没有可用的项目经历。</p>
        <label v-for="project in projects" :key="project.id" class="option-item">
          <input
            type="checkbox"
            :checked="selectedProjectIds.includes(project.id)"
            @change="emit('toggle-project', project.id)"
          />
          <span>
            <strong>{{ project.name }}</strong>
            <small>{{ project.project_type }} · {{ project.role }}</small>
          </span>
        </label>
      </section>

      <section class="context-selector-group" aria-label="已分析 JD">
        <h3>已分析 JD</h3>
        <p v-if="analyzedJobDescriptions.length === 0" class="muted-text">还没有已分析的 JD，请先在 JD 页面完成分析。</p>
        <label v-for="jobDescription in analyzedJobDescriptions" :key="jobDescription.id" class="option-item">
          <input
            type="radio"
            name="job-description"
            :value="jobDescription.id"
            :checked="selectedJobDescriptionId === jobDescription.id"
            @change="emit('select-job-description', jobDescription.id)"
          />
          <span>
            <strong>{{ jobDescription.job_title }}</strong>
            <small>{{ jobDescription.company_name }} · {{ formatDate(jobDescription.updated_at) }}</small>
          </span>
        </label>
      </section>
    </CollapsibleSection>

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

    <LoadingButton
      class="primary-button"
      type="submit"
      :disabled="!canGenerate"
      :loading="isGenerating"
      loading-text="正在生成定制简历..."
    >
      生成定制简历
    </LoadingButton>
  </form>
</template>
