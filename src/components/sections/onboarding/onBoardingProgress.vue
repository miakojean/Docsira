<template>
    <nav
        class="tour-progress"
        role="progressbar"
        aria-label="Progression de la visite guidée"
        :aria-valuemin="1"
        :aria-valuemax="total"
        :aria-valuenow="current"
        :aria-valuetext="`Étape ${current} sur ${total}`"
    >
        <ol class="segments">
            <li
                v-for="n in total"
                :key="n"
                class="segment"
                :class="{ done: n < current, active: n === current }"
            >
                <button
                    type="button"
                    class="segment-btn"
                    :disabled="n > current || !clickable"
                    :aria-label="`Aller à l'étape ${n}`"
                    :aria-current="n === current ? 'step' : undefined"
                    @click="$emit('select', n)"
                >
                    <span class="bar"><span class="fill"></span></span>
                </button>
            </li>
        </ol>
    </nav>
</template>

<script>
export default {
  name: 'OnBoardingProgress',
  props: {
    current: { type: Number, default: 1 },   // étape courante (1 = première)
    total: { type: Number, default: 4 },
    clickable: { type: Boolean, default: true } // permet de revenir en arrière
  },
  emits: ['select']
}
</script>

<style scoped>
.tour-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 20%;
  background: none;
}

.segments {
  display: flex;
  flex: 1;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.segment {
  flex: 1;
}

.segment-btn {
  display: block;
  width: 100%;
  padding: 8px 0; /* zone de clic plus grande que la barre */
  background: #fff;
  border: none;
  cursor: pointer;
}

.segment-btn:disabled {
  cursor: default;
}

.segment-btn:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
  border-radius: 4px;
}

.bar {
  display: block;
  height: 4px;
  border-radius: 999px;
  background: none;
  overflow: hidden;
}

.fill {
  display: block;
  height: 100%;
  width: 100%;
  background: var(--primary-color);
  border-radius: inherit;
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform 0.45s cubic-bezier(0.22, 1, 0.36, 1);
}

.segment.done .fill,
.segment.active .fill {
  transform: scaleX(1);
}

.counter {
  margin: 0;
  min-width: 2.75rem;
  text-align: right;
  font-size: 0.85rem;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  color: var(--primary-black-color);
}

@media (prefers-reduced-motion: reduce) {
  .fill { transition: none; }
}
</style>