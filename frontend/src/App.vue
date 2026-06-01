<script setup lang="ts">
const navItems = [
  { label: "总览", to: "/" },
  { label: "简历", to: "/resume" },
  { label: "项目", to: "/projects" },
  { label: "JD", to: "/jobs" },
  { label: "分析", to: "/analysis" },
  { label: "版本", to: "/versions" }
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
