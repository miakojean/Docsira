<template>
  <div v-if="active && !suspended" class="spotlight-layer" aria-hidden="true">
    <svg class="spotlight-svg" :viewBox="`0 0 ${vw} ${vh}`" preserveAspectRatio="none">
      <defs>
        <mask :id="`spotlight-mask-${uid}`">
          <rect x="0" y="0" :width="vw" :height="vh" fill="white" />
          <rect
            v-if="cutout"
            :x="cutout.x"
            :y="cutout.y"
            :width="cutout.width"
            :height="cutout.height"
            :rx="10"
            :ry="10"
            fill="black"
          />
        </mask>
      </defs>
      <rect
        x="0"
        y="0"
        :width="vw"
        :height="vh"
        fill="rgba(15, 23, 42, 0.42)"
        :mask="`url(#spotlight-mask-${uid})`"
      />
    </svg>

    <div
      v-if="cutout"
      class="spotlight-ring"
      :style="{
        top: `${cutout.y}px`,
        left: `${cutout.x}px`,
        width: `${cutout.width}px`,
        height: `${cutout.height}px`,
      }"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue';

const props = defineProps<{
  targetSelector?: string | string[];
  active: boolean;
  suspended?: boolean;
  recheckKey?: string | number;
}>();

const emit = defineEmits<{
  (e: 'targetRect', rect: DOMRect | null): void;
}>();

const uid = Math.random().toString(36).slice(2, 9);
const vw = ref(typeof window !== 'undefined' ? window.innerWidth : 1280);
const vh = ref(typeof window !== 'undefined' ? window.innerHeight : 800);
const cutout = ref<{ x: number; y: number; width: number; height: number } | null>(null);

let resizeObserver: ResizeObserver | null = null;
let retryTimer: ReturnType<typeof setTimeout> | null = null;
let settleTimer: ReturnType<typeof setTimeout> | null = null;

function clearTimers() {
  if (retryTimer) {
    clearTimeout(retryTimer);
    retryTimer = null;
  }
  if (settleTimer) {
    clearTimeout(settleTimer);
    settleTimer = null;
  }
}

function disconnectObserver() {
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
}

function findTargetElement(selector?: string | string[]): HTMLElement | null {
  if (!selector) return null;
  const candidates = Array.isArray(selector) ? selector : [selector];
  for (const sel of candidates) {
    if (!sel) continue;
    const el = document.querySelector(sel) as HTMLElement | null;
    if (el) {
      const rect = el.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0) {
        return el;
      }
    }
  }
  return null;
}

function isOutsideViewport(rect: DOMRect): boolean {
  return (
    rect.top < 0 ||
    rect.left < 0 ||
    rect.bottom > window.innerHeight ||
    rect.right > window.innerWidth
  );
}

function measureTarget(retriesLeft = 0) {
  vw.value = window.innerWidth;
  vh.value = window.innerHeight;

  if (!props.active) {
    cutout.value = null;
    emit('targetRect', null);
    return;
  }

  if (props.suspended) {
    cutout.value = null;
    return;
  }

  const el = findTargetElement(props.targetSelector);
  if (!el) {
    cutout.value = null;
    emit('targetRect', null);
    if (retriesLeft > 0) {
      if (retryTimer) clearTimeout(retryTimer);
      retryTimer = setTimeout(() => measureTarget(retriesLeft - 1), 250);
    }
    return;
  }

  let rect = el.getBoundingClientRect();
  if (isOutsideViewport(rect)) {
    el.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    rect = el.getBoundingClientRect();
  }

  const pad = 6;
  cutout.value = {
    x: Math.max(4, rect.left - pad),
    y: Math.max(4, rect.top - pad),
    width: rect.width + pad * 2,
    height: rect.height + pad * 2,
  };
  emit('targetRect', rect);

  disconnectObserver();
  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => measureTarget(0));
    resizeObserver.observe(el);
  }
}

function onViewportChange() {
  measureTarget(0);
}

watch(
  () => [props.active, props.suspended, props.targetSelector, props.recheckKey] as const,
  async () => {
    clearTimers();
    disconnectObserver();
    await nextTick();
    measureTarget(8);
    settleTimer = setTimeout(() => measureTarget(0), 150);
  },
  { immediate: true }
);

onMounted(() => {
  window.addEventListener('resize', onViewportChange);
  window.addEventListener('scroll', onViewportChange, true);
});

onUnmounted(() => {
  clearTimers();
  disconnectObserver();
  window.removeEventListener('resize', onViewportChange);
  window.removeEventListener('scroll', onViewportChange, true);
});
</script>

<style scoped>
.spotlight-layer {
  position: fixed;
  inset: 0;
  z-index: 9000;
  pointer-events: none;
}

.spotlight-svg {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  display: block;
  pointer-events: none;
}

.spotlight-ring {
  position: fixed;
  border-radius: 10px;
  border: 2px solid #2563eb;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.22);
  pointer-events: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  animation: spotlightPulse 2s ease-in-out infinite;
}

@keyframes spotlightPulse {
  0%,
  100% {
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.18);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(37, 99, 235, 0.28);
  }
}

@media (prefers-reduced-motion: reduce) {
  .spotlight-ring {
    animation: none;
  }
}
</style>
