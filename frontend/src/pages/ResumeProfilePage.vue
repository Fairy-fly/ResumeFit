<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import {
  createResumeProfile,
  listResumeProfiles,
  type ResumeProfileRead
} from "../api/resumeProfiles";

const title = ref("");
const rawMarkdown = ref("");
const resumes = ref<ResumeProfileRead[]>([]);
const isLoading = ref(false);
const isSaving = ref(false);
const errorMessage = ref("");

const canSave = computed(() => title.value.trim().length > 0 && rawMarkdown.value.trim().length > 0);

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function previewResume(content: string): string {
  const normalized = content.replace(/\s+/g, " ").trim();
  if (normalized.length <= 120) {
    return normalized;
  }

  return `${normalized.slice(0, 120)}...`;
}

async function loadResumes(): Promise<void> {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    resumes.value = await listResumeProfiles();
  } catch {
    errorMessage.value = "简历列表加载失败，请稍后重试。";
  } finally {
    isLoading.value = false;
  }
}

async function handleSubmit(): Promise<void> {
  if (!canSave.value || isSaving.value) {
    return;
  }

  isSaving.value = true;
  errorMessage.value = "";

  try {
    await createResumeProfile({
      title: title.value.trim(),
      raw_markdown: rawMarkdown.value
    });
    title.value = "";
    rawMarkdown.value = "";
    await loadResumes();
  } catch {
    errorMessage.value = "简历保存失败，请检查后端服务是否已启动。";
  } finally {
    isSaving.value = false;
  }
}

onMounted(() => {
  void loadResumes();
});
</script>

<template>
  <section class="resume-page">
    <div class="page-header">
      <h1 class="page-title">简历</h1>
    </div>

    <form class="resume-form" @submit.prevent="handleSubmit">
      <label class="field">
        <span>简历标题</span>
        <input v-model="title" type="text" placeholder="例如：后端开发通用简历" />
      </label>

      <label class="field">
        <span>简历正文</span>
        <textarea v-model="rawMarkdown" rows="14" placeholder="粘贴或输入你的通用简历正文" />
      </label>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <button class="primary-button" type="submit" :disabled="!canSave || isSaving">
        {{ isSaving ? "保存中..." : "保存简历" }}
      </button>
    </form>

    <section class="resume-list-section" aria-labelledby="resume-list-title">
      <div class="section-header">
        <h2 id="resume-list-title">已保存简历</h2>
        <button class="secondary-button" type="button" :disabled="isLoading" @click="loadResumes">
          {{ isLoading ? "加载中..." : "刷新" }}
        </button>
      </div>

      <p v-if="isLoading" class="muted-text">正在加载简历列表...</p>
      <p v-else-if="resumes.length === 0" class="muted-text">还没有保存的简历。</p>

      <div v-else class="resume-list">
        <article v-for="resume in resumes" :key="resume.id" class="resume-item">
          <div class="resume-item-header">
            <h3>{{ resume.title }}</h3>
            <time :datetime="resume.created_at">{{ formatDate(resume.created_at) }}</time>
          </div>
          <p>{{ previewResume(resume.raw_markdown) }}</p>
        </article>
      </div>
    </section>
  </section>
</template>

<style scoped>
.resume-page {
  display: grid;
  gap: 24px;
  max-width: 980px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.resume-form,
.resume-list-section {
  display: grid;
  gap: 18px;
}

.field {
  display: grid;
  gap: 8px;
  color: #343944;
  font-weight: 600;
}

.field input,
.field textarea {
  width: 100%;
  border: 1px solid #ccd1dc;
  border-radius: 8px;
  background: #ffffff;
  color: #1d1f24;
  font: inherit;
  font-weight: 400;
  line-height: 1.5;
  padding: 12px 14px;
}

.field textarea {
  min-height: 280px;
  resize: vertical;
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

.section-header,
.resume-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.section-header h2,
.resume-item h3,
.resume-item p {
  margin: 0;
}

.section-header h2 {
  font-size: 20px;
}

.resume-list {
  display: grid;
  gap: 12px;
}

.resume-item {
  display: grid;
  gap: 10px;
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.resume-item h3 {
  color: #1d1f24;
  font-size: 18px;
}

.resume-item time,
.muted-text {
  color: #667085;
}

.resume-item p {
  color: #4d5564;
  line-height: 1.6;
}

.error-message {
  margin: 0;
  color: #b42318;
  font-weight: 600;
}

@media (max-width: 760px) {
  .section-header,
  .resume-item-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
