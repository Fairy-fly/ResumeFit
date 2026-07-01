<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { getUsageSummary, type AIUsageSummary } from "../api/usage";
import EmptyState from "../components/common/EmptyState.vue";
import { getFriendlyErrorMessage } from "../utils/errors";

const summary = ref<AIUsageSummary | null>(null);
const isLoading = ref(false);
const errorMessage = ref("");

const featureLabels: Record<string, string> = {
  jd_analysis: "JD 分析",
  match_report: "匹配报告",
  resume_generation: "定制简历",
  truth_check: "真实性检测",
  interview_question: "面试追问"
};

const quotaPercent = computed(() => {
  if (!summary.value || summary.value.monthly_quota <= 0) {
    return "0%";
  }
  return `${Math.min(Math.round((summary.value.monthly_used / summary.value.monthly_quota) * 100), 100)}%`;
});

const hasUsage = computed(() => (summary.value?.total_call_count ?? 0) > 0);

async function loadUsageSummary(): Promise<void> {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    summary.value = await getUsageSummary();
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    isLoading.value = false;
  }
}

function featureLabel(featureType: string): string {
  return featureLabels[featureType] ?? featureType;
}

function statusLabel(status: string): string {
  return status === "success" ? "成功" : "失败";
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

function formatTokens(value: number | null): string {
  return value === null ? "-" : String(value);
}

function formatCost(value: number | null): string {
  return value === null ? "-" : value.toFixed(6);
}

onMounted(() => {
  void loadUsageSummary();
});
</script>

<template>
  <section class="usage-page motion-page">
    <header class="page-hero usage-hero">
      <div>
        <p class="eyebrow">Usage</p>
        <h1 class="page-title">用量统计</h1>
        <p>查看当前账号的 AI 调用次数、额度消耗、功能分布和最近调用记录。</p>
      </div>
      <button class="secondary-action" type="button" :disabled="isLoading" @click="loadUsageSummary">
        {{ isLoading ? "正在刷新..." : "刷新" }}
      </button>
    </header>

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    <p v-if="isLoading && !summary" class="muted">正在加载用量统计...</p>

    <template v-if="summary">
      <section class="usage-grid">
        <article class="metric-card usage-quota-card">
          <div class="metric-heading">
            <span>本月额度</span>
            <small>{{ quotaPercent }} 已使用</small>
          </div>
          <strong>{{ summary.monthly_used }} / {{ summary.monthly_quota }}</strong>
          <div class="quota-bar" aria-label="本月 AI 调用额度使用进度">
            <span :style="{ width: quotaPercent }"></span>
          </div>
          <p class="muted">剩余额度：{{ summary.monthly_remaining }}</p>
        </article>

        <article class="metric-card stat-card">
          <span class="metric-label">总调用次数</span>
          <strong>{{ summary.total_call_count }}</strong>
          <small>累计 AI 调用</small>
        </article>

        <article class="metric-card stat-card">
          <span class="metric-label">本月成功</span>
          <strong>{{ summary.monthly_success_count }}</strong>
          <small>成功返回结果</small>
        </article>

        <article class="metric-card stat-card">
          <span class="metric-label">本月失败</span>
          <strong>{{ summary.monthly_failure_count }}</strong>
          <small>网络或格式异常</small>
        </article>
      </section>

      <section class="page-section">
        <div class="section-heading">
          <div>
            <h2>功能调用分布</h2>
            <p class="muted">按 JD 分析、匹配报告、定制简历、真实性检测和面试追问拆分。</p>
          </div>
        </div>
        <div v-if="hasUsage" class="feature-grid">
          <article v-for="item in summary.feature_counts" :key="item.feature_type" class="usage-feature-card">
            <div>
              <span>{{ featureLabel(item.feature_type) }}</span>
              <small>成功 {{ item.success_count }} / 失败 {{ item.failure_count }}</small>
            </div>
            <strong>{{ item.count }}</strong>
          </article>
        </div>
        <EmptyState
          v-else
          title="还没有 AI 调用记录"
          description="完成 JD 分析、匹配报告、定制简历、真实性检测或面试追问后，这里会展示用量统计。"
          action-text="去分析 JD"
          action-to="/jobs"
        />
      </section>

      <section class="page-section">
        <div class="section-heading">
          <div>
            <h2>最近调用记录</h2>
            <p class="muted">用于排查 AI 调用状态、模型、Token 和成本估算。</p>
          </div>
        </div>
        <div v-if="hasUsage" class="usage-table-wrapper">
          <table class="usage-table">
            <thead>
              <tr>
                <th>功能</th>
                <th>模型</th>
                <th>状态</th>
                <th>Token</th>
                <th>估算成本</th>
                <th>时间</th>
                <th>错误信息</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="call in summary.recent_calls" :key="call.id">
                <td>{{ featureLabel(call.feature_type) }}</td>
                <td>{{ call.model_name }}</td>
                <td>
                  <span class="status-pill" :class="call.status">{{ statusLabel(call.status) }}</span>
                </td>
                <td>{{ formatTokens(call.total_tokens) }}</td>
                <td>{{ formatCost(call.estimated_cost) }}</td>
                <td>{{ formatDate(call.created_at) }}</td>
                <td>{{ call.error_message || "-" }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <EmptyState
          v-else
          title="最近调用为空"
          description="当你完成任意 AI 功能后，最近调用记录会出现在这里。"
          action-text="去分析 JD"
          action-to="/jobs"
        />
      </section>
    </template>
  </section>
</template>

<style scoped>
.usage-page {
  display: grid;
  gap: 22px;
}

.usage-hero p {
  max-width: 720px;
  margin: 10px 0 0;
  color: var(--text-muted);
  line-height: 1.7;
}

.secondary-action {
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--text-secondary);
  cursor: pointer;
  font-weight: 800;
  padding: 9px 14px;
}

.usage-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.usage-quota-card {
  grid-column: span 2;
}

.usage-quota-card,
.stat-card,
.usage-feature-card {
  display: grid;
  gap: 10px;
  padding: 18px;
}

.metric-heading,
.section-heading,
.usage-feature-card {
  align-items: center;
  display: flex;
  justify-content: space-between;
}

.metric-heading span,
.metric-label,
.usage-feature-card span {
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 850;
}

.metric-heading small,
.stat-card small,
.usage-feature-card small {
  color: var(--text-faint);
  font-size: 12px;
}

.usage-quota-card strong,
.stat-card strong,
.usage-feature-card strong {
  color: var(--text-primary);
  font-size: 28px;
  line-height: 1;
}

.quota-bar {
  background: #e2e8f0;
  border-radius: 999px;
  height: 10px;
  overflow: hidden;
}

.quota-bar span {
  background: var(--brand-gradient);
  display: block;
  height: 100%;
}

.feature-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  margin-top: 16px;
}

.usage-feature-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  background: linear-gradient(180deg, #ffffff, #f8fbff);
}

.section-heading h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 20px;
}

.section-heading p {
  margin: 4px 0 0;
}

.usage-table-wrapper {
  overflow-x: auto;
  margin-top: 16px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
}

.usage-table {
  border-collapse: collapse;
  min-width: 820px;
  width: 100%;
}

.usage-table th,
.usage-table td {
  border-bottom: 1px solid var(--border-soft);
  padding: 12px;
  text-align: left;
  vertical-align: top;
}

.usage-table th {
  background: #f8fafc;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 850;
}

.usage-table tbody tr:hover {
  background: #f8fafc;
}

.status-pill.success {
  background: var(--success-soft);
  color: var(--success);
}

.status-pill.failed {
  background: var(--danger-soft);
  color: var(--danger);
}

@media (max-width: 900px) {
  .usage-grid {
    grid-template-columns: 1fr;
  }

  .usage-quota-card {
    grid-column: span 1;
  }

  .metric-heading,
  .section-heading,
  .usage-feature-card {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
