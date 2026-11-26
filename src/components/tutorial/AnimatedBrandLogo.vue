<template>
  <div
    class="animated-brand-logo"
    :style="{ width: `${size}px`, height: `${size}px` }"
    aria-hidden="true"
  >
    <div class="brand-glow"></div>
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="110 75 400 370"
      fill="none"
      class="brand-svg"
    >
      <defs>
        <filter :id="`brand-cyan-glow-${uid}`" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="4.5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <!-- 1. Dossier arrière (Bleu moyen) -->
      <g class="layer-back-folder">
        <path
          d="M 161 121 A 26 26 0 0 1 187 95 L 268 95 C 285 95 294 130 314 130 L 432 130 A 26 26 0 0 1 458 156 L 458 210 L 161 210 Z"
          fill="#2b7af1"
        />
        <circle cx="201" cy="146" r="5.5" fill="#68a4f7" />
        <rect x="218" y="141" width="46" height="10" rx="5" fill="#68a4f7" />
        <rect class="layer-doc-sheet" x="195" y="165" width="228" height="42" rx="18" fill="#91c8ff" />
      </g>

      <!-- 2. Volet intermédiaire droit (Bleu moyen) -->
      <g class="layer-mid-flap">
        <path
          d="M 215 188 L 466 188 A 26 26 0 0 1 492 214 L 492 272 A 26 26 0 0 1 466 298 L 215 298 Z"
          fill="#2b7af1"
        />
        <g class="layer-cyan-pulse" :filter="`url(#brand-cyan-glow-${uid})`">
          <circle cx="397" cy="234.5" r="5.5" fill="#5df2de" />
          <rect x="413" y="229.5" width="46" height="10" rx="5" fill="#5df2de" />
        </g>
      </g>

      <!-- 3. Onglet supérieur bleu nuit + intercalaire bleu clair -->
      <g class="layer-navy-tab">
        <path
          d="M 127 214 A 26 26 0 0 1 153 188 L 230 188 A 14 14 0 0 1 244 202 L 244 250 L 127 250 Z"
          fill="#0c306c"
        />
        <path
          d="M 161 231 A 14 14 0 0 1 175 217 L 234 217 C 247 217 251 241 266 241 L 266 252 L 161 252 Z"
          fill="#91c8ff"
        />
      </g>

      <!-- 4. Dossier principal avant-gauche (Bleu nuit profond) -->
      <g class="layer-navy-body">
        <path
          d="M 127 241 L 354 241 A 24 24 0 0 1 378 265 L 378 422 L 153 422 A 26 26 0 0 1 127 396 Z"
          fill="#0c306c"
        />
        <circle cx="166" cy="276.5" r="5.5" fill="#367ef4" />
        <circle class="layer-cyan-pulse" cx="189" cy="276.5" r="5.5" fill="#5ef2e0" :filter="`url(#brand-cyan-glow-${uid})`" />
        <circle class="layer-cyan-pulse delay" cx="211.5" cy="276.5" r="5.5" fill="#5ef2e0" :filter="`url(#brand-cyan-glow-${uid})`" />
      </g>

      <!-- 5. Carte avant-droite (Bleu ciel) -->
      <g class="layer-front-card">
        <path
          d="M 264 322 A 24 24 0 0 1 288 298 L 466 298 A 26 26 0 0 0 492 272 L 492 396 A 26 26 0 0 1 466 422 L 290 422 A 26 26 0 0 1 264 396 Z"
          fill="#8ac5fd"
        />
        <circle cx="305" cy="333.5" r="5.5" fill="#3180f8" />
        <rect x="321" y="328.5" width="88" height="10" rx="5" fill="#d2e9ff" />
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: number;
  }>(),
  {
    size: 96,
  }
);

const uid = Math.random().toString(36).slice(2, 9);
</script>

<style scoped>
.animated-brand-logo {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  user-select: none;
}

.brand-glow {
  position: absolute;
  inset: 14%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(43, 122, 241, 0.13) 0%, rgba(93, 242, 222, 0.05) 55%, transparent 75%);
  filter: blur(10px);
  animation: brandGlowPulse 4.5s ease-in-out infinite;
  pointer-events: none;
}

.brand-svg {
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1;
  animation: brandFloat 4.5s ease-in-out infinite;
  filter: drop-shadow(0 6px 12px rgba(12, 48, 108, 0.1));
}

.layer-doc-sheet {
  animation: docBreathe 4.5s ease-in-out infinite;
}

.layer-front-card {
  animation: frontCardShift 4.5s ease-in-out infinite;
}

.layer-cyan-pulse {
  animation: cyanSoftPulse 3s ease-in-out infinite;
}

.layer-cyan-pulse.delay {
  animation-delay: 0.45s;
}

@keyframes brandFloat {
  0%,
  100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-5px);
  }
}

@keyframes docBreathe {
  0%,
  100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-4px);
  }
}

@keyframes frontCardShift {
  0%,
  100% {
    transform: translate(0px, 0px);
  }
  50% {
    transform: translate(2px, -2px);
  }
}

@keyframes cyanSoftPulse {
  0%,
  100% {
    opacity: 0.85;
  }
  50% {
    opacity: 1;
  }
}

@keyframes brandGlowPulse {
  0%,
  100% {
    transform: scale(0.95);
    opacity: 0.7;
  }
  50% {
    transform: scale(1.08);
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .brand-glow,
  .brand-svg,
  .layer-doc-sheet,
  .layer-front-card,
  .layer-cyan-pulse {
    animation: none;
  }
}
</style>

