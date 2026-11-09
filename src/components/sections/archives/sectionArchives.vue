<template>
  <section class="main-section archives-section">
    <div class="archives-detail">
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

      <headerNav
        :title="headerTitle"
        :placeholder="searchPlaceholder"
        :showToolsButton="false"
        v-model="searchQuery"
      />

      <!-- Onglet Dossiers par défaut -->
      <archiveDossiersTab
        v-if="activeCategory === 'dossiers'"
        :searchQuery="searchQuery"
      />

      <!-- Onglet Clients -->
      <archiveClientsTab
        v-else-if="activeCategory === 'clients'"
        :searchQuery="searchQuery"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import headerNav from '../../navbar/headerNav.vue';
import archiveDossiersTab from './archiveDossiersTab.vue';
import archiveClientsTab from './archiveClientsTab.vue';

import { useClientDossierStore } from '../../../stores/dossierStore';
import { useClientStore } from '../../../stores/clientStore';

type ArchiveCategory = 'dossiers' | 'clients';

const router = useRouter();
const route = useRoute();
const dossierStore = useClientDossierStore();
const clientStore = useClientStore();

// Par défaut : tomber directement sur les dossiers
const activeCategory = ref<ArchiveCategory>('dossiers');
const searchQuery = ref('');

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
