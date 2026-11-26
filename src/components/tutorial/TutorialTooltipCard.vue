<template>
  <div
    ref="cardRef"
    class="tooltip-card"
    :class="{ 'is-docked': docked }"
    :style="cardStyle"
    role="dialog"
    aria-modal="false"
    aria-labelledby="tutorial-step-title"
  >
    <div class="card-header">
      <span class="step-counter">{{ counterLabel }}</span>
      <button type="button" class="skip-btn" @click="$emit('skip')">
        Passer
      </button>
    </div>

    <h3 id="tutorial-step-title" class="step-title">{{ step.title }}</h3>
    <p class="step-desc">{{ step.description }}</p>

    <TutorialActionPrompt
      v-if="step.actionHint"
      :hint="step.actionHint"
      :completedHint="step.completedHint"
      :satisfied="isSatisfied"
      :hasRequiredAction="Boolean(step.requiredAction)"
    />

    <TutorialStepProgress :current="currentIndex" :total="totalSteps" />

    <div class="card-footer">
      <button
        type="button"
        class="btn-prev"
        :disabled="isFirst"
        @click="$emit('prev')"
      >
        Précédent
      </button>

      <div class="footer-right">
        <button
          v-if="track === 'basic' && isLast"
          type="button"
          class="btn-support"
          @click="$emit('openSupport')"
        >
          Aller dans Support
        </button>

        <button
          type="button"
          class="btn-next"
          :disabled="!canAdvance"
          @click="isLast ? $emit('finish') : $emit('next')"
        >
          {{ isLast ? 'Terminer' : 'Suivant' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import type { TutorialStep, TutorialTrack } from '../../stores/tutorialStore';
import TutorialActionPrompt from './TutorialActionPrompt.vue';
import TutorialStepProgress from './TutorialStepProgress.vue';

const props = withDefaults(
  defineProps<{
    step: TutorialStep;
    track: TutorialTrack;
    currentIndex: number;
    totalSteps: number;
    targetRect: DOMRect | null;
    isFirst: boolean;
    isLast: boolean;
    canAdvance: boolean;
    isSatisfied: boolean;
    docked?: boolean;
  }>(),
  {
    docked: false,
  }
);

const emit = defineEmits<{
  (e: 'next'): void;
  (e: 'prev'): void;
  (e: 'skip'): void;
  (e: 'finish'): void;
  (e: 'openSupport'): void;
}>();

const cardRef = ref<HTMLDivElement | null>(null);
const vw = ref(typeof window !== 'undefined' ? window.innerWidth : 1280);
const vh = ref(typeof window !== 'undefined' ? window.innerHeight : 800);
const measuredHeight = ref(240);

const counterLabel = computed(() => {
  const prefix = props.track === 'advanced' ? 'Avancé · ' : '';
  return `${prefix}${props.currentIndex + 1} / ${props.totalSteps}`;
});

function updateDimensions() {
  vw.value = window.innerWidth;
  vh.value = window.innerHeight;
  if (cardRef.value) {
    measuredHeight.value = cardRef.value.offsetHeight || 240;
  }
}

watch(
  () => [props.step.id, props.targetRect, props.docked, props.isSatisfied],
  async () => {
    await nextTick();
    updateDimensions();
  },
  { immediate: true }
);

const cardStyle = computed<Record<string, string>>(() => {
  const margin = 16;

  if (props.docked) {
    const dockedWidth = Math.min(300, vw.value - margin * 2);
    return {
      width: `${dockedWidth}px`,
      right: `${margin}px`,
      bottom: `${margin}px`,
      top: 'auto',
      left: 'auto',
    };
  }

  const cardWidth = Math.min(330, vw.value - margin * 2);
  const cardHeight = Math.min(measuredHeight.value, vh.value - margin * 2);

  if (!props.targetRect || vw.value < 768) {
    return {
      width: `${cardWidth}px`,
      right: `${margin}px`,
      bottom: `${margin}px`,
      top: 'auto',
      left: 'auto',
    };
  }

  const rect = props.targetRect;
  const gap = 14;
  let top = rect.top;
  let left = rect.right + gap;

  if (left + cardWidth > vw.value - margin) {
    left = rect.left - cardWidth - gap;
  }

  if (left < margin) {
    left = Math.max(margin, Math.min(rect.left, vw.value - cardWidth - margin));
    const spaceBelow = vh.value - rect.bottom - margin;
    const spaceAbove = rect.top - margin;
    if (spaceBelow >= cardHeight + gap || spaceBelow >= spaceAbove) {
      top = rect.bottom + gap;
    } else {
      top = rect.top - cardHeight - gap;
    }
  }

  left = Math.max(margin, Math.min(left, vw.value - cardWidth - margin));
  top = Math.max(margin, Math.min(top, vh.value - cardHeight - margin));

  return {
    width: `${cardWidth}px`,
    top: `${Math.round(top)}px`,
    left: `${Math.round(left)}px`,
    right: 'auto',
    bottom: 'auto',
  };
});

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    if (props.docked) return;
    event.preventDefault();
    emit('skip');
  } else if (event.key === 'ArrowRight') {
    if (!props.canAdvance) return;
    event.preventDefault();
    if (props.isLast) emit('finish');
    else emit('next');
  } else if (event.key === 'ArrowLeft' && !props.isFirst) {
    event.preventDefault();
    emit('prev');
  }
}

onMounted(() => {
  updateDimensions();
  window.addEventListener('resize', updateDimensions);
  window.addEventListener('keydown', onKeydown);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateDimensions);
  window.removeEventListener('keydown', onKeydown);
});
</script>

<style scoped>
.tooltip-card {
  position: fixed;
  z-index: 12000;
  max-height: calc(100vh - 32px);
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.14);
  padding: 0.95rem 1.05rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  transition: top 0.2s cubic-bezier(0.16, 1, 0.3, 1), left 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.step-counter {
  font-size: 0.74rem;
  font-weight: 500;
  color: #64748b;
}

.skip-btn {
  padding: 0.22rem 0.5rem;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  color: #64748b;
  font-size: 0.76rem;
  font-weight: 500;
  cursor: pointer;
}

.skip-btn:hover {
  background: #f8fafc;
  color: #0f172a;
}

.step-title {
  margin: 0;
  font-size: 0.98rem;
  font-weight: 600;
  color: var(--blues-color, #002945);
  text-align: left;
  line-height: 1.3;
}

.step-desc {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.5;
  color: #475569;
  text-align: left;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.45rem;
  padding-top: 0.25rem;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-prev,
.btn-support,
.btn-next {
  padding: 0.42rem 0.78rem;
  border-radius: 7px;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.btn-prev {
  border: 1px solid transparent;
  background: transparent;
  color: #64748b;
}

.btn-prev:hover:not(:disabled) {
  background: #f8fafc;
  color: #0f172a;
}

.btn-prev:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-support {
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
}

.btn-support:hover {
  background: #f8fafc;
  border-color: #94a3b8;
}

.btn-next {
  border: 1px solid rgba(0, 87, 146, 0.22);
  background: rgba(0, 87, 146, 0.09);
  color: var(--primary-color, #005792);
}

.btn-next:hover:not(:disabled) {
  background: rgba(0, 87, 146, 0.15);
  border-color: rgba(0, 87, 146, 0.34);
}

.btn-next:disabled {
  border-color: #e2e8f0;
  background: #f8fafc;
  color: #94a3b8;
  cursor: not-allowed;
}
</style>
