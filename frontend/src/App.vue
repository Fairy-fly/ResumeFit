<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import AppLogo from "./components/AppLogo.vue";
import { authSession, clearSession } from "./auth/session";

const route = useRoute();
const router = useRouter();

const baseNavItems = [
  { label: "首页", to: "/", icon: "⌂" },
  { label: "通用简历", to: "/resume", icon: "CV" },
  { label: "项目库", to: "/projects", icon: "P" },
  { label: "岗位 JD", to: "/jobs", icon: "JD" },
  { label: "匹配分析", to: "/analysis", icon: "M" },
  { label: "简历版本", to: "/versions", icon: "V" },
  { label: "用量统计", to: "/usage", icon: "U" },
  { label: "个人中心", to: "/account", icon: "A" }
];

const navItems = computed(() => {
  if (authSession.user?.role === "admin") {
    return [...baseNavItems, { label: "管理后台", to: "/admin", icon: "AD" }];
  }
  return baseNavItems;
});

const isAuthPage = computed(() => route.path === "/login" || route.path === "/register");
const userLabel = computed(() => authSession.user?.display_name || authSession.user?.email || "已登录用户");

async function logout(): Promise<void> {
  clearSession();
  await router.push("/login");
}
</script>

<template>
  <div v-if="isAuthPage" class="auth-layout">
    <RouterLink class="auth-brand" to="/login">
      <AppLogo />
      <span>
        <strong>ResumeFit</strong>
        <small>AI Resume Workspace</small>
      </span>
    </RouterLink>
    <main class="auth-content">
      <RouterView />
    </main>
  </div>

  <div v-else class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand" to="/">
        <AppLogo />
        <span class="brand-copy">
          <span class="brand-title">ResumeFit</span>
          <span class="brand-subtitle">AI Resume Workspace</span>
        </span>
      </RouterLink>
      <nav class="nav-list" aria-label="Primary navigation">
        <RouterLink v-for="item in navItems" :key="item.to" class="nav-link" :to="item.to">
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
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
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 100vh;
  background:
    radial-gradient(ellipse 70% 45% at 18% 8%, rgba(75, 92, 240, 0.08), transparent 55%),
    radial-gradient(ellipse 52% 40% at 86% 28%, rgba(24, 169, 153, 0.06), transparent 55%),
    var(--page-bg);
  padding: 24px;
}

.auth-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--text-main);
}

.auth-brand span {
  display: grid;
  gap: 1px;
}

.auth-brand strong {
  font-size: 20px;
  font-weight: 850;
  line-height: 1.1;
}

.auth-brand small {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 750;
}

.auth-content {
  display: grid;
  min-height: calc(100vh - 72px);
}

.sidebar-user {
  display: grid;
  gap: 7px;
  margin-top: auto;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.04);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  padding: 12px;
}

.sidebar-user::before {
  content: "";
  display: block;
  width: 32px;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--brand-primary), var(--brand-teal));
}

/* Kept for older layout spacing if user card wraps after nav. */
.sidebar-user + .sidebar-user {
  margin-top: 28px;
}

.sidebar-user-label {
  color: var(--sidebar-text);
  font-size: 12px;
  font-weight: 700;
}

.sidebar-user strong {
  color: #ffffff;
  font-size: 14px;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.logout-button {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.06);
  color: #e2e8f0;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 800;
  padding: 8px 10px;
}

.logout-button:hover {
  border-color: rgba(255, 255, 255, 0.24);
  background: rgba(255, 255, 255, 0.11);
  color: #ffffff;
}
</style>
