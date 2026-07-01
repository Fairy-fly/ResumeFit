<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import { login } from "../api/auth";
import { saveSession } from "../auth/session";
import { getFriendlyErrorMessage } from "../utils/errors";

const router = useRouter();
const route = useRoute();

const email = ref("");
const password = ref("");
const isSubmitting = ref(false);
const errorMessage = ref("");

const redirectPath = computed(() => {
  const redirect = route.query.redirect;
  return typeof redirect === "string" && redirect.startsWith("/") ? redirect : "/";
});

async function submitLogin(): Promise<void> {
  if (isSubmitting.value) {
    return;
  }

  errorMessage.value = "";
  isSubmitting.value = true;

  try {
    const response = await login({
      email: email.value,
      password: password.value
    });
    saveSession(response);
    await router.push(redirectPath.value);
  } catch (error) {
    errorMessage.value = getFriendlyErrorMessage(error);
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <section class="auth-page" aria-labelledby="login-title">
    <aside class="auth-story">
      <p class="auth-eyebrow">AI Resume Workspace</p>
      <h2>从真实经历到可投递简历，一条链路完成。</h2>
      <p>
        ResumeFit 帮你围绕目标岗位整理简历、项目、匹配报告、真实性风险和面试追问，
        保持表达专业，也守住真实边界。
      </p>
      <div class="auth-feature-grid" aria-label="ResumeFit 核心能力">
        <span>定制简历</span>
        <span>真实性检测</span>
        <span>面试追问</span>
        <span>DOCX 导出</span>
      </div>
    </aside>

    <div class="auth-panel">
      <p class="auth-eyebrow">ResumeFit Account</p>
      <h1 id="login-title">登录账号</h1>
      <p class="auth-description">登录后进入你的 AI 求职工作台，继续管理简历版本、用量和导出文件。</p>

      <form class="auth-form" @submit.prevent="submitLogin">
        <label>
          邮箱
          <input v-model.trim="email" type="email" autocomplete="email" required placeholder="you@example.com" />
        </label>

        <label>
          密码
          <input v-model="password" type="password" autocomplete="current-password" required placeholder="请输入密码" />
        </label>

        <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>

        <button class="auth-submit" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? "正在登录..." : "登录" }}
        </button>
      </form>

      <p class="auth-switch">
        还没有账号？
        <RouterLink to="/register">去注册</RouterLink>
      </p>
    </div>
  </section>
</template>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(320px, 0.95fr) minmax(360px, 440px);
  align-items: center;
  gap: 40px;
  min-height: calc(100vh - 64px);
  padding: 32px;
}

.auth-story {
  display: grid;
  gap: 18px;
  max-width: 620px;
}

.auth-story h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(34px, 4vw, 54px);
  line-height: 1.08;
  letter-spacing: -0.02em;
}

.auth-story p {
  max-width: 560px;
  margin: 0;
  color: var(--text-muted);
  font-size: 16px;
  line-height: 1.8;
}

.auth-feature-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 180px));
  gap: 10px;
  margin-top: 8px;
}

.auth-feature-grid span {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  background: rgb(255 255 255 / 0.78);
  box-shadow: var(--shadow-xs);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 800;
  padding: 10px 12px;
}

.auth-panel {
  width: min(100%, 440px);
  justify-self: center;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: linear-gradient(180deg, rgb(255 255 255 / 0.98), rgb(248 251 255 / 0.96));
  box-shadow: var(--shadow-lg);
  padding: 32px;
  animation: fadeUp 0.35s ease both;
}

@media (max-width: 900px) {
  .auth-page {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 22px 0;
  }

  .auth-story {
    max-width: 520px;
    justify-self: center;
    text-align: center;
  }

  .auth-feature-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: min(100%, 420px);
    justify-self: center;
  }
}

.auth-panel::before {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  height: 4px;
  background: var(--brand-gradient);
  content: "";
}

.auth-eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: 28px;
}

.auth-description {
  margin: 10px 0 22px;
  color: var(--text-muted);
  line-height: 1.6;
}

.auth-form {
  display: grid;
  gap: 16px;
}

label {
  display: grid;
  gap: 8px;
  color: var(--text-primary);
  font-weight: 700;
}

input {
  width: 100%;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--text-primary);
  padding: 11px 12px;
  font: inherit;
}

.auth-error {
  margin: 0;
  border: 1px solid rgb(239 68 68 / 0.2);
  border-radius: var(--radius-sm);
  background: #fff1f2;
  color: var(--danger);
  padding: 10px 12px;
  line-height: 1.5;
}

.auth-submit {
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--brand-gradient);
  box-shadow: var(--shadow-brand);
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  padding: 12px 16px;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    opacity 0.18s ease;
}

.auth-submit:not(:disabled):hover {
  box-shadow: 0 16px 30px rgb(75 92 240 / 0.28);
  transform: translateY(-1px);
}

.auth-submit:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.auth-switch {
  margin: 18px 0 0;
  color: var(--text-muted);
}

.auth-switch a {
  color: var(--brand-primary);
  font-weight: 700;
}
</style>
