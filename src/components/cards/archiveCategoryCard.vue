<template>
  <div
    class="archive-cat-card"
    :class="[`archive-cat-card--${variant}`, { 'is-featured': featured }]"
    role="button"
    tabindex="0"
    @click="$emit('select')"
    @keydown.enter.prevent="$emit('select')"
    @keydown.space.prevent="$emit('select')"
  >
    <!-- Bulle pastel organique avec icône -->
    <div class="archive-cat-card__blob">
      <!-- Icône Dossiers -->
      <svg
        v-if="variant === 'dossiers'"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.8"
        stroke="currentColor"
        class="archive-cat-card__icon"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h2.586a1 1 0 0 1 .707.293l1.414 1.414a1 1 0 0 0 .707.293H17a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2Z"
        />
      </svg>

      <!-- Icône Documents -->
      <svg
        v-else-if="variant === 'documents'"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.8"
        stroke="currentColor"
        class="archive-cat-card__icon"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"
        />
      </svg>

      <!-- Icône Clients -->
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.8"
        stroke="currentColor"
        class="archive-cat-card__icon"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z"
        />
      </svg>
    </div>

    <!-- Titre -->
    <h4 class="archive-cat-card__title">{{ title }}</h4>

    <!-- Description -->
    <p class="archive-cat-card__description">{{ description }}</p>

    <!-- Compteur discret en bas -->
    <div v-if="count !== undefined" class="archive-cat-card__badge">
      <span>{{ count }} {{ countLabel }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string;
    description: string;
    variant?: 'dossiers' | 'documents' | 'clients';
    count?: number;
    countLabel?: string;
    featured?: boolean;
  }>(),
  {
    variant: 'dossiers',
    count: undefined,
    countLabel: 'éléments',
    featured: false,
  }
);

defineEmits<{
  (e: 'select'): void;
}>();
</script>

<style scoped>
.archive-cat-card {
  width: 100%;
  max-width: 270px;
  min-height: 310px;
  background: #ffffff;
  border-radius: 10px;
  border: 1px solid rgba(226, 232, 240, 0.7);
  padding: 2.75rem 1.75rem 2.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.03);
  transition: transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1),
    box-shadow 0.28s ease,
    border-color 0.28s ease;
  user-select: none;
}

.archive-cat-card.is-featured {
  box-shadow: 0 22px 42px -10px rgba(42, 72, 140, 0.12);
}

.archive-cat-card:hover,
.archive-cat-card:focus-visible {
  transform: translateY(-6px);
  box-shadow: 0 24px 44px -10px rgba(42, 72, 140, 0.16);
  border-color: rgba(0, 87, 146, 0.18);
  outline: none;
}

/* Bulle organique douce (style maquette) */
.archive-cat-card__blob {
  width: 84px;
  height: 84px;
  border-radius: 48% 52% 55% 45% / 54% 46% 54% 46%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.65rem;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), border-radius 0.4s ease;
}

.archive-cat-card:hover .archive-cat-card__blob {
  transform: scale(1.07);
  border-radius: 53% 47% 46% 54% / 47% 54% 46% 53%;
}

/* Variantes de couleurs fidèles à l'image */
.archive-cat-card--dossiers .archive-cat-card__blob {
  background-color: #eef4ff;
  color: #3168c4;
}

.archive-cat-card--documents .archive-cat-card__blob {
  background-color: #fff1ef;
  color: #d96b63;
}

.archive-cat-card--clients .archive-cat-card__blob {
  background-color: #e9f9f2;
  color: #42a779;
}

.archive-cat-card__icon {
  width: 28px;
  height: 28px;
}

.archive-cat-card__title {
  margin: 0 0 0.7rem 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #1e2433;
  letter-spacing: -0.01em;
}

.archive-cat-card__description {
  margin: 0;
  font-size: 0.84rem;
  line-height: 1.6;
  color: #646d82;
  max-width: 220px;
}

.archive-cat-card__badge {
  margin-top: auto;
  padding-top: 1.25rem;
}

.archive-cat-card__badge span {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #f8fafc;
  color: #475569;
  border: 1px solid #e2e8f0;
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.archive-cat-card--dossiers:hover .archive-cat-card__badge span {
  background: #eef4ff;
  color: #3168c4;
  border-color: #cfe0ff;
}

.archive-cat-card--documents:hover .archive-cat-card__badge span {
  background: #fff1ef;
  color: #d96b63;
  border-color: #fbd5d1;
}

.archive-cat-card--clients:hover .archive-cat-card__badge span {
  background: #e9f9f2;
  color: #42a779;
  border-color: #c2eedb;
}
</style>

