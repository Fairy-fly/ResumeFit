<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import {
  analyzeJobDescription,
  createJobDescription,
  listJobDescriptions,
  type JobAnalysisRead,
  type JobDescriptionRead
} from "../api/jobDescriptions";
import DetailModal from "../components/common/DetailModal.vue";
import EmptyState from "../components/common/EmptyState.vue";

const companyName = ref("");
const jobTitle = ref("");
const rawText = ref("");
const companyNameInput = ref<HTMLInputElement | null>(null);
const jobDescriptions = ref<JobDescriptionRead[]>([]);
const selectedJobDescription = ref<JobDescriptionRead | null>(null);
const selectedJobDetail = ref<JobDescriptionRead | null>(null);
const analysis = ref<JobAnalysisRead | null>(null);
const isLoading = ref(false);
const isAnalyzing = ref(false);
const errorMessage = ref("");

const canAnalyze = computed(
  () =>
    companyName.value.trim().length > 0 &&
    jobTitle.value.trim().length > 0 &&
    rawText.value.trim().length > 0
);

const selectedJobDetailAnalysis = computed(() => {
  if (!selectedJobDetail.value || !analysis.value) {
    return null;
  }

  return analysis.value.job_description_id === selectedJobDetail.value.id ? analysis.value : null;
});

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

function focusJobForm(): void {
  companyNameInput.value?.focus();
}

function messageFromError(error: unknown): string {
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }

  return "JD 分析失败，请检查输入内容、AI 配置或后端服务状态。";
}

async function loadJobDescriptions(): Promise<void> {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    jobDescriptions.value = await listJobDescriptions();
  } catch (error) {
    errorMessage.value = messageFromError(error);
  } finally {
    isLoading.value = false;
  }
}

async function handleSubmit(): Promise<void> {
  if (!canAnalyze.value || isAnalyzing.value) {
    return;
  }

  isAnalyzing.value = true;
  errorMessage.value = "";
  analysis.value = null;

  try {
    const savedJobDescription = await createJobDescription({
      company_name: companyName.value.trim(),
      job_title: jobTitle.value.trim(),
      raw_text: rawText.value.trim()
    });
    selectedJobDescription.value = savedJobDescription;
    analysis.value = await analyzeJobDescription(savedJobDescription.id);
    await loadJobDescriptions();
  } catch (error) {
    errorMessage.value = messageFromError(error);
  } finally {
    isAnalyzing.value = false;
  }
}

onMounted(() => {
  void loadJobDescriptions();
});
</script>

<template>
  <section class="jobs-page">
    <div class="page-header">
      <h1 class="page-title">JD 分析</h1>
    </div>

    <form class="job-form" @submit.prevent="handleSubmit">
      <label class="field">
        <span>公司名称</span>
        <input ref="companyNameInput" v-model="companyName" type="text" placeholder="例如：示例科技" />
      </label>

      <label class="field">
        <span>岗位名称</span>
        <input v-model="jobTitle" type="text" placeholder="例如：后端开发工程师" />
      </label>

      <label class="field">
        <span>岗位 JD 原文</span>
        <textarea v-model="rawText" rows="14" placeholder="粘贴目标岗位的 JD 原文" />
      </label>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <button class="primary-button" type="submit" :disabled="!canAnalyze || isAnalyzing">
        {{ isAnalyzing ? "分析中..." : "保存并分析" }}
      </button>
    </form>

    <section v-if="analysis" class="analysis-section" aria-labelledby="analysis-title">
      <div class="section-header">
        <div>
          <h2 id="analysis-title">分析结果</h2>
          <p v-if="selectedJobDescription" class="muted-text">
            {{ selectedJobDescription.company_name }} · {{ selectedJobDescription.job_title }}
          </p>
        </div>
        <time :datetime="analysis.created_at">{{ formatDate(analysis.created_at) }}</time>
      </div>

      <div class="analysis-grid">
        <article class="analysis-card">
          <h3>岗位概览</h3>
          <dl>
            <div>
              <dt>岗位名称</dt>
              <dd>{{ analysis.job_title }}</dd>
            </div>
            <div>
              <dt>岗位类型</dt>
              <dd>{{ analysis.job_type }}</dd>
            </div>
          </dl>
        </article>

        <article class="analysis-card">
          <h3>必备技能</h3>
          <div class="tag-list">
            <span v-for="skill in analysis.required_skills" :key="skill">{{ skill }}</span>
            <span v-if="analysis.required_skills.length === 0">信息不足</span>
          </div>
        </article>

        <article class="analysis-card">
          <h3>加分技能</h3>
          <div class="tag-list">
            <span v-for="skill in analysis.bonus_skills" :key="skill">{{ skill }}</span>
            <span v-if="analysis.bonus_skills.length === 0">信息不足</span>
          </div>
        </article>

        <article class="analysis-card">
          <h3>关键词</h3>
          <div class="tag-list">
            <span v-for="keyword in analysis.keywords" :key="keyword">{{ keyword }}</span>
            <span v-if="analysis.keywords.length === 0">信息不足</span>
          </div>
        </article>

        <article class="analysis-card wide">
          <h3>岗位职责</h3>
          <ul>
            <li v-for="item in analysis.responsibilities" :key="item">{{ item }}</li>
            <li v-if="analysis.responsibilities.length === 0">信息不足</li>
          </ul>
        </article>

        <article class="analysis-card wide">
          <h3>简历侧重点</h3>
          <ul>
            <li v-for="item in analysis.resume_focus_suggestions" :key="item">{{ item }}</li>
            <li v-if="analysis.resume_focus_suggestions.length === 0">信息不足</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="job-list-section" aria-labelledby="job-list-title">
      <div class="section-header">
        <h2 id="job-list-title">已保存 JD</h2>
        <button class="secondary-button" type="button" :disabled="isLoading" @click="loadJobDescriptions">
          {{ isLoading ? "加载中..." : "刷新" }}
        </button>
      </div>

      <p v-if="isLoading" class="muted-text">正在加载 JD 列表...</p>
      <EmptyState
        v-else-if="jobDescriptions.length === 0"
        title="还没有岗位 JD"
        description="粘贴目标岗位 JD 后，系统才能分析岗位要求和关键词。"
        action-text="粘贴岗位 JD"
        secondary-text="如果已经添加数据，请点击刷新。"
        @action="focusJobForm"
      />

      <div v-else class="job-list">
        <article v-for="jobDescription in jobDescriptions" :key="jobDescription.id" class="job-item">
          <div class="job-item-header">
            <div>
              <h3>{{ jobDescription.job_title }}</h3>
              <p>{{ jobDescription.company_name }}</p>
            </div>
            <div class="job-meta">
              <span>{{ jobDescription.status }}</span>
              <time :datetime="jobDescription.created_at">{{ formatDate(jobDescription.created_at) }}</time>
            </div>
          </div>
          <p>{{ previewText(jobDescription.raw_text) }}</p>
          <div class="job-actions">
            <button class="secondary-button" type="button" @click="selectedJobDetail = jobDescription">查看详情</button>
          </div>
        </article>
      </div>
    </section>

    <DetailModal
      v-if="selectedJobDetail"
      :title="selectedJobDetail.job_title"
      :subtitle="`创建时间：${formatDate(selectedJobDetail.created_at)} · 更新时间：${formatDate(selectedJobDetail.updated_at)}`"
      @close="selectedJobDetail = null"
    >
      <dl class="detail-list">
        <div>
          <dt>公司名称</dt>
          <dd>{{ selectedJobDetail.company_name ?? "未填写" }}</dd>
        </div>
        <div>
          <dt>岗位名称</dt>
          <dd>{{ selectedJobDetail.job_title }}</dd>
        </div>
        <div>
          <dt>分析状态</dt>
          <dd>{{ selectedJobDetail.status }}</dd>
        </div>
        <div>
          <dt>创建时间</dt>
          <dd>{{ formatDate(selectedJobDetail.created_at) }}</dd>
        </div>
        <div>
          <dt>更新时间</dt>
          <dd>{{ formatDate(selectedJobDetail.updated_at) }}</dd>
        </div>
      </dl>

      <article class="detail-block">
        <h3>JD 原文</h3>
        <pre class="detail-pre">{{ selectedJobDetail.raw_text }}</pre>
      </article>

      <section v-if="selectedJobDetailAnalysis" class="detail-block">
        <h3>当前分析结果</h3>
        <div class="analysis-grid">
          <article class="analysis-card">
            <h4>岗位概览</h4>
            <dl>
              <div>
                <dt>岗位名称</dt>
                <dd>{{ selectedJobDetailAnalysis.job_title }}</dd>
              </div>
              <div>
                <dt>岗位类型</dt>
                <dd>{{ selectedJobDetailAnalysis.job_type }}</dd>
              </div>
            </dl>
          </article>

          <article class="analysis-card">
            <h4>必备技能</h4>
            <div class="tag-list">
              <span v-for="skill in selectedJobDetailAnalysis.required_skills" :key="skill">{{ skill }}</span>
              <span v-if="selectedJobDetailAnalysis.required_skills.length === 0">信息不足</span>
            </div>
          </article>

          <article class="analysis-card">
            <h4>加分技能</h4>
            <div class="tag-list">
              <span v-for="skill in selectedJobDetailAnalysis.bonus_skills" :key="skill">{{ skill }}</span>
              <span v-if="selectedJobDetailAnalysis.bonus_skills.length === 0">信息不足</span>
            </div>
          </article>

          <article class="analysis-card">
            <h4>关键词</h4>
            <div class="tag-list">
              <span v-for="keyword in selectedJobDetailAnalysis.keywords" :key="keyword">{{ keyword }}</span>
              <span v-if="selectedJobDetailAnalysis.keywords.length === 0">信息不足</span>
            </div>
          </article>

          <article class="analysis-card wide">
            <h4>岗位职责</h4>
            <ul>
              <li v-for="item in selectedJobDetailAnalysis.responsibilities" :key="item">{{ item }}</li>
              <li v-if="selectedJobDetailAnalysis.responsibilities.length === 0">信息不足</li>
            </ul>
          </article>

          <article class="analysis-card wide">
            <h4>简历侧重点建议</h4>
            <ul>
              <li v-for="item in selectedJobDetailAnalysis.resume_focus_suggestions" :key="item">{{ item }}</li>
              <li v-if="selectedJobDetailAnalysis.resume_focus_suggestions.length === 0">信息不足</li>
            </ul>
          </article>
        </div>
      </section>
    </DetailModal>
  </section>
</template>

<style scoped>
.jobs-page {
  display: grid;
  gap: 24px;
  max-width: 1100px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.job-form,
.analysis-section,
.job-list-section {
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
  min-height: 300px;
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
.job-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.section-header h2,
.analysis-card h3,
.job-item h3,
.job-item p {
  margin: 0;
}

.section-header h2 {
  font-size: 20px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.analysis-card,
.job-item {
  display: grid;
  gap: 12px;
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.analysis-card.wide {
  grid-column: 1 / -1;
}

.analysis-card h3,
.job-item h3 {
  color: #1d1f24;
  font-size: 18px;
}

.analysis-card dl {
  display: grid;
  gap: 10px;
  margin: 0;
}

.analysis-card dl div {
  display: grid;
  gap: 4px;
}

.analysis-card dt {
  color: #667085;
  font-size: 13px;
  font-weight: 700;
}

.analysis-card dd {
  margin: 0;
  color: #343944;
}

.analysis-card ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 20px;
}

.analysis-card li,
.job-item p {
  color: #4d5564;
  line-height: 1.6;
}

.job-list {
  display: grid;
  gap: 12px;
}

.job-actions {
  display: flex;
  justify-content: flex-end;
}

.job-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #667085;
  font-size: 13px;
}

.job-meta span {
  border-radius: 999px;
  background: #eef2ff;
  color: #243b99;
  font-weight: 700;
  padding: 5px 9px;
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

.detail-pre {
  overflow-x: auto;
  margin: 0;
  border-radius: 8px;
  background: #f6f7f9;
  color: #1d1f24;
  font: 14px/1.7 "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  padding: 14px;
  white-space: pre-wrap;
}

.analysis-card h4 {
  margin: 0;
  color: #1d1f24;
  font-size: 18px;
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

.muted-text,
.section-header time {
  color: #667085;
}

.error-message {
  margin: 0;
  color: #b42318;
  font-weight: 600;
}

@media (max-width: 760px) {
  .section-header,
  .job-item-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .job-actions {
    justify-content: flex-start;
  }

  .analysis-grid {
    grid-template-columns: 1fr;
  }
}
</style>
