<template>
  <div
    class="progress-bar-track"
    role="progressbar"
    :aria-valuenow="current + 1"
    :aria-valuemin="1"
    :aria-valuemax="total"
  >
    <div class="progress-bar-fill" :style="{ width: `${percent}%` }"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  current: number;
  total: number;
}>();

const percent = computed(() => {
  if (props.total <= 0) return 0;
  return Math.min(100, Math.max(0, Math.round(((props.current + 1) / props.total) * 100)));
});
</script>

<style scoped>
.progress-bar-track {
  width: 100%;
  height: 3px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--primary-color, #005792);
  transition: width 0.22s ease;
}
</style>
