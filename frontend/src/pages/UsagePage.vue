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
  <section class="page-header">
    <div>
      <p class="eyebrow">Usage</p>
      <h1>用量统计</h1>
      <p>查看当前账号的 AI 调用次数、额度消耗、功能分布和最近调用记录。</p>
    </div>
    <button type="button" :disabled="isLoading" @click="loadUsageSummary">
      {{ isLoading ? "正在刷新..." : "刷新" }}
    </button>
  </section>

  <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
  <p v-if="isLoading && !summary" class="muted">正在加载用量统计...</p>

  <template v-if="summary">
    <section class="usage-grid">
      <article class="panel usage-quota-card">
        <span class="muted">本月额度</span>
        <strong>{{ summary.monthly_used }} / {{ summary.monthly_quota }}</strong>
        <div class="quota-bar" aria-label="本月 AI 调用额度使用进度">
          <span :style="{ width: quotaPercent }"></span>
        </div>
        <p class="muted">剩余额度：{{ summary.monthly_remaining }}</p>
      </article>

      <article class="panel stat-card">
        <span class="muted">总调用次数</span>
        <strong>{{ summary.total_call_count }}</strong>
      </article>

      <article class="panel stat-card">
        <span class="muted">本月成功</span>
        <strong>{{ summary.monthly_success_count }}</strong>
      </article>

      <article class="panel stat-card">
        <span class="muted">本月失败</span>
        <strong>{{ summary.monthly_failure_count }}</strong>
      </article>
    </section>

    <EmptyState
      v-if="!hasUsage"
      title="还没有 AI 调用记录"
      description="完成 JD 分析、匹配报告、定制简历、真实性检测或面试追问后，这里会展示用量统计。"
      action-text="去分析 JD"
      action-to="/jobs"
    />

    <section v-else class="panel">
      <div class="section-heading">
        <h2>各功能调用次数</h2>
      </div>
      <div class="feature-grid">
        <article v-for="item in summary.feature_counts" :key="item.feature_type" class="usage-feature-card">
          <span>{{ featureLabel(item.feature_type) }}</span>
          <strong>{{ item.count }}</strong>
          <small>成功 {{ item.success_count }} / 失败 {{ item.failure_count }}</small>
        </article>
      </div>
    </section>

    <section v-if="hasUsage" class="panel">
      <div class="section-heading">
        <h2>最近调用记录</h2>
      </div>
      <div class="usage-table-wrapper">
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
    </section>
  </template>
</template>

<style scoped>
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
}

.usage-quota-card strong,
.stat-card strong,
.usage-feature-card strong {
  color: #1d1f24;
  font-size: 28px;
}

.quota-bar {
  background: #eceef3;
  border-radius: 999px;
  height: 10px;
  overflow: hidden;
}

.quota-bar span {
  background: #2f6fed;
  display: block;
  height: 100%;
}

.feature-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.usage-feature-card {
  border: 1px solid #eceef3;
  border-radius: 8px;
  padding: 14px;
}

.usage-table-wrapper {
  overflow-x: auto;
}

.usage-table {
  border-collapse: collapse;
  min-width: 820px;
  width: 100%;
}

.usage-table th,
.usage-table td {
  border-bottom: 1px solid #eceef3;
  padding: 12px;
  text-align: left;
  vertical-align: top;
}

.usage-table th {
  color: #6b7280;
  font-size: 12px;
}

.status-pill {
  border-radius: 999px;
  display: inline-flex;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 8px;
}

.status-pill.success {
  background: #e7f7ef;
  color: #157347;
}

.status-pill.failed {
  background: #fdecec;
  color: #b42318;
}

@media (max-width: 900px) {
  .usage-grid {
    grid-template-columns: 1fr;
  }

  .usage-quota-card {
    grid-column: span 1;
  }
}
</style>
