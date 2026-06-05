<script setup lang="ts">
import type { ResumeVersionRead } from "../../api/resumeVersions";
import LoadingButton from "../common/LoadingButton.vue";

defineProps<{
  resumeVersion: ResumeVersionRead;
  isExportingMarkdown: boolean;
  copyMessage: string;
  exportMessage: string;
  exportErrorMessage: string;
}>();

const emit = defineEmits<{
  (event: "copy"): void;
  (event: "export"): void;
}>();

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
</script>

<template>
  <section class="result-section" aria-labelledby="resume-version-title">
    <div class="section-header">
      <div>
        <h2 id="resume-version-title">{{ resumeVersion.title }}</h2>
        <p class="muted-text">
          模型：{{ resumeVersion.model_name }} · {{ resumeVersion.version_type }} ·
          {{ formatDate(resumeVersion.created_at) }}
        </p>
      </div>
      <div class="action-row">
        <button class="secondary-button" type="button" @click="emit('copy')">复制 Markdown</button>
        <LoadingButton
          class="secondary-button"
          :loading="isExportingMarkdown"
          loading-text="正在导出 Markdown..."
          @click="emit('export')"
        >
          导出 Markdown
        </LoadingButton>
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
      <div v-if="resumeVersion.change_explanations.length > 0" class="explanation-grid">
        <article
          v-for="item in resumeVersion.change_explanations"
          :key="`${item.section}-${item.reason}`"
          class="explanation-card"
        >
          <div class="explanation-card-header">
            <strong>{{ item.section }}</strong>
            <span v-if="item.uncertain" class="explanation-tag">uncertain</span>
          </div>
          <p>{{ item.reason }}</p>
          <small>来源：{{ item.source }}</small>
        </article>
      </div>
      <p v-else class="muted-text">暂无修改说明。</p>
    </article>
  </section>
</template>
