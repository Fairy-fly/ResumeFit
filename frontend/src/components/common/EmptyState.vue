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
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: var(--shadow-xs);
  padding: 20px;
}

.empty-state::before {
  flex: 0 0 auto;
  width: 10px;
  min-height: 52px;
  border-radius: 999px;
  background: var(--brand-gradient);
  content: "";
}

.empty-state-content {
  display: grid;
  gap: 8px;
  flex: 1;
}

.empty-state h3,
.empty-state p {
  margin: 0;
}

.empty-state h3 {
  color: var(--text-primary);
  font-size: 18px;
}

.empty-state p,
.empty-state small {
  color: var(--text-muted);
  line-height: 1.6;
}

.empty-state-action {
  flex: 0 0 auto;
  width: fit-content;
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--brand-gradient);
  box-shadow: var(--shadow-brand);
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  padding: 10px 14px;
  text-decoration: none;
  transition:
    box-shadow 0.18s ease,
    transform 0.18s ease;
}

.empty-state-action:hover {
  box-shadow: 0 14px 26px rgb(75 92 240 / 0.24);
  transform: translateY(-1px);
}

@media (max-width: 760px) {
  .empty-state {
    flex-direction: column;
  }

  .empty-state::before {
    width: 56px;
    min-height: 8px;
  }
}
</style>
