<template>
  <section class="main-section archives-section">
    <div class="archives-detail">
      <headerNav
        :title="headerTitle"
        :placeholder="searchPlaceholder"
        :showToolsButton="false"
        v-model="searchQuery"
      >
        <template #actions>
          <div v-if="activeCategory === 'dossiers' && dossierStore.archivedDossiers.length > 0" class="controls-bar">
            <div class="sort-control">
              <div class="sort-select">
                <BaseSelectInput
                  v-model="dossierStatutFilter"
                  :options="DOSSIER_STATUT_OPTIONS"
                  inputId="archive-dossiers-statut"
                />
              </div>
            </div>

            <div class="sort-control">
              <div class="sort-select">
                <BaseSelectInput
                  v-model="dossierSortBy"
                  :options="DOSSIER_SORT_OPTIONS"
                  inputId="archive-dossiers-sort"
                />
              </div>
            </div>
          </div>

          <div v-else-if="activeCategory === 'clients' && clientStore.archivedClients.length > 0" class="controls-bar">
            <div class="sort-control">
              <div class="sort-select">
                <BaseSelectInput
                  v-model="clientSortBy"
                  :options="clientSortOptions"
                  inputId="archive-clients-sort"
                />
              </div>
            </div>
          </div>
        </template>
      </headerNav>

      <div class="archives-topbar">
        <div class="category-tabs">
          <button
            v-for="cat in categories"
            :key="cat.key"
            type="button"
            class="category-tab"
            :class="{ active: activeCategory === cat.key }"
            @click="selectCategory(cat.key)"
          >
            {{ cat.label }} ({{ cat.count }})
          </button>
        </div>
      </div>

      <!-- Onglet Dossiers par défaut -->
      <archiveDossiersTab
        v-if="activeCategory === 'dossiers'"
        :searchQuery="searchQuery"
        :statutFilter="dossierStatutFilter"
        :sortBy="dossierSortBy"
      />

      <!-- Onglet Clients -->
      <archiveClientsTab
        v-else-if="activeCategory === 'clients'"
        :searchQuery="searchQuery"
        :sortBy="clientSortBy"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import headerNav from '../../navbar/headerNav.vue';
import BaseSelectInput from '../../BaseInput/BaseSelectInput.vue';
import archiveDossiersTab from './archiveDossiersTab.vue';
import archiveClientsTab from './archiveClientsTab.vue';

import { useClientDossierStore } from '../../../stores/dossierStore';
import { useClientStore } from '../../../stores/clientStore';
import { DOSSIER_STATUT_OPTIONS, DOSSIER_SORT_OPTIONS } from '../../../helpers/dossierSort';

type ArchiveCategory = 'dossiers' | 'clients';

const router = useRouter();
const route = useRoute();
const dossierStore = useClientDossierStore();
const clientStore = useClientStore();

// Par défaut : tomber directement sur les dossiers
const activeCategory = ref<ArchiveCategory>('dossiers');
const searchQuery = ref('');
const dossierStatutFilter = ref('ALL');
const dossierSortBy = ref('date_desc');
const clientSortBy = ref('date_desc');

const clientSortOptions = [
  { value: 'date_desc', label: "Plus récents d'abord" },
  { value: 'date_asc', label: "Plus anciens d'abord" },
  { value: 'alpha_asc', label: 'Ordre alphabétique (A → Z)' },
  { value: 'alpha_desc', label: 'Ordre alphabétique (Z → A)' },
  { value: 'ref_asc', label: 'Référence (croissante)' },
  { value: 'ville_asc', label: 'Ville (A → Z)' },
];

const categories = computed(() => [
  { key: 'dossiers' as const, label: 'Dossiers', count: dossierStore.archivedDossiers.length },
  { key: 'clients' as const, label: 'Clients', count: clientStore.archivedClients.length },
]);

const headerTitle = computed(() => {
  if (activeCategory.value === 'clients') return 'Archives — Clients';
  return 'Archives — Dossiers';
});

const searchPlaceholder = computed(() => {
  if (activeCategory.value === 'clients') return 'Rechercher un client archivé...';
  return 'Rechercher un dossier archivé...';
});

function selectCategory(cat: ArchiveCategory) {
  activeCategory.value = cat;
  searchQuery.value = '';
  router.replace({ query: { ...route.query, tab: cat } });
}

watch(
  () => route.query.tab,
  (tab) => {
    if (tab === 'clients') {
      activeCategory.value = 'clients';
    } else {
      activeCategory.value = 'dossiers';
    }
  },
  { immediate: true }
);

onMounted(() => {
  dossierStore.fetchArchivedDossiers();
  clientStore.fetchArchivedClients();
});
</script>

<style scoped>
.archives-section {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow-y: auto;
}

.archives-detail {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  height: 100%;
  width: 100%;
}

.controls-bar {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.sort-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-select {
  min-width: fit-content;
}

.sort-select :deep(.select-input) {
  padding: 0.5rem 2.2rem 0.5rem 0.8rem;
  font-size: 0.85rem;
}

.archives-topbar {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid #e2e8f0;
}

.category-tabs {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 10px;
}

.category-tab {
  padding: 0.45rem 1rem;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-tab:hover {
  color: #1e293b;
}

.category-tab.active {
  background: #ffffff;
  color: var(--primary-color, #005792);
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
}

.size-4 {
  width: 1rem;
  height: 1rem;
}
</style>
