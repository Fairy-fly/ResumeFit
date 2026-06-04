<script setup lang="ts">
import type { JobDescriptionRead } from "../../api/jobDescriptions";
import type { ResumeVersionRead } from "../../api/resumeVersions";

const props = defineProps<{
  resumeVersions: ResumeVersionRead[];
  jobDescriptions: JobDescriptionRead[];
  selectedResumeVersionId: number | null;
  selectedResumeVersion: ResumeVersionRead | null;
  isLoadingVersions: boolean;
  truthChecksCount: number;
  interviewQuestionResultsCount: number;
}>();

const emit = defineEmits<{
  (event: "refresh"): void;
  (event: "select", resumeVersion: ResumeVersionRead): void;
}>();

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function findJobTitle(jobDescriptionId: number | null): string {
  if (jobDescriptionId === null) {
    return "未关联 JD";
  }

  const jobDescription = props.jobDescriptions.find((job) => job.id === jobDescriptionId);
  if (!jobDescription) {
    return `JD #${jobDescriptionId}`;
  }

  return `${jobDescription.company_name ?? "未填写公司"} · ${jobDescription.job_title}`;
}
</script>

<template>
  <section class="truth-section" aria-labelledby="resume-version-selector-title">
    <div class="section-header">
      <div>
        <h2 id="resume-version-selector-title">历史版本选择</h2>
        <p class="muted-text">选择一个已生成版本，用于真实性风险检测和面试追问预测。</p>
      </div>
      <button class="secondary-button" type="button" :disabled="isLoadingVersions" @click="emit('refresh')">
        {{ isLoadingVersions ? "加载中..." : "刷新版本" }}
      </button>
    </div>

    <section class="selector-section" aria-label="选择简历版本">
      <p v-if="resumeVersions.length === 0" class="muted-text">还没有已生成的定制简历。</p>
      <label v-for="version in resumeVersions" :key="version.id" class="option-item">
        <input
          type="radio"
          name="resume-version"
          :checked="selectedResumeVersionId === version.id"
          @change="emit('select', version)"
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
          <dt>当前版本</dt>
          <dd>{{ selectedResumeVersion.title }}</dd>
        </div>
        <div>
          <dt>关联岗位</dt>
          <dd>{{ findJobTitle(selectedResumeVersion.job_description_id) }}</dd>
        </div>
        <div>
          <dt>历史检测</dt>
          <dd>{{ truthChecksCount }} 次</dd>
        </div>
        <div>
          <dt>历史预测</dt>
          <dd>{{ interviewQuestionResultsCount }} 次</dd>
        </div>
      </dl>
    </div>
  </section>
</template>
