<template>
  <article class="track-card" :class="`is-${variant}`">
    <div class="track-header">
      <span class="track-meta">{{ meta }}</span>
      <span v-if="completed" class="completed-text">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="check-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
        </svg>
        Terminé
      </span>
    </div>

    <h4 class="track-title">{{ title }}</h4>
    <p class="track-desc">{{ description }}</p>

    <ul class="track-highlights">
      <li v-for="(item, idx) in highlights" :key="idx" class="highlight-row">
        <span class="row-bullet"></span>
        <span>{{ item }}</span>
      </li>
    </ul>

    <div class="track-footer">
      <button
        type="button"
        class="track-cta"
        :class="`is-${variant}`"
        @click="$emit('start')"
      >
        <span>{{ ctaLabel }}</span>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="cta-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
        </svg>
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string;
    meta: string;
    description: string;
    highlights: string[];
    completed?: boolean;
    variant?: 'primary' | 'secondary';
    ctaLabel?: string;
  }>(),
  {
    completed: false,
    variant: 'primary',
    ctaLabel: 'Lancer le tutoriel',
  }
);

defineEmits<{
  (e: 'start'): void;
}>();
</script>

<style scoped>
.track-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.3rem 1.35rem;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.track-card.is-primary {
  border-color: #dbeafe;
}

.track-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
}

.track-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.track-meta {
  font-size: 0.76rem;
  font-weight: 500;
  color: #64748b;
}

.completed-text {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.76rem;
  font-weight: 500;
  color: #0f766e;
}

.check-icon {
  width: 13px;
  height: 13px;
}

.track-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--blues-color, #002945);
  text-align: left;
}

.track-desc {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.5;
  color: #475569;
  text-align: left;
}

.track-highlights {
  margin: 0.2rem 0 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.highlight-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #334155;
}

.row-bullet {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #94a3b8;
  flex-shrink: 0;
}

.track-footer {
  margin-top: auto;
  padding-top: 0.55rem;
}

.track-cta {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.55rem 0.9rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}

.track-cta.is-primary {
  border: 1px solid rgba(0, 87, 146, 0.22);
  background: rgba(0, 87, 146, 0.09);
  color: var(--primary-color, #005792);
}

.track-cta.is-primary:hover {
  background: rgba(0, 87, 146, 0.15);
  border-color: rgba(0, 87, 146, 0.34);
}

.track-cta.is-secondary {
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #334155;
}

.track-cta.is-secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.cta-icon {
  width: 15px;
  height: 15px;
}
</style>
