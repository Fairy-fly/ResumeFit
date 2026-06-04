<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
}>();

const emit = defineEmits<{
  (event: "close"): void;
}>();
</script>

<template>
  <div class="modal-backdrop" role="presentation" @click.self="emit('close')">
    <section class="detail-modal" role="dialog" aria-modal="true" aria-labelledby="detail-modal-title">
      <header class="detail-modal-header">
        <div>
          <h2 id="detail-modal-title">{{ title }}</h2>
          <p v-if="subtitle">{{ subtitle }}</p>
        </div>
        <button class="close-button" type="button" aria-label="关闭详情弹窗" @click="emit('close')">关闭</button>
      </header>

      <div class="detail-modal-body">
        <slot />
      </div>
    </section>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  z-index: 50;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgb(18 24 38 / 0.42);
  padding: 24px;
}

.detail-modal {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  width: min(860px, 100%);
  max-height: 80vh;
  border: 1px solid #dedfe3;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 24px 70px rgb(18 24 38 / 0.24);
}

.detail-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid #edf0f4;
  padding: 18px 20px;
}

.detail-modal-header h2,
.detail-modal-header p {
  margin: 0;
}

.detail-modal-header h2 {
  color: #1d1f24;
  font-size: 22px;
}

.detail-modal-header p {
  margin-top: 6px;
  color: #667085;
  line-height: 1.5;
}

.detail-modal-body {
  overflow-y: auto;
  padding: 20px;
}

.close-button {
  flex: 0 0 auto;
  border: 0;
  border-radius: 8px;
  background: #e6e9f2;
  color: #263044;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  padding: 9px 14px;
}

@media (max-width: 760px) {
  .modal-backdrop {
    align-items: stretch;
    padding: 12px;
  }

  .detail-modal {
    max-height: calc(100vh - 24px);
  }

  .detail-modal-header {
    flex-direction: column;
  }
}
</style>
