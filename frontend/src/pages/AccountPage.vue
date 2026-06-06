<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { getAccountMe, updateAccountMe, type AccountRead } from "../api/account";
import type { AuthUser } from "../api/auth";
import EmptyState from "../components/common/EmptyState.vue";
import { setCurrentUser } from "../auth/session";
import { getFriendlyErrorMessage } from "../utils/errors";

const account = ref<AccountRead | null>(null);
const displayName = ref("");
const isLoading = ref(false);
const isSaving = ref(false);
const errorMessage = ref("");
const formError = ref("");
const successMessage = ref("");

const featureLabels: Record<string, string> = {
  jd_analysis: "JD 分析",
  match_report: "匹配报告",
  resume_generation: "定制简历",
  truth_check: "真实性检测",
  interview_question: "面试追问"
};

const quotaPercent = computed(() => {
  const summary = account.value?.usage_summary;
  if (!summary || summary.monthly_quota <= 0) {
    return "0%";
  }
  return `${Math.min(Math.round((summary.monthly_used / summary.monthly_quota) * 100), 100)}%`;
});

const recentCalls = computed(() => account.value?.usage_summary.recent_calls.slice(0, 5) ?? []);

async function loadAccount(): Promise<void> {
  isLoading.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const result = await getAccountMe();
    account.value = result;
    displayName.value = result.display_name ?? "";
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    isLoading.value = false;
  }
}

async function saveDisplayName(): Promise<void> {
  if (isSaving.value) {
    return;
  }

  const trimmedName = displayName.value.trim();
  formError.value = "";
  successMessage.value = "";
  errorMessage.value = "";

  if (!trimmedName) {
    formError.value = "昵称不能为空。";
    return;
  }

  if (trimmedName.length > 50) {
    formError.value = "昵称不能超过 50 个字符。";
    return;
  }

  isSaving.value = true;

  try {
    const result = await updateAccountMe({ display_name: trimmedName });
    account.value = result;
    displayName.value = result.display_name ?? "";
    setCurrentUser(toAuthUser(result));
    successMessage.value = "昵称已更新。";
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    isSaving.value = false;
  }
}

function toAuthUser(value: AccountRead): AuthUser {
  return {
    id: value.id,
    email: value.email,
    display_name: value.display_name,
    status: value.status,
    created_at: value.created_at,
    updated_at: value.updated_at
  };
}

function featureLabel(featureType: string): string {
  return featureLabels[featureType] ?? featureType;
}

function statusLabel(status: string): string {
  if (status === "active") {
    return "正常";
  }
  return status;
}

function callStatusLabel(status: string): string {
  return status === "success" ? "成功" : "失败";
}

function formatDate(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString();
}

onMounted(() => {
  void loadAccount();
});
</script>

<template>
  <section class="page-header">
    <div>
      <p class="eyebrow">Account</p>
      <h1>个人中心</h1>
      <p>查看账户信息、调整昵称，并快速了解本月 AI 用量。</p>
    </div>
    <button type="button" :disabled="isLoading" @click="loadAccount">
      {{ isLoading ? "正在刷新..." : "刷新" }}
    </button>
  </section>

  <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
  <p v-if="successMessage" class="success-text">{{ successMessage }}</p>
  <p v-if="isLoading && !account" class="muted">正在加载账户信息...</p>

  <template v-if="account">
    <section class="account-grid">
      <article class="panel account-card">
        <div class="section-heading">
          <h2>账户信息</h2>
        </div>
        <div class="account-info-grid">
          <div class="account-field">
            <span>邮箱</span>
            <strong>{{ account.email }}</strong>
          </div>
          <div class="account-field">
            <span>昵称</span>
            <strong>{{ account.display_name }}</strong>
          </div>
          <div class="account-field">
            <span>账号状态</span>
            <strong>{{ statusLabel(account.status) }}</strong>
          </div>
          <div class="account-field">
            <span>创建时间</span>
            <strong>{{ formatDate(account.created_at) }}</strong>
          </div>
          <div class="account-field">
            <span>更新时间</span>
            <strong>{{ formatDate(account.updated_at) }}</strong>
          </div>
        </div>
      </article>

      <article class="panel account-card">
        <div class="section-heading">
          <h2>修改昵称</h2>
        </div>
        <form class="account-form" @submit.prevent="saveDisplayName">
          <label>
            昵称
            <input v-model="displayName" type="text" maxlength="50" autocomplete="name" />
          </label>
          <p v-if="formError" class="error-text">{{ formError }}</p>
          <button type="submit" :disabled="isSaving">
            {{ isSaving ? "正在保存..." : "保存昵称" }}
          </button>
        </form>
      </article>
    </section>

    <section class="panel">
      <div class="section-heading account-section-heading">
        <div>
          <h2>用量概览</h2>
          <p class="muted">本月额度、已用次数和最近 AI 调用摘要。</p>
        </div>
        <RouterLink class="secondary-link" to="/usage">查看详细用量</RouterLink>
      </div>

      <div class="usage-overview-grid">
        <article class="usage-stat">
          <span>本月额度</span>
          <strong>{{ account.usage_summary.monthly_quota }}</strong>
        </article>
        <article class="usage-stat">
          <span>本月已用</span>
          <strong>{{ account.usage_summary.monthly_used }}</strong>
        </article>
        <article class="usage-stat">
          <span>剩余额度</span>
          <strong>{{ account.usage_summary.monthly_remaining }}</strong>
        </article>
      </div>

      <div class="quota-bar" aria-label="本月 AI 调用额度使用进度">
        <span :style="{ width: quotaPercent }"></span>
      </div>

      <div class="recent-section">
        <h3>最近 AI 调用</h3>
        <EmptyState
          v-if="recentCalls.length === 0"
          title="还没有 AI 调用记录"
          description="完成 JD 分析、匹配报告、定制简历、真实性检测或面试追问后，这里会显示最近记录。"
          action-text="去分析 JD"
          action-to="/jobs"
        />
        <div v-else class="recent-call-list">
          <article v-for="call in recentCalls" :key="call.id" class="recent-call-item">
            <div>
              <strong>{{ featureLabel(call.feature_type) }}</strong>
              <span class="muted">{{ call.model_name }}</span>
            </div>
            <div>
              <span class="status-pill" :class="call.status">{{ callStatusLabel(call.status) }}</span>
              <span class="muted">{{ formatDate(call.created_at) }}</span>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="panel commerce-note">
      <div>
        <h2>会员与额度管理</h2>
        <p class="muted">会员与额度管理后续开放。当前版本仅展示基础额度和用量统计，不包含支付、套餐或订单功能。</p>
      </div>
    </section>
  </template>
</template>

<style scoped>
.account-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
}

.account-card {
  align-content: start;
  display: grid;
  gap: 16px;
}

.account-info-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.account-field,
.usage-stat {
  border: 1px solid #eceef3;
  border-radius: 8px;
  display: grid;
  gap: 8px;
  padding: 14px;
}

.account-field span,
.usage-stat span {
  color: #6b7280;
  font-size: 13px;
  font-weight: 700;
}

.account-field strong {
  color: #1d1f24;
  font-size: 15px;
  overflow-wrap: anywhere;
}

.account-form {
  display: grid;
  gap: 12px;
}

.account-section-heading {
  align-items: start;
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.secondary-link {
  align-items: center;
  border: 1px solid #cfd3dc;
  border-radius: 8px;
  color: #1d1f24;
  display: inline-flex;
  font-weight: 700;
  padding: 9px 12px;
  text-decoration: none;
  white-space: nowrap;
}

.secondary-link:hover {
  background: #f6f7f9;
}

.usage-overview-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 16px;
}

.usage-stat strong {
  color: #1d1f24;
  font-size: 28px;
}

.quota-bar {
  background: #eceef3;
  border-radius: 999px;
  height: 10px;
  margin-top: 16px;
  overflow: hidden;
}

.quota-bar span {
  background: #2f6fed;
  display: block;
  height: 100%;
}

.recent-section {
  display: grid;
  gap: 12px;
  margin-top: 22px;
}

.recent-section h3 {
  margin: 0;
}

.recent-call-list {
  display: grid;
  gap: 10px;
}

.recent-call-item {
  align-items: center;
  border: 1px solid #eceef3;
  border-radius: 8px;
  display: flex;
  gap: 16px;
  justify-content: space-between;
  padding: 12px;
}

.recent-call-item > div {
  display: grid;
  gap: 4px;
}

.recent-call-item > div:last-child {
  justify-items: end;
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

.commerce-note {
  background: #f8fafc;
}

.commerce-note h2 {
  margin-top: 0;
}

@media (max-width: 900px) {
  .account-grid,
  .usage-overview-grid {
    grid-template-columns: 1fr;
  }

  .account-info-grid {
    grid-template-columns: 1fr;
  }

  .account-section-heading,
  .recent-call-item {
    align-items: stretch;
    flex-direction: column;
  }

  .recent-call-item > div:last-child {
    justify-items: start;
  }
}
</style>
