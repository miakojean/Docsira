<template>
  <div
    class="logo-loader-wrapper"
    :class="[
      `logo-loader--${ normalizedSize }`,
      { 'logo-loader--inline': inline, 'logo-loader--with-label': !!label }
    ]"
    role="status"
    :aria-label="label || 'Chargement en cours'"
  >
    <div class="logo-loader-stage" :style="customSizeStyle">
      <!-- Halo d'ambiance immersif (visible sur tailles md/lg/xl) -->
      <div v-if="!inline && normalizedSize !== 'xs' && normalizedSize !== 'sm'" class="logo-loader-aura"></div>

      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="110 75 400 370"
        fill="none"
        class="logo-loader-svg"
      >
        <defs>
          <filter :id="`cyan-glow-${uid}`" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <linearGradient :id="`back-folder-grad-${uid}`" x1="161" y1="95" x2="458" y2="210" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#3684f7" />
            <stop offset="100%" stop-color="#2572eb" />
          </linearGradient>

          <linearGradient :id="`mid-flap-grad-${uid}`" x1="215" y1="188" x2="492" y2="298" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#317ff4" />
            <stop offset="100%" stop-color="#2673ec" />
          </linearGradient>

          <linearGradient :id="`navy-grad-${uid}`" x1="127" y1="188" x2="378" y2="422" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#10397e" />
            <stop offset="100%" stop-color="#0a2b61" />
          </linearGradient>

          <linearGradient :id="`card-grad-${uid}`" x1="264" y1="280" x2="492" y2="422" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#96ccff" />
            <stop offset="100%" stop-color="#82bffc" />
          </linearGradient>
        </defs>

        <!-- 1. Dossier arrière (Bleu moyen) -->
        <g class="anim-back-folder">
          <path
            d="M 161 121 A 26 26 0 0 1 187 95 L 268 95 C 285 95 294 130 314 130 L 432 130 A 26 26 0 0 1 458 156 L 458 215 L 161 215 Z"
            :fill="`url(#back-folder-grad-${uid})`"
          />
          <circle class="anim-top-dot" cx="201" cy="146" r="5.5" fill="#68a4f7" />
          <rect class="anim-top-pill" x="218" y="141" width="46" height="10" rx="5" fill="#68a4f7" />
          <!-- Feuille de document supérieure qui coulisse avec fluidité -->
          <rect class="anim-top-sheet" x="195" y="165" width="228" height="46" rx="18" fill="#91c8ff" />
        </g>

        <!-- 2. Volet intermédiaire droit (Bleu moyen) -->
        <g class="anim-mid-flap">
          <path
            d="M 215 188 L 466 188 A 26 26 0 0 1 492 214 L 492 272 A 26 26 0 0 1 466 298 L 215 298 Z"
            :fill="`url(#mid-flap-grad-${uid})`"
          />
          <!-- Indicateur lumineux cyan à droite -->
          <g :filter="`url(#cyan-glow-${uid})`">
            <circle class="anim-cyan-dot" cx="397" cy="234.5" r="5.5" fill="#5df2de" />
            <rect class="anim-cyan-pill" x="413" y="229.5" width="46" height="10" rx="5" fill="#5df2de" />
          </g>
        </g>

        <!-- 3. Onglet supérieur du dossier bleu nuit + Intercalaire bleu clair gauche -->
        <g class="anim-navy-group">
          <path
            d="M 127 214 A 26 26 0 0 1 153 188 L 230 188 A 14 14 0 0 1 244 202 L 244 252 L 127 252 Z"
            :fill="`url(#navy-grad-${uid})`"
          />
          <!-- Intercalaire bleu clair qui respire -->
          <path
            class="anim-left-tab"
            d="M 161 231 A 14 14 0 0 1 175 217 L 234 217 C 247 217 251 241 266 241 L 266 255 L 161 255 Z"
            fill="#91c8ff"
          />

          <!-- 4. Corps principal du dossier avant-gauche (Bleu nuit profond) -->
          <path
            d="M 127 241 L 354 241 A 24 24 0 0 1 378 265 L 378 422 L 153 422 A 26 26 0 0 1 127 396 Z"
            :fill="`url(#navy-grad-${uid})`"
          />

          <!-- 3 points de statut animés en vague -->
          <circle class="anim-status-dot anim-status-dot--1" cx="166" cy="276.5" r="5.5" fill="#367ef4" />
          <circle
            class="anim-status-dot anim-status-dot--2"
            cx="189"
            cy="276.5"
            r="5.5"
            fill="#5ef2e0"
            :filter="`url(#cyan-glow-${uid})`"
          />
          <circle
            class="anim-status-dot anim-status-dot--3"
            cx="211.5"
            cy="276.5"
            r="5.5"
            fill="#5ef2e0"
            :filter="`url(#cyan-glow-${uid})`"
          />
        </g>

        <!-- 5. Carte avant-droite (Bleu ciel) -->
        <g class="anim-front-card">
          <path
            d="M 264 322 A 24 24 0 0 1 288 298 L 466 298 A 26 26 0 0 0 492 272 L 492 396 A 26 26 0 0 1 466 422 L 290 422 A 26 26 0 0 1 264 396 Z"
            :fill="`url(#card-grad-${uid})`"
          />
          <!-- Point bleu et barre de progression fluide -->
          <circle class="anim-card-dot" cx="305" cy="333.5" r="5.5" fill="#3180f8" />
          <rect class="anim-card-pill-track" x="321" y="328.5" width="88" height="10" rx="5" fill="#b4dcff" />
          <rect class="anim-card-pill" x="321" y="328.5" width="88" height="10" rx="5" fill="#e2f2ff" />
        </g>
      </svg>
    </div>

    <p v-if="label" class="logo-loader-label">{{ label }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number;
    label?: string;
    inline?: boolean;
  }>(),
  {
    size: 'md',
    label: '',
    inline: false,
  }
);

const uid = Math.random().toString(36).substring(2, 9);

const normalizedSize = computed(() => {
  if (typeof props.size === 'number') return 'custom';
  return props.size;
});

const customSizeStyle = computed(() => {
  if (typeof props.size === 'number') {
    return {
      width: `${props.size}px`,
      height: `${props.size}px`,
    };
  }
  return {};
});
</script>

<style scoped>
.logo-loader-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  user-select: none;
}

.logo-loader--inline {
  display: inline-flex;
  flex-direction: row;
  vertical-align: middle;
  gap: 0.45rem;
}

.logo-loader-stage {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Tailles prédéfinies */
.logo-loader--xs .logo-loader-stage {
  width: 20px;
  height: 20px;
}

.logo-loader--sm .logo-loader-stage {
  width: 26px;
  height: 26px;
}

.logo-loader--md .logo-loader-stage {
  width: 60px;
  height: 60px;
}

.logo-loader--lg .logo-loader-stage {
  width: 88px;
  height: 88px;
}

.logo-loader--xl .logo-loader-stage {
  width: 120px;
  height: 120px;
}

/* Halo immersif derrière le logo */
.logo-loader-aura {
  position: absolute;
  inset: 8%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(43, 122, 241, 0.22) 0%, rgba(93, 242, 222, 0.1) 45%, transparent 72%);
  filter: blur(8px);
  animation: aura-pulse 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  pointer-events: none;
}

.logo-loader-svg {
  width: 100%;
  height: 100%;
  overflow: visible;
  animation: logo-levitate 2.4s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
  filter: drop-shadow(0 4px 10px rgba(12, 48, 108, 0.14));
}

.logo-loader--xs .logo-loader-svg,
.logo-loader--sm .logo-loader-svg {
  filter: drop-shadow(0 1px 3px rgba(12, 48, 108, 0.18));
}

/* Animations des couches du dossier */
.anim-back-folder {
  animation: back-folder-wave 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  transform-origin: center;
}

.anim-top-sheet {
  animation: top-sheet-slide 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.anim-top-pill {
  animation: top-pill-breathe 2.4s ease-in-out infinite;
  transform-box: fill-box;
  transform-origin: left center;
}

.anim-mid-flap {
  animation: mid-flap-wave 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.anim-cyan-dot {
  animation: cyan-dot-pulse 1.6s ease-in-out infinite;
  transform-box: fill-box;
  transform-origin: center;
}

.anim-cyan-pill {
  animation: cyan-pill-shimmer 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  transform-box: fill-box;
  transform-origin: left center;
}

.anim-left-tab {
  animation: left-tab-peek 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.anim-navy-group {
  animation: navy-folder-wave 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

/* Les 3 points de statut dans le dossier bleu nuit */
.anim-status-dot {
  transform-box: fill-box;
  transform-origin: center;
  animation: status-dot-bounce 1.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.anim-status-dot--1 {
  animation-delay: 0s;
}

.anim-status-dot--2 {
  animation-delay: 0.22s;
}

.anim-status-dot--3 {
  animation-delay: 0.44s;
}

/* Carte avant-droite et sa barre de progression */
.anim-front-card {
  animation: front-card-wave 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.anim-card-dot {
  transform-box: fill-box;
  transform-origin: center;
  animation: card-dot-pulse 1.8s ease-in-out infinite;
}

.anim-card-pill {
  transform-box: fill-box;
  transform-origin: left center;
  animation: card-pill-progress 2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.logo-loader-label {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 500;
  color: #4b5563;
  letter-spacing: 0.01em;
  animation: label-fade 2s ease-in-out infinite;
}

.logo-loader--inline .logo-loader-label {
  font-size: inherit;
  color: inherit;
}

/* Keyframes */
@keyframes logo-levitate {
  0%, 100% {
    transform: translateY(0px) scale(1);
  }
  50% {
    transform: translateY(-4px) scale(1.015);
  }
}

@keyframes aura-pulse {
  0%, 100% {
    transform: scale(0.92);
    opacity: 0.65;
  }
  50% {
    transform: scale(1.12);
    opacity: 1;
  }
}

@keyframes back-folder-wave {
  0%, 100% {
    transform: translateY(0px);
  }
  40% {
    transform: translateY(-8px);
  }
}

@keyframes top-sheet-slide {
  0%, 100% {
    transform: translateY(0px);
  }
  45% {
    transform: translateY(-7px);
  }
}

@keyframes top-pill-breathe {
  0%, 100% {
    transform: scaleX(1);
    opacity: 0.85;
  }
  50% {
    transform: scaleX(1.22);
    opacity: 1;
  }
}

@keyframes mid-flap-wave {
  0%, 100% {
    transform: translate(0px, 0px);
  }
  50% {
    transform: translate(3px, -3px);
  }
}

@keyframes cyan-dot-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.85;
  }
  50% {
    transform: scale(1.28);
    opacity: 1;
  }
}

@keyframes cyan-pill-shimmer {
  0%, 100% {
    transform: scaleX(1);
    opacity: 0.88;
  }
  50% {
    transform: scaleX(0.68);
    opacity: 1;
  }
}

@keyframes left-tab-peek {
  0%, 100% {
    transform: translateY(0px);
  }
  55% {
    transform: translateY(-6px);
  }
}

@keyframes navy-folder-wave {
  0%, 100% {
    transform: translate(0px, 0px);
  }
  50% {
    transform: translate(-2px, 2px);
  }
}

@keyframes status-dot-bounce {
  0%, 80%, 100% {
    transform: scale(1) translateY(0);
    opacity: 0.75;
  }
  40% {
    transform: scale(1.38) translateY(-4px);
    opacity: 1;
  }
}

@keyframes front-card-wave {
  0%, 100% {
    transform: translate(0px, 0px);
  }
  50% {
    transform: translate(4px, 3px);
  }
}

@keyframes card-dot-pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.25);
  }
}

@keyframes card-pill-progress {
  0% {
    transform: scaleX(0.25);
    opacity: 0.7;
  }
  50% {
    transform: scaleX(1);
    opacity: 1;
  }
  100% {
    transform: scaleX(0.25);
    opacity: 0.7;
  }
}

@keyframes label-fade {
  0%, 100% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
}
</style>

