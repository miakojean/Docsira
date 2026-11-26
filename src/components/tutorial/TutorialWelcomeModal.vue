<template>
  <div
    class="welcome-fullscreen"
    role="dialog"
    aria-modal="true"
    aria-labelledby="welcome-tutorial-title"
  >
    <div class="welcome-center">
      <div class="welcome-logo-stage">
        <AnimatedBrandLogo :size="76" />
      </div>

      <h1 id="welcome-tutorial-title" class="welcome-title">
        {{ greetingLine }}
      </h1>

      <p class="welcome-subtitle">
        Votre espace est prêt pour centraliser vos clients, organiser vos dossiers et collaborer avec votre cabinet.
      </p>

      <div class="welcome-actions">
        <button type="button" class="btn-skip-tour" @click="$emit('skip')">
          Passer
        </button>

        <button type="button" class="btn-start-tour" @click="$emit('start')">
          Commencer
        </button>
      </div>

      <p class="welcome-footer-note">
        Accessible à tout moment depuis Support client.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AnimatedBrandLogo from './AnimatedBrandLogo.vue';

const props = withDefaults(
  defineProps<{
    userName?: string;
  }>(),
  {
    userName: '',
  }
);

defineEmits<{
  (e: 'start'): void;
  (e: 'skip'): void;
}>();

const greetingLine = computed(() => {
  const clean = props.userName.trim();
  if (clean) {
    return `Bienvenue sur DocSira, ${clean}`;
  }
  return 'Bienvenue sur DocSira';
});
</script>

<style scoped>
.welcome-fullscreen {
  position: fixed;
  inset: 0;
  z-index: 10050;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.welcome-center {
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.welcome-logo-stage {
  margin-bottom: 1rem;
  opacity: 0;
  animation: welcomeFadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) 0.05s forwards;
}

.welcome-title {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: -0.01em;
  color: var(--blues-color, #002945);
  text-align: center;
  opacity: 0;
  animation: welcomeFadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.3s forwards;
}

.welcome-subtitle {
  margin: 0.7rem 0 1.65rem;
  font-size: 0.9rem;
  line-height: 1.55;
  color: #64748b;
  max-width: 370px;
  text-align: center;
  opacity: 0;
  animation: welcomeFadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.55s forwards;
}

.welcome-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  opacity: 0;
  animation: welcomeFadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) 0.85s forwards;
}

.btn-skip-tour {
  padding: 0.5rem 0.95rem;
  border-radius: 8px;
  border: 1px solid transparent;
  background: transparent;
  color: #64748b;
  font-size: 0.84rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.btn-skip-tour:hover {
  background: #f8fafc;
  color: #334155;
}

.btn-start-tour {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.15rem;
  border-radius: 8px;
  border: 1px solid rgba(0, 87, 146, 0.22);
  background: rgba(0, 87, 146, 0.08);
  color: var(--primary-color, #005792);
  font-size: 0.84rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}

.btn-start-tour:hover {
  background: rgba(0, 87, 146, 0.14);
  border-color: rgba(0, 87, 146, 0.35);
}

.welcome-footer-note {
  margin: 1.25rem 0 0;
  font-size: 0.74rem;
  line-height: 1.4;
  color: #94a3b8;
  text-align: center;
  opacity: 0;
  animation: welcomeFadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) 1.05s forwards;
}

@keyframes welcomeFadeUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .welcome-logo-stage,
  .welcome-title,
  .welcome-subtitle,
  .welcome-actions,
  .welcome-footer-note {
    opacity: 1;
    animation: none;
  }
}
</style>
