<template>
  <div
    class="action-prompt"
    :class="{ 'is-satisfied': satisfied, 'is-pending': hasRequiredAction && !satisfied }"
  >
    <span v-if="satisfied && hasRequiredAction" class="prompt-icon is-done" aria-hidden="true">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.2" stroke="currentColor" class="icon-svg">
        <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
      </svg>
    </span>
    <span v-else-if="hasRequiredAction" class="prompt-dot" aria-hidden="true"></span>

    <span class="prompt-text">
      {{ satisfied && hasRequiredAction ? (completedHint || 'Étape validée') : hint }}
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  hint: string;
  completedHint?: string;
  satisfied: boolean;
  hasRequiredAction: boolean;
}>();
</script>

<style scoped>
.action-prompt {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.65rem;
  border-left: 2px solid #cbd5e1;
  background: #f8fafc;
  border-radius: 0 6px 6px 0;
  font-size: 0.78rem;
  line-height: 1.4;
  color: #475569;
  transition: border-color 0.2s ease, background-color 0.2s ease, color 0.2s ease;
}

.action-prompt.is-pending {
  border-left-color: var(--primary-color, #005792);
  color: #1e293b;
}

.action-prompt.is-satisfied {
  border-left-color: #0f766e;
  background: #f0fdfa;
  color: #0f766e;
}

.prompt-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--primary-color, #005792);
  flex-shrink: 0;
  animation: pulseDot 1.8s ease-in-out infinite;
}

.prompt-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.prompt-icon.is-done {
  color: #0f766e;
}

.icon-svg {
  width: 14px;
  height: 14px;
}

.prompt-text {
  font-weight: 500;
}

@keyframes pulseDot {
  0%,
  100% {
    opacity: 0.45;
    transform: scale(0.9);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .prompt-dot {
    animation: none;
  }
}
</style>

