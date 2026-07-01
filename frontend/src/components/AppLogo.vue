<script setup lang="ts">
withDefaults(
  defineProps<{
    compact?: boolean;
  }>(),
  {
    compact: false
  }
);
</script>

<template>
  <span class="app-logo" :class="{ compact }" aria-hidden="true">
    <svg viewBox="0 0 48 48" role="img">
      <rect x="7" y="5" width="28" height="36" rx="6" fill="url(#paperGradient)" />
      <path d="M15 16h12M15 23h10M15 30h8" stroke="white" stroke-width="2.6" stroke-linecap="round" />
      <circle cx="34" cy="33" r="9" fill="url(#checkGradient)" />
      <path d="m29.5 33.2 3 3.1 6.2-7" fill="none" stroke="white" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M30 11c4 1 7 4 8 8" fill="none" stroke="#2dd4bf" stroke-width="2.4" stroke-linecap="round" />
      <defs>
        <linearGradient id="paperGradient" x1="7" x2="35" y1="5" y2="41" gradientUnits="userSpaceOnUse">
          <stop stop-color="#6672f6" />
          <stop offset="1" stop-color="#4b5cf0" />
        </linearGradient>
        <linearGradient id="checkGradient" x1="25" x2="43" y1="24" y2="42" gradientUnits="userSpaceOnUse">
          <stop stop-color="#2dd4bf" />
          <stop offset="1" stop-color="#18a999" />
        </linearGradient>
      </defs>
    </svg>
    <span v-if="!compact" class="logo-initials">RF</span>
  </span>
</template>

<style scoped>
.app-logo {
  position: relative;
  display: inline-grid;
  width: 42px;
  height: 42px;
  place-items: center;
  flex: 0 0 auto;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, rgb(255 255 255 / 0.16), rgb(255 255 255 / 0.04));
  box-shadow: var(--shadow-button);
}

.app-logo svg {
  width: 38px;
  height: 38px;
}

.app-logo.compact {
  width: 38px;
  height: 38px;
}

.logo-initials {
  position: absolute;
  right: -4px;
  bottom: -3px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 16px;
  border: 1px solid rgb(255 255 255 / 0.45);
  border-radius: 999px;
  background: #0b1220;
  color: #ffffff;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: 0;
}
</style>
