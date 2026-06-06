<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import { authSession, clearSession } from "./auth/session";

const route = useRoute();
const router = useRouter();

const navItems = [
  { label: "首页", to: "/" },
  { label: "通用简历", to: "/resume" },
  { label: "项目库", to: "/projects" },
  { label: "岗位 JD", to: "/jobs" },
  { label: "匹配分析", to: "/analysis" },
  { label: "简历版本", to: "/versions" },
  { label: "用量统计", to: "/usage" }
];

const isAuthPage = computed(() => route.path === "/login" || route.path === "/register");
const userLabel = computed(() => authSession.user?.display_name || authSession.user?.email || "已登录用户");

async function logout(): Promise<void> {
  clearSession();
  await router.push("/login");
}
</script>

<template>
  <div v-if="isAuthPage" class="auth-layout">
    <RouterLink class="auth-brand" to="/login">ResumeFit</RouterLink>
    <main class="auth-content">
      <RouterView />
    </main>
  </div>

  <div v-else class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand" to="/">ResumeFit</RouterLink>
      <nav class="nav-list" aria-label="Primary navigation">
        <RouterLink v-for="item in navItems" :key="item.to" class="nav-link" :to="item.to">
          {{ item.label }}
        </RouterLink>
      </nav>

      <div v-if="authSession.user" class="sidebar-user">
        <span class="sidebar-user-label">当前用户</span>
        <strong>{{ userLabel }}</strong>
        <button type="button" class="logout-button" @click="logout">退出登录</button>
      </div>
    </aside>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  background: #f6f7f9;
  padding: 24px;
}

.auth-brand {
  display: inline-flex;
  color: #1d1f24;
  font-size: 20px;
  font-weight: 700;
}

.auth-content {
  min-height: calc(100vh - 48px);
}

.sidebar-user {
  display: grid;
  gap: 8px;
  margin-top: 28px;
  border-top: 1px solid #eceef3;
  padding-top: 18px;
}

.sidebar-user-label {
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
}

.sidebar-user strong {
  color: #1d1f24;
  font-size: 14px;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.logout-button {
  border: 1px solid #cfd3dc;
  border-radius: 8px;
  background: #ffffff;
  color: #343946;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  padding: 8px 10px;
}

.logout-button:hover {
  background: #f6f7f9;
}
</style>
