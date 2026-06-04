<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { createProject, listProjects, type ProjectRead } from "../api/projects";
import DetailModal from "../components/common/DetailModal.vue";

const name = ref("");
const projectType = ref("");
const role = ref("");
const techStackInput = ref("");
const description = ref("");
const userContribution = ref("");
const workUrl = ref("");
const projects = ref<ProjectRead[]>([]);
const selectedProjectDetail = ref<ProjectRead | null>(null);
const isLoading = ref(false);
const isSaving = ref(false);
const errorMessage = ref("");

const parsedTechStack = computed(() =>
  techStackInput.value
    .split(/[,\n]/)
    .map((item) => item.trim())
    .filter(Boolean)
);

const canSave = computed(
  () =>
    name.value.trim().length > 0 &&
    projectType.value.trim().length > 0 &&
    role.value.trim().length > 0 &&
    parsedTechStack.value.length > 0 &&
    description.value.trim().length > 0 &&
    userContribution.value.trim().length > 0
);

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function previewText(value: string): string {
  const normalized = value.replace(/\s+/g, " ").trim();
  if (normalized.length <= 120) {
    return normalized;
  }

  return `${normalized.slice(0, 120)}...`;
}

async function loadProjects(): Promise<void> {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    projects.value = await listProjects();
  } catch {
    errorMessage.value = "项目列表加载失败，请稍后重试。";
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
    await createProject({
      name: name.value.trim(),
      project_type: projectType.value.trim(),
      role: role.value.trim(),
      tech_stack: parsedTechStack.value,
      description: description.value.trim(),
      user_contribution: userContribution.value.trim(),
      work_url: workUrl.value.trim() || null
    });
    name.value = "";
    projectType.value = "";
    role.value = "";
    techStackInput.value = "";
    description.value = "";
    userContribution.value = "";
    workUrl.value = "";
    await loadProjects();
  } catch {
    errorMessage.value = "项目保存失败，请检查输入内容或后端服务状态。";
  } finally {
    isSaving.value = false;
  }
}

onMounted(() => {
  void loadProjects();
});
</script>

<template>
  <section class="projects-page">
    <div class="page-header">
      <h1 class="page-title">项目</h1>
    </div>

    <form class="project-form" @submit.prevent="handleSubmit">
      <label class="field">
        <span>项目名称</span>
        <input v-model="name" type="text" placeholder="例如：ResumeFit Demo" />
      </label>

      <label class="field">
        <span>项目类型</span>
        <input v-model="projectType" type="text" placeholder="例如：Web 应用" />
      </label>

      <label class="field">
        <span>我的角色</span>
        <input v-model="role" type="text" placeholder="例如：独立开发 / 组长 / 后端开发" />
      </label>

      <label class="field">
        <span>技术栈</span>
        <textarea v-model="techStackInput" rows="4" placeholder="例如：Vue 3, FastAPI, SQLite" />
      </label>

      <label class="field">
        <span>项目描述</span>
        <textarea v-model="description" rows="6" placeholder="描述项目背景、目标和主要功能" />
      </label>

      <label class="field">
        <span>个人贡献</span>
        <textarea v-model="userContribution" rows="6" placeholder="描述你负责的模块、技术实现和交付内容" />
      </label>

      <label class="field">
        <span>作品链接</span>
        <input v-model="workUrl" type="url" placeholder="https://example.com" />
      </label>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <button class="primary-button" type="submit" :disabled="!canSave || isSaving">
        {{ isSaving ? "保存中..." : "保存项目" }}
      </button>
    </form>

    <section class="project-list-section" aria-labelledby="project-list-title">
      <div class="section-header">
        <h2 id="project-list-title">已保存项目</h2>
        <button class="secondary-button" type="button" :disabled="isLoading" @click="loadProjects">
          {{ isLoading ? "加载中..." : "刷新" }}
        </button>
      </div>

      <p v-if="isLoading" class="muted-text">正在加载项目列表...</p>
      <p v-else-if="projects.length === 0" class="muted-text">还没有保存的项目。</p>

      <div v-else class="project-list">
        <article v-for="project in projects" :key="project.id" class="project-item">
          <div class="project-item-header">
            <div>
              <h3>{{ project.name }}</h3>
              <p class="project-type">{{ project.project_type }}</p>
              <p class="project-role">{{ project.role }}</p>
            </div>
            <time :datetime="project.created_at">{{ formatDate(project.created_at) }}</time>
          </div>

          <div class="tag-list" aria-label="技术栈">
            <span v-for="tech in project.tech_stack" :key="tech">{{ tech }}</span>
          </div>

          <p>{{ previewText(project.description) }}</p>
          <p>{{ previewText(project.user_contribution) }}</p>
          <a v-if="project.work_url" :href="project.work_url" target="_blank" rel="noreferrer">
            {{ project.work_url }}
          </a>
          <div class="project-actions">
            <button class="secondary-button" type="button" @click="selectedProjectDetail = project">查看详情</button>
          </div>
        </article>
      </div>
    </section>

    <DetailModal
      v-if="selectedProjectDetail"
      :title="selectedProjectDetail.name"
      :subtitle="`创建时间：${formatDate(selectedProjectDetail.created_at)} · 更新时间：${formatDate(selectedProjectDetail.updated_at)}`"
      @close="selectedProjectDetail = null"
    >
      <dl class="detail-list">
        <div>
          <dt>项目名称</dt>
          <dd>{{ selectedProjectDetail.name }}</dd>
        </div>
        <div>
          <dt>项目类型</dt>
          <dd>{{ selectedProjectDetail.project_type }}</dd>
        </div>
        <div>
          <dt>我的角色</dt>
          <dd>{{ selectedProjectDetail.role }}</dd>
        </div>
        <div>
          <dt>作品链接</dt>
          <dd>
            <a
              v-if="selectedProjectDetail.work_url"
              :href="selectedProjectDetail.work_url"
              target="_blank"
              rel="noreferrer"
            >
              {{ selectedProjectDetail.work_url }}
            </a>
            <span v-else>未填写</span>
          </dd>
        </div>
        <div>
          <dt>创建时间</dt>
          <dd>{{ formatDate(selectedProjectDetail.created_at) }}</dd>
        </div>
        <div>
          <dt>更新时间</dt>
          <dd>{{ formatDate(selectedProjectDetail.updated_at) }}</dd>
        </div>
      </dl>

      <section class="detail-block">
        <h3>技术栈</h3>
        <div class="tag-list" aria-label="技术栈详情">
          <span v-for="tech in selectedProjectDetail.tech_stack" :key="tech">{{ tech }}</span>
        </div>
      </section>

      <section class="detail-block">
        <h3>项目描述</h3>
        <p class="detail-text">{{ selectedProjectDetail.description }}</p>
      </section>

      <section class="detail-block">
        <h3>个人贡献</h3>
        <p class="detail-text">{{ selectedProjectDetail.user_contribution }}</p>
      </section>
    </DetailModal>
  </section>
</template>

<style scoped>
.projects-page {
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

.project-form,
.project-list-section {
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
.project-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.section-header h2,
.project-item h3,
.project-item p {
  margin: 0;
}

.section-header h2 {
  font-size: 20px;
}

.project-list {
  display: grid;
  gap: 12px;
}

.project-actions {
  display: flex;
  justify-content: flex-end;
}

.project-item {
  display: grid;
  gap: 12px;
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.project-item h3 {
  color: #1d1f24;
  font-size: 18px;
}

.project-item time,
.muted-text,
.project-type,
.project-role {
  color: #667085;
}

.project-item p {
  color: #4d5564;
  line-height: 1.6;
}

.project-item a {
  color: #243b99;
  overflow-wrap: anywhere;
}

.detail-list {
  display: grid;
  gap: 12px;
  margin: 0 0 18px;
}

.detail-list div {
  display: grid;
  gap: 4px;
}

.detail-list dt {
  color: #667085;
  font-size: 13px;
  font-weight: 700;
}

.detail-list dd {
  margin: 0;
  color: #343944;
  line-height: 1.6;
}

.detail-list a {
  color: #243b99;
  overflow-wrap: anywhere;
}

.detail-block {
  display: grid;
  gap: 10px;
  margin-top: 18px;
}

.detail-block h3 {
  margin: 0;
  color: #1d1f24;
  font-size: 18px;
}

.detail-text {
  margin: 0;
  color: #4d5564;
  line-height: 1.7;
  white-space: pre-wrap;
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

.error-message {
  margin: 0;
  color: #b42318;
  font-weight: 600;
}

@media (max-width: 760px) {
  .section-header,
  .project-item-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .project-actions {
    justify-content: flex-start;
  }
}
</style>
