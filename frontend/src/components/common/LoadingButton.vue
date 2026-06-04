<script setup lang="ts">
withDefaults(
  defineProps<{
    loading: boolean;
    disabled?: boolean;
    loadingText: string;
    type?: "button" | "submit";
  }>(),
  {
    disabled: false,
    type: "button"
  }
);

const emit = defineEmits<{
  (event: "click", payload: MouseEvent): void;
}>();
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :aria-busy="loading"
    @click="emit('click', $event)"
  >
    {{ loading ? loadingText : "" }}
    <slot v-if="!loading" />
  </button>
</template>
