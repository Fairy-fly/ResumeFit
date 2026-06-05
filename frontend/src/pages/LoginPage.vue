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
    <div class="auth-panel">
      <p class="auth-eyebrow">ResumeFit V0.3</p>
      <h1 id="login-title">登录账号</h1>
      <p class="auth-description">登录后可以进入 ResumeFit 工作台，后续多用户数据隔离会基于当前账号完成。</p>

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
  min-height: calc(100vh - 64px);
  place-items: center;
}

.auth-panel {
  width: min(100%, 440px);
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  padding: 28px;
}

.auth-eyebrow {
  margin: 0 0 8px;
  color: #4f5a72;
  font-size: 13px;
  font-weight: 700;
}

h1 {
  margin: 0;
  font-size: 28px;
}

.auth-description {
  margin: 10px 0 22px;
  color: #5d6472;
  line-height: 1.6;
}

.auth-form {
  display: grid;
  gap: 16px;
}

label {
  display: grid;
  gap: 8px;
  font-weight: 700;
}

input {
  width: 100%;
  border: 1px solid #cfd3dc;
  border-radius: 8px;
  padding: 11px 12px;
  font: inherit;
}

.auth-error {
  margin: 0;
  border-radius: 8px;
  background: #fff1f2;
  color: #b4232f;
  padding: 10px 12px;
  line-height: 1.5;
}

.auth-submit {
  border: 0;
  border-radius: 8px;
  background: #243b99;
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  padding: 12px 16px;
}

.auth-submit:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.auth-switch {
  margin: 18px 0 0;
  color: #5d6472;
}

.auth-switch a {
  color: #243b99;
  font-weight: 700;
}
</style>
