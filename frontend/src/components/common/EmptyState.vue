<script setup lang="ts">
defineProps<{
  title: string;
  description: string;
  actionText?: string;
  actionTo?: string;
  secondaryText?: string;
}>();

const emit = defineEmits<{
  (event: "action"): void;
}>();
</script>

<template>
  <section class="empty-state" aria-live="polite">
    <div class="empty-state-content">
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
      <small v-if="secondaryText">{{ secondaryText }}</small>
    </div>

    <RouterLink v-if="actionText && actionTo" class="empty-state-action" :to="actionTo">
      {{ actionText }}
    </RouterLink>
    <button v-else-if="actionText" class="empty-state-action" type="button" @click="emit('action')">
      {{ actionText }}
    </button>
  </section>
</template>

<style scoped>
.empty-state {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  padding: 18px;
}

.empty-state-content {
  display: grid;
  gap: 8px;
}

.empty-state h3,
.empty-state p {
  margin: 0;
}

.empty-state h3 {
  color: #1d1f24;
  font-size: 18px;
}

.empty-state p,
.empty-state small {
  color: #667085;
  line-height: 1.6;
}

.empty-state-action {
  flex: 0 0 auto;
  width: fit-content;
  border: 0;
  border-radius: 8px;
  background: #243b99;
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  padding: 10px 14px;
  text-decoration: none;
}

@media (max-width: 760px) {
  .empty-state {
    flex-direction: column;
  }
}
</style>
