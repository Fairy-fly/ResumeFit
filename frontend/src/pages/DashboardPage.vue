<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { getDashboardSummary, type DashboardSummary } from "../api/dashboard";
import { getFriendlyErrorMessage } from "../utils/errors";

interface WorkflowStep {
  title: string;
  description: string;
  route: string;
  action: string;
}

interface NextAction {
  title: string;
  description: string;
  route: string;
  actionText: string;
}

const summary = ref<DashboardSummary | null>(null);
const isLoading = ref(false);
const errorMessage = ref("");

const workflowSteps: WorkflowStep[] = [
  {
    title: "填写通用简历",
    description: "录入基础简历正文，作为后续生成和校验的事实来源。",
    route: "/resume",
    action: "去填写"
  },
  {
    title: "添加项目经历",
    description: "维护真实项目、技术栈、个人角色、贡献和作品链接。",
    route: "/projects",
    action: "去添加"
  },
  {
    title: "粘贴岗位 JD",
    description: "保存公司、岗位和 JD 原文，并生成结构化岗位分析。",
    route: "/jobs",
    action: "去分析"
  },
  {
    title: "生成匹配度报告",
    description: "选择简历、项目和已分析 JD，获得匹配分数与修改方向。",
    route: "/analysis",
    action: "去匹配"
  },
  {
    title: "生成定制简历",
    description: "基于匹配报告输出 Markdown 简历和每处修改原因。",
    route: "/versions",
    action: "去生成"
  },
  {
    title: "真实性风险检测",
    description: "检查夸大、缺证据、不确定内容被写成确定事实等风险。",
    route: "/versions",
    action: "去检测"
  },
  {
    title: "面试追问预测",
    description: "围绕定制简历、岗位和风险点准备真实、保守的回答。",
    route: "/versions",
    action: "去准备"
  },
  {
    title: "导出 Markdown",
    description: "将选中的简历版本下载为 .md 文件，便于投递和排版。",
    route: "/versions",
    action: "去导出"
  }
];

const quickLinks = [
  { label: "填写简历", route: "/resume", description: "录入和查看原始简历" },
  { label: "添加项目", route: "/projects", description: "管理可用于简历的真实项目" },
  { label: "分析 JD", route: "/jobs", description: "保存 JD 并生成岗位分析" },
  { label: "生成报告", route: "/analysis", description: "生成匹配度报告" },
  { label: "管理版本", route: "/versions", description: "生成、检测、追问和导出" }
];

const statCards = computed(() => [
  {
    label: "简历数量",
    value: summary.value?.resume_profile_count ?? 0,
    route: "/resume",
    hint: "通用简历"
  },
  {
    label: "项目数量",
    value: summary.value?.project_count ?? 0,
    route: "/projects",
    hint: "项目经历"
  },
  {
    label: "岗位 JD 数量",
    value: summary.value?.job_description_count ?? 0,
    route: "/jobs",
    hint: "岗位原文"
  },
  {
    label: "匹配报告数量",
    value: summary.value?.match_report_count ?? 0,
    route: "/analysis",
    hint: "AI 匹配报告"
  },
  {
    label: "简历版本数量",
    value: summary.value?.resume_version_count ?? 0,
    route: "/versions",
    hint: "Markdown 版本"
  }
]);

const completedCoreSteps = computed(() => {
  if (!summary.value) {
    return 0;
  }

  return [
    summary.value.resume_profile_count > 0,
    summary.value.project_count > 0,
    summary.value.job_description_count > 0,
    summary.value.match_report_count > 0,
    summary.value.resume_version_count > 0
  ].filter(Boolean).length;
});

const progressPercent = computed(() => `${Math.round((completedCoreSteps.value / 5) * 100)}%`);

const nextAction = computed<NextAction | null>(() => {
  if (!summary.value) {
    return null;
  }

  if (summary.value.resume_profile_count === 0) {
    return {
      title: "填写通用简历",
      description: "先粘贴或输入一份基础简历，后续才能进行岗位匹配和定制生成。",
      route: "/resume",
      actionText: "填写简历"
    };
  }

  if (summary.value.project_count === 0) {
    return {
      title: "添加项目经历",
      description: "项目经历会用于证明技能真实性，并帮助定制简历更有针对性。",
      route: "/projects",
      actionText: "添加项目"
    };
  }

  if (summary.value.job_description_count === 0) {
    return {
      title: "粘贴并分析岗位 JD",
      description: "保存目标岗位 JD 后，系统才能提取岗位要求、关键词和简历侧重点。",
      route: "/jobs",
      actionText: "分析 JD"
    };
  }

  if (summary.value.match_report_count === 0) {
    return {
      title: "生成匹配度报告",
      description: "选择通用简历、项目经历和已分析 JD，生成岗位匹配分数与修改建议。",
      route: "/analysis",
      actionText: "生成报告"
    };
  }

  if (summary.value.resume_version_count === 0) {
    return {
      title: "生成定制简历",
      description: "基于匹配报告生成 Markdown 定制简历，并查看每处修改原因。",
      route: "/versions",
      actionText: "生成定制简历"
    };
  }

  return {
    title: "进入简历版本工作区",
    description: "核心链路已跑通，可以继续做真实性检测、面试追问预测或导出 Markdown。",
    route: "/versions",
    actionText: "管理版本"
  };
});

function workflowStatus(index: number): "done" | "current" | "pending" | "available" {
  if (index < 5) {
    if (index < completedCoreSteps.value) {
      return "done";
    }

    if (index === completedCoreSteps.value && completedCoreSteps.value < 5) {
      return "current";
    }

    return "pending";
  }

  return summary.value?.resume_version_count ? "available" : "pending";
}

function workflowStatusLabel(index: number): string {
  const status = workflowStatus(index);
  const labels = {
    done: "已完成",
    current: "下一步",
    available: "可继续",
    pending: "待完成"
  };

  return labels[status];
}

async function loadSummary() {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    summary.value = await getDashboardSummary();
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    isLoading.value = false;
  }
}

onMounted(loadSummary);
</script>

<template>
  <section class="dashboard-page">
    <header class="dashboard-header">
      <div>
        <p class="eyebrow">Demo 操作台</p>
        <h1 class="page-title">ResumeFit 演示流程</h1>
        <p class="dashboard-intro">
          从真实材料输入到 Markdown 导出，按顺序跑通完整的简历定制与求职准备链路。
        </p>
      </div>
      <button class="refresh-button" type="button" :disabled="isLoading" @click="loadSummary">
        {{ isLoading ? "刷新中" : "刷新统计" }}
      </button>
    </header>

    <p v-if="errorMessage" class="status-message error">
      {{ errorMessage }}
    </p>

    <section class="dashboard-overview" aria-labelledby="progress-title">
      <article class="progress-card">
        <div>
          <p class="eyebrow">当前完成进度</p>
          <h2 id="progress-title">{{ completedCoreSteps }} / 5</h2>
          <p>简历、项目、岗位 JD、匹配报告和简历版本五项核心数据。</p>
        </div>
        <div class="progress-bar" aria-hidden="true">
          <span :style="{ width: progressPercent }"></span>
        </div>
      </article>

      <article class="next-action-card">
        <p class="eyebrow">下一步建议</p>
        <template v-if="nextAction">
          <h2>{{ nextAction.title }}</h2>
          <p>{{ nextAction.description }}</p>
          <RouterLink class="primary-action" :to="nextAction.route">{{ nextAction.actionText }}</RouterLink>
        </template>
        <template v-else>
          <h2>正在读取项目进度</h2>
          <p>加载完成后，这里会根据当前数据给出下一步建议。</p>
        </template>
      </article>
    </section>

    <section class="dashboard-section" aria-labelledby="summary-title">
      <div class="section-heading">
        <h2 id="summary-title">当前数据</h2>
        <p>只统计数量，不暴露简历正文、项目内容或 JD 原文。</p>
      </div>
      <div class="stat-grid" aria-live="polite">
        <RouterLink v-for="stat in statCards" :key="stat.label" class="stat-card" :to="stat.route">
          <span class="stat-label">{{ stat.label }}</span>
          <strong>{{ stat.value }}</strong>
          <span class="stat-hint">{{ stat.hint }}</span>
        </RouterLink>
      </div>
    </section>

    <section class="dashboard-section" aria-labelledby="workflow-title">
      <div class="section-heading">
        <h2 id="workflow-title">8 步 Demo 流程</h2>
        <p>答辩或演示时建议从上到下依次完成，每一步都对应一个可操作页面。</p>
      </div>
      <div class="workflow-grid">
        <article
          v-for="(step, index) in workflowSteps"
          :key="step.title"
          class="step-card"
          :class="`step-${workflowStatus(index)}`"
        >
          <div class="step-index">{{ index + 1 }}</div>
          <span class="step-status">{{ workflowStatusLabel(index) }}</span>
          <h3>{{ step.title }}</h3>
          <p>{{ step.description }}</p>
          <RouterLink class="step-action" :to="step.route">{{ step.action }}</RouterLink>
        </article>
      </div>
    </section>

    <section class="dashboard-section" aria-labelledby="links-title">
      <div class="section-heading">
        <h2 id="links-title">快捷入口</h2>
        <p>/versions 页面承载定制简历、真实性检测、面试追问和 Markdown 导出。</p>
      </div>
      <div class="quick-link-grid">
        <RouterLink v-for="link in quickLinks" :key="link.route" class="quick-link-card" :to="link.route">
          <span>{{ link.label }}</span>
          <small>{{ link.description }}</small>
        </RouterLink>
      </div>
    </section>
  </section>
</template>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 32px;
}

.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #49605f;
  font-size: 13px;
  font-weight: 700;
}

.dashboard-intro {
  max-width: 760px;
  margin: 12px 0 0;
  color: #5b6270;
  font-size: 15px;
  line-height: 1.7;
}

.refresh-button,
.step-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  border-radius: 8px;
  border: 1px solid #c7ccd6;
  background: #ffffff;
  color: #26313f;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.refresh-button {
  flex: 0 0 auto;
  padding: 0 14px;
}

.refresh-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.status-message {
  margin: 0;
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 14px;
}

.status-message.error {
  border: 1px solid #f2b8b5;
  background: #fff4f2;
  color: #9b2c1f;
}

.dashboard-overview {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  gap: 16px;
}

.progress-card,
.next-action-card {
  display: grid;
  gap: 16px;
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  padding: 20px;
}

.next-action-card {
  border-color: #9eb2ff;
  background: #f5f7ff;
}

.progress-card h2,
.next-action-card h2 {
  margin: 0;
  color: #1f2a37;
  font-size: 28px;
  line-height: 1.2;
}

.progress-card p,
.next-action-card p {
  margin: 8px 0 0;
  color: #5f6877;
  line-height: 1.6;
}

.progress-bar {
  overflow: hidden;
  height: 10px;
  border-radius: 999px;
  background: #e6e9f2;
}

.progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #243b99;
  transition: width 0.2s ease;
}

.primary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  min-height: 40px;
  border-radius: 8px;
  background: #243b99;
  color: #ffffff;
  font-weight: 800;
  padding: 0 16px;
}

.dashboard-section {
  display: grid;
  gap: 16px;
}

.section-heading h2 {
  margin: 0;
  font-size: 20px;
  line-height: 1.25;
}

.section-heading p {
  margin: 6px 0 0;
  color: #676f7d;
  font-size: 14px;
  line-height: 1.6;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.stat-card,
.step-card,
.quick-link-card {
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
}

.stat-card {
  display: grid;
  gap: 6px;
  min-height: 116px;
  padding: 16px;
}

.stat-card strong {
  color: #1f2a37;
  font-size: 32px;
  line-height: 1;
}

.stat-label,
.stat-hint {
  color: #687181;
  font-size: 13px;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.step-card {
  display: grid;
  grid-template-rows: auto auto auto 1fr auto;
  gap: 10px;
  min-height: 220px;
  padding: 18px;
}

.step-card.step-current {
  border-color: #9eb2ff;
  background: #f5f7ff;
  box-shadow: inset 4px 0 0 #243b99;
}

.step-card.step-done {
  border-color: #b7dec5;
  background: #f7fcf9;
}

.step-card.step-available {
  border-color: #c7ccd6;
  background: #fbfcff;
}

.step-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #e9f4ef;
  color: #245845;
  font-weight: 800;
}

.step-current .step-index {
  background: #243b99;
  color: #ffffff;
}

.step-done .step-index {
  background: #dff4e7;
  color: #176b3a;
}

.step-status {
  width: fit-content;
  border-radius: 999px;
  background: #eef2ff;
  color: #243b99;
  font-size: 12px;
  font-weight: 800;
  padding: 4px 8px;
}

.step-done .step-status {
  background: #e9f8ef;
  color: #176b3a;
}

.step-pending .step-status {
  background: #f1f3f7;
  color: #687181;
}

.step-card h3 {
  margin: 0;
  font-size: 17px;
  line-height: 1.35;
}

.step-card p {
  margin: 0;
  color: #5f6877;
  font-size: 14px;
  line-height: 1.65;
}

.step-action {
  width: fit-content;
  padding: 0 12px;
  background: #26313f;
  color: #ffffff;
}

.quick-link-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.quick-link-card {
  display: grid;
  gap: 8px;
  min-height: 96px;
  padding: 16px;
}

.quick-link-card span {
  font-weight: 800;
}

.quick-link-card small {
  color: #66707f;
  font-size: 13px;
  line-height: 1.5;
}

.stat-card:hover,
.quick-link-card:hover {
  border-color: #98a4b7;
}

@media (max-width: 1180px) {
  .stat-grid,
  .quick-link-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .workflow-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .dashboard-header {
    display: grid;
  }

  .dashboard-overview {
    grid-template-columns: 1fr;
  }

  .refresh-button {
    width: fit-content;
  }

  .stat-grid,
  .workflow-grid,
  .quick-link-grid {
    grid-template-columns: 1fr;
  }
}
</style>
