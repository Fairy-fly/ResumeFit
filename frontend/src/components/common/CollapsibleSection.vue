<script setup lang="ts">
import { computed, ref, watch } from "vue";

const props = withDefaults(
  defineProps<{
    title: string;
    count?: number | string | null;
    defaultOpen?: boolean;
    modelValue?: boolean;
  }>(),
  {
    count: null,
    defaultOpen: false,
    modelValue: undefined
  }
);

const emit = defineEmits<{
  (event: "update:modelValue", value: boolean): void;
}>();

const internalOpen = ref(props.defaultOpen);
const isControlled = computed(() => props.modelValue !== undefined);
const isOpen = computed({
  get: () => props.modelValue ?? internalOpen.value,
  set: (value: boolean) => {
    internalOpen.value = value;
    emit("update:modelValue", value);
  }
});

const hasCount = computed(() => props.count !== null && props.count !== undefined);

watch(
  () => props.defaultOpen,
  (value) => {
    if (!isControlled.value) {
      internalOpen.value = value;
    }
  }
);

function toggleOpen(): void {
  isOpen.value = !isOpen.value;
}
</script>

<template>
  <section class="collapsible-section">
    <div class="collapsible-header">
      <button
        class="collapsible-toggle"
        type="button"
        :aria-expanded="isOpen"
        @click="toggleOpen"
      >
        <span class="collapsible-title">
          {{ title }}
          <span v-if="hasCount" class="collapsible-count">· {{ count }}</span>
        </span>
        <span class="collapsible-state">{{ isOpen ? "收起" : "展开" }}</span>
      </button>
      <div v-if="$slots.actions" class="collapsible-actions">
        <slot name="actions" />
      </div>
    </div>

    <div v-if="isOpen" class="collapsible-content">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.collapsible-section {
  display: grid;
  gap: 14px;
  min-width: 0;
}

.collapsible-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.collapsible-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  min-width: 0;
  border: 1px solid rgb(75 92 240 / 0.16);
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #eef2ff, #f7faff);
  color: var(--brand-primary);
  cursor: pointer;
  font: inherit;
  font-weight: 800;
  padding: 10px 12px;
  text-align: left;
  transition:
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    transform 0.18s ease;
}

.collapsible-toggle:hover {
  border-color: rgb(75 92 240 / 0.28);
  box-shadow: var(--shadow-xs);
  transform: translateY(-1px);
}

.collapsible-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.collapsible-count {
  color: var(--text-muted);
  font-weight: 700;
}

.collapsible-state {
  flex: 0 0 auto;
  border-radius: 999px;
  background: rgb(255 255 255 / 0.72);
  color: var(--brand-primary);
  font-size: 13px;
  font-weight: 800;
  padding: 4px 8px;
}

.collapsible-actions {
  display: flex;
  flex: 0 0 auto;
  gap: 8px;
}

.collapsible-content {
  display: grid;
  gap: 14px;
}

@media (max-width: 760px) {
  .collapsible-header {
    align-items: stretch;
    flex-direction: column;
  }

  .collapsible-toggle {
    width: 100%;
  }
}
</style>
