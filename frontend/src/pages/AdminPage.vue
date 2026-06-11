<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import {
  getAdminUsageSummary,
  getAdminUserDetail,
  listAdminUsers,
  updateAdminUserStatus,
  type AdminGlobalUsageSummary,
  type AdminUserDetail,
  type AdminUserListItem
} from "../api/admin";
import { authSession } from "../auth/session";
import EmptyState from "../components/common/EmptyState.vue";
import { getFriendlyErrorMessage } from "../utils/errors";

const users = ref<AdminUserListItem[]>([]);
const selectedUser = ref<AdminUserDetail | null>(null);
const usageSummary = ref<AdminGlobalUsageSummary | null>(null);
const totalUsers = ref(0);
const page = ref(1);
const pageSize = 10;
const searchInput = ref("");
const searchQuery = ref("");
const isLoadingUsers = ref(false);
const isLoadingSummary = ref(false);
const isLoadingDetail = ref(false);
const updatingUserId = ref<number | null>(null);
const errorMessage = ref("");
const successMessage = ref("");

const featureLabels: Record<string, string> = {
  jd_analysis: "JD 分析",
  match_report: "匹配报告",
  resume_generation: "定制简历",
  truth_check: "真实性检测",
  interview_question: "面试追问"
};

const pageCount = computed(() => Math.max(Math.ceil(totalUsers.value / pageSize), 1));
const isAdmin = computed(() => authSession.user?.role === "admin");

async function loadAdminDashboard(): Promise<void> {
  await Promise.all([loadUsageSummary(), loadUsers()]);
}

async function loadUsageSummary(): Promise<void> {
  isLoadingSummary.value = true;
  errorMessage.value = "";

  try {
    usageSummary.value = await getAdminUsageSummary();
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    isLoadingSummary.value = false;
  }
}

async function loadUsers(): Promise<void> {
  isLoadingUsers.value = true;
  errorMessage.value = "";

  try {
    const result = await listAdminUsers({
      page: page.value,
      page_size: pageSize,
      search: searchQuery.value
    });
    users.value = result.items;
    totalUsers.value = result.total;

    if (selectedUser.value && !result.items.some((user) => user.id === selectedUser.value?.id)) {
      selectedUser.value = null;
    }
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    isLoadingUsers.value = false;
  }
}

async function searchUsers(): Promise<void> {
  searchQuery.value = searchInput.value.trim();
  page.value = 1;
  await loadUsers();
}

async function goToPage(nextPage: number): Promise<void> {
  page.value = Math.min(Math.max(nextPage, 1), pageCount.value);
  await loadUsers();
}

async function selectUser(userId: number): Promise<void> {
  isLoadingDetail.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    selectedUser.value = await getAdminUserDetail(userId);
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    isLoadingDetail.value = false;
  }
}

async function toggleUserStatus(user: AdminUserListItem | AdminUserDetail): Promise<void> {
  if (updatingUserId.value !== null) {
    return;
  }

  const nextStatus = user.status === "active" ? "disabled" : "active";
  const actionLabel = nextStatus === "disabled" ? "禁用" : "启用";

  if (user.id === authSession.user?.id && nextStatus === "disabled") {
    errorMessage.value = "不能禁用当前登录的管理员账号。";
    return;
  }

  if (!window.confirm(`确认${actionLabel}用户 ${user.email || user.display_name || user.id} 吗？`)) {
    return;
  }

  updatingUserId.value = user.id;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const updatedUser = await updateAdminUserStatus(user.id, nextStatus);
    selectedUser.value = selectedUser.value?.id === updatedUser.id ? updatedUser : selectedUser.value;
    successMessage.value = `用户已${actionLabel}。`;
    await loadUsers();
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    updatingUserId.value = null;
  }
}

function featureLabel(featureType: string): string {
  return featureLabels[featureType] ?? featureType;
}

function statusLabel(status: string): string {
  return status === "active" ? "正常" : "禁用";
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
  void loadAdminDashboard();
});
</script>

<template>
  <section class="page-header">
    <div>
      <p class="eyebrow">Admin</p>
      <h1>管理后台</h1>
      <p>查看用户基础信息、AI 用量概览，并进行轻量账号状态管理。</p>
    </div>
    <button type="button" :disabled="isLoadingUsers || isLoadingSummary" @click="loadAdminDashboard">
      {{ isLoadingUsers || isLoadingSummary ? "正在刷新..." : "刷新" }}
    </button>
  </section>

  <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
  <p v-if="successMessage" class="success-text">{{ successMessage }}</p>

  <EmptyState
    v-if="!isAdmin && errorMessage"
    title="没有管理后台权限"
    description="当前账号不是管理员。管理后台入口隐藏只是体验优化，真正权限由后端接口校验。"
  />

  <template v-else>
    <section class="admin-stats-grid">
      <article class="panel admin-stat-card">
        <span>用户总数</span>
        <strong>{{ totalUsers }}</strong>
      </article>
      <article class="panel admin-stat-card">
        <span>本月 AI 调用</span>
        <strong>{{ usageSummary?.monthly_call_count ?? 0 }}</strong>
      </article>
      <article class="panel admin-stat-card">
        <span>本月成功</span>
        <strong>{{ usageSummary?.monthly_success_count ?? 0 }}</strong>
      </article>
      <article class="panel admin-stat-card">
        <span>本月失败</span>
        <strong>{{ usageSummary?.monthly_failure_count ?? 0 }}</strong>
      </article>
    </section>

    <section class="admin-layout">
      <article class="panel">
        <div class="section-heading admin-section-heading">
          <div>
            <h2>用户列表</h2>
            <p class="muted">仅展示账户基础信息和用量概览，不展示用户简历、项目或 JD 正文。</p>
          </div>
        </div>

        <form class="admin-search-form" @submit.prevent="searchUsers">
          <input v-model="searchInput" type="search" placeholder="搜索 email 或昵称" />
          <button type="submit" :disabled="isLoadingUsers">搜索</button>
        </form>

        <p v-if="isLoadingUsers && users.length === 0" class="muted">正在加载用户列表...</p>
        <EmptyState
          v-else-if="users.length === 0"
          title="没有匹配的用户"
          description="换一个邮箱或昵称关键词再试。"
        />

        <div v-else class="admin-table-wrapper">
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户</th>
                <th>角色</th>
                <th>状态</th>
                <th>本月用量</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>
                  <strong>{{ user.email || "-" }}</strong>
                  <small>{{ user.display_name || "-" }}</small>
                </td>
                <td>{{ user.role }}</td>
                <td>
                  <span class="status-pill" :class="user.status">{{ statusLabel(user.status) }}</span>
                </td>
                <td>{{ user.usage.monthly_used }} / {{ user.usage.monthly_quota }}</td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="table-actions">
                    <button type="button" @click="selectUser(user.id)">详情</button>
                    <button
                      type="button"
                      :disabled="updatingUserId === user.id || (user.id === authSession.user?.id && user.status === 'active')"
                      @click="toggleUserStatus(user)"
                    >
                      {{ user.status === "active" ? "禁用" : "启用" }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination-row">
          <button type="button" :disabled="page <= 1 || isLoadingUsers" @click="goToPage(page - 1)">上一页</button>
          <span>第 {{ page }} / {{ pageCount }} 页，共 {{ totalUsers }} 位用户</span>
          <button type="button" :disabled="page >= pageCount || isLoadingUsers" @click="goToPage(page + 1)">下一页</button>
        </div>
      </article>

      <aside class="panel admin-detail-panel">
        <div class="section-heading">
          <h2>用户详情</h2>
        </div>
        <p v-if="isLoadingDetail" class="muted">正在加载用户详情...</p>
        <EmptyState
          v-else-if="!selectedUser"
          title="尚未选择用户"
          description="点击用户列表中的“详情”查看账户信息和最近 AI 调用。"
        />
        <template v-else>
          <dl class="detail-list">
            <div>
              <dt>ID</dt>
              <dd>{{ selectedUser.id }}</dd>
            </div>
            <div>
              <dt>邮箱</dt>
              <dd>{{ selectedUser.email || "-" }}</dd>
            </div>
            <div>
              <dt>昵称</dt>
              <dd>{{ selectedUser.display_name || "-" }}</dd>
            </div>
            <div>
              <dt>角色</dt>
              <dd>{{ selectedUser.role }}</dd>
            </div>
            <div>
              <dt>状态</dt>
              <dd>{{ statusLabel(selectedUser.status) }}</dd>
            </div>
            <div>
              <dt>创建时间</dt>
              <dd>{{ formatDate(selectedUser.created_at) }}</dd>
            </div>
          </dl>

          <div class="detail-actions">
            <button
              type="button"
              :disabled="updatingUserId === selectedUser.id || (selectedUser.id === authSession.user?.id && selectedUser.status === 'active')"
              @click="toggleUserStatus(selectedUser)"
            >
              {{ selectedUser.status === "active" ? "禁用用户" : "启用用户" }}
            </button>
          </div>

          <section class="detail-usage">
            <h3>用量概览</h3>
            <div class="detail-usage-grid">
              <span>本月 {{ selectedUser.usage_summary.monthly_used }} / {{ selectedUser.usage_summary.monthly_quota }}</span>
              <span>剩余 {{ selectedUser.usage_summary.monthly_remaining }}</span>
              <span>总调用 {{ selectedUser.usage_summary.total_call_count }}</span>
            </div>
          </section>

          <section class="detail-usage">
            <h3>最近 AI 调用</h3>
            <EmptyState
              v-if="selectedUser.usage_summary.recent_calls.length === 0"
              title="暂无调用记录"
              description="该用户还没有 AI 调用日志。"
            />
            <div v-else class="recent-call-list">
              <article v-for="call in selectedUser.usage_summary.recent_calls" :key="call.id" class="recent-call-item">
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
          </section>
        </template>
      </aside>
    </section>

    <section class="panel">
      <div class="section-heading">
        <h2>全站功能调用分布</h2>
      </div>
      <EmptyState
        v-if="!usageSummary || usageSummary.feature_counts.length === 0"
        title="暂无全站 AI 调用"
        description="当用户完成 JD 分析、匹配报告、定制简历、真实性检测或面试追问后，这里会显示功能分布。"
      />
      <div v-else class="feature-grid">
        <article v-for="item in usageSummary.feature_counts" :key="item.feature_type" class="feature-card">
          <span>{{ featureLabel(item.feature_type) }}</span>
          <strong>{{ item.count }}</strong>
          <small>成功 {{ item.success_count }} / 失败 {{ item.failure_count }}</small>
        </article>
      </div>
    </section>
  </template>
</template>

<style scoped>
.admin-stats-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.admin-stat-card {
  display: grid;
  gap: 8px;
}

.admin-stat-card span,
.feature-card span {
  color: #6b7280;
  font-size: 13px;
  font-weight: 700;
}

.admin-stat-card strong,
.feature-card strong {
  color: #1d1f24;
  font-size: 28px;
}

.admin-layout {
  align-items: start;
  display: grid;
  gap: 18px;
  grid-template-columns: minmax(0, 1.4fr) minmax(340px, 0.8fr);
}

.admin-section-heading {
  align-items: start;
}

.admin-search-form {
  display: flex;
  gap: 10px;
  margin: 16px 0;
}

.admin-search-form input {
  flex: 1;
}

.admin-table-wrapper {
  overflow-x: auto;
}

.admin-table {
  border-collapse: collapse;
  min-width: 840px;
  width: 100%;
}

.admin-table th,
.admin-table td {
  border-bottom: 1px solid #eceef3;
  padding: 12px;
  text-align: left;
  vertical-align: top;
}

.admin-table th {
  color: #6b7280;
  font-size: 12px;
}

.admin-table td strong,
.admin-table td small {
  display: block;
}

.admin-table td small {
  color: #6b7280;
  margin-top: 4px;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.pagination-row {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 14px;
}

.admin-detail-panel {
  display: grid;
  gap: 16px;
}

.detail-list {
  display: grid;
  gap: 10px;
  margin: 0;
}

.detail-list div {
  border-bottom: 1px solid #eceef3;
  display: grid;
  gap: 4px;
  padding-bottom: 10px;
}

.detail-list dt {
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
}

.detail-list dd {
  margin: 0;
  overflow-wrap: anywhere;
}

.detail-actions {
  display: flex;
  gap: 10px;
}

.detail-usage {
  display: grid;
  gap: 10px;
}

.detail-usage h3 {
  margin: 0;
}

.detail-usage-grid,
.feature-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}

.detail-usage-grid span,
.feature-card {
  border: 1px solid #eceef3;
  border-radius: 8px;
  padding: 12px;
}

.feature-card {
  display: grid;
  gap: 8px;
}

.recent-call-list {
  display: grid;
  gap: 10px;
}

.recent-call-item {
  border: 1px solid #eceef3;
  border-radius: 8px;
  display: grid;
  gap: 8px;
  padding: 12px;
}

.recent-call-item > div {
  display: flex;
  gap: 10px;
  justify-content: space-between;
}

.status-pill {
  border-radius: 999px;
  display: inline-flex;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 8px;
}

.status-pill.active,
.status-pill.success {
  background: #e7f7ef;
  color: #157347;
}

.status-pill.disabled,
.status-pill.failed {
  background: #fdecec;
  color: #b42318;
}

@media (max-width: 1000px) {
  .admin-stats-grid,
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .admin-search-form,
  .pagination-row,
  .recent-call-item > div {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
