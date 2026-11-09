<template>
  <nav
    v-if="!(hideOnSinglePage && totalPages <= 1)"
    class="pagination"
    role="navigation"
    aria-label="Pagination"
  >

    <ul class="pagination-list">
      <!-- Précédent -->
      <li>
        <button
          type="button"
          class="pagination-btn pagination-btn--nav"
          :disabled="disabled || currentPage <= 1"
          aria-label="Page précédente"
          @click="goTo(currentPage - 1)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
          </svg>
        </button>
      </li>

      <!-- Numéros de page avec ellipses -->
      <li v-for="(item, index) in pageItems" :key="`${item}-${index}`">
        <span v-if="item === ELLIPSIS" class="pagination-ellipsis" aria-hidden="true">…</span>
        <button
          v-else
          type="button"
          class="pagination-btn"
          :class="{ 'is-active': item === currentPage }"
          :disabled="disabled"
          :aria-current="item === currentPage ? 'page' : undefined"
          :aria-label="`Page ${item}`"
          @click="goTo(item as number)"
        >
          {{ item }}
        </button>
      </li>

      <!-- Suivant -->
      <li>
        <button
          type="button"
          class="pagination-btn pagination-btn--nav"
          :disabled="disabled || currentPage >= totalPages"
          aria-label="Page suivante"
          @click="goTo(currentPage + 1)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
          </svg>
        </button>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue';

/**
 * Composant de pagination réutilisable.
 *
 * Compatible avec la pagination DRF (PageNumberPagination) :
 *   - `totalItems` = champ `count` de la réponse
 *   - `pageSize`   = `page_size` côté backend (10 pour /affairs/)
 *   - la page sélectionnée s'envoie via `?page=N`
 *
 * Fonctionne aussi pour une pagination purement côté front (slice d'un tableau).
 *
 * Usage :
 *   <Pagination v-model="page" :totalItems="count" :pageSize="10" @change="fetchPage" />
 */
const props = withDefaults(
  defineProps<{
    /** Page courante (1-indexée), utilisée avec v-model. */
    modelValue: number;
    /** Nombre total d'éléments (champ `count` de DRF). */
    totalItems: number;
    /** Nombre d'éléments par page. */
    pageSize?: number;
    /** Nombre maximum de boutons numérotés visibles (hors ellipses). */
    maxVisible?: number;
    /** Désactive les interactions (ex : pendant un chargement). */
    disabled?: boolean;
    /** Masque le composant s'il n'y a qu'une seule page. */
    hideOnSinglePage?: boolean;
    /** Affiche le résumé "1–10 sur 42". */
    showSummary?: boolean;
  }>(),
  {
    pageSize: 10,
    maxVisible: 5,
    disabled: false,
    hideOnSinglePage: false,
    showSummary: true,
  }
);

const emit = defineEmits<{
  (e: 'update:modelValue', page: number): void;
  (e: 'change', page: number): void;
}>();

const ELLIPSIS = '…' as const;

const totalPages = computed(() =>
  Math.max(1, Math.ceil(Math.max(0, props.totalItems) / Math.max(1, props.pageSize)))
);

const currentPage = computed(() => Math.min(Math.max(1, props.modelValue), totalPages.value));

/** Construit la liste des pages à afficher, ex : [1, '…', 4, 5, 6, '…', 12]. */
const pageItems = computed<(number | typeof ELLIPSIS)[]>(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  const max = Math.max(3, props.maxVisible);

  if (total <= max + 2) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const half = Math.floor((max - 2) / 2);
  let start = Math.max(2, current - half);
  let end = Math.min(total - 1, start + (max - 3));
  start = Math.max(2, end - (max - 3));

  const items: (number | typeof ELLIPSIS)[] = [1];
  if (start > 2) items.push(ELLIPSIS);
  for (let p = start; p <= end; p++) items.push(p);
  if (end < total - 1) items.push(ELLIPSIS);
  items.push(total);
  return items;
});

function goTo(page: number) {
  if (props.disabled) return;
  const target = Math.min(Math.max(1, page), totalPages.value);
  if (target === currentPage.value) return;
  emit('update:modelValue', target);
  emit('change', target);
}
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 0.25rem;
}

.pagination-summary {
  margin: 0;
  font-size: 0.85rem;
  color: #6b7280;
}

.pagination-summary-strong {
  font-weight: 600;
  color: #1f2937;
}

.pagination-list {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  list-style: none;
  margin: 0 0 0 auto;
  padding: 0;
}

.pagination-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.1rem;
  height: 2.1rem;
  padding: 0 0.6rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease, transform 0.18s ease,
    box-shadow 0.18s ease;
}

.pagination-btn svg {
  width: 1rem;
  height: 1rem;
}

.pagination-btn:hover:not(:disabled):not(.is-active) {
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-1px);
}

.pagination-btn.is-active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: #ffffff;
  box-shadow: 0 4px 10px rgba(0, 87, 146, 0.25);
  cursor: default;
}

.pagination-btn:disabled:not(.is-active) {
  opacity: 0.45;
  cursor: not-allowed;
}

.pagination-btn:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.pagination-ellipsis {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.5rem;
  color: #9ca3af;
  font-weight: 600;
}

@media (max-width: 520px) {
  .pagination {
    justify-content: center;
  }

  .pagination-list {
    margin: 0;
  }
}
</style>

