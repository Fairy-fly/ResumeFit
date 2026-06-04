<script setup lang="ts">
const navItems = [
  { label: "首页", to: "/" },
  { label: "通用简历", to: "/resume" },
  { label: "项目库", to: "/projects" },
  { label: "岗位 JD", to: "/jobs" },
  { label: "匹配分析", to: "/analysis" },
  { label: "简历版本", to: "/versions" }
];
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand" to="/">ResumeFit</RouterLink>
      <nav class="nav-list" aria-label="Primary navigation">
        <RouterLink v-for="item in navItems" :key="item.to" class="nav-link" :to="item.to">
          {{ item.label }}
        </RouterLink>
      </nav>
    </aside>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>
