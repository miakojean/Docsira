<template>
  <section class="main-section archives-section">
    <!-- =====================================================
         VUE 1 : HUB DES ARCHIVES (LES 2 CARTES)
         ===================================================== -->
    <div v-if="!activeCategory" class="archives-hub">
      <div class="archives-hub__header">
        <h2 class="archives-hub__title">Archives du cabinet</h2>
        <p class="archives-hub__subtitle">
          Explorez et consultez vos dossiers et clients archivés en un seul endroit
        </p>
      </div>

      <div class="archives-hub__cards">
        <archiveCategoryCard
          variant="dossiers"
          title="Dossiers"
          description="Retrouvez l'ensemble de vos dossiers archivés, suivez leur progression et consultez leurs pièces."
          :count="dossierStore.allDossiers.length"
          :countLabel="dossierStore.allDossiers.length > 1 ? 'dossiers' : 'dossier'"
          @select="selectCategory('dossiers')"
        />

        <archiveCategoryCard
          variant="clients"
          title="Clients"
          description="Consultez les fiches complètes de vos clients archivés et accédez directement à leurs dossiers."
          :count="clientStore.clients.length"
          :countLabel="clientStore.clients.length > 1 ? 'clients' : 'client'"
          @select="selectCategory('clients')"
        />
      </div>

      <div class="archives-hub__footer">
        <button type="button" class="archives-hub__cta" @click="selectCategory('dossiers')">
          Tout parcourir
        </button>
      </div>
    </div>

    <!-- =====================================================
         VUE 2 : DÉTAIL D'UNE CATÉGORIE
         ===================================================== -->
    <div v-else class="archives-detail">
      <div class="archives-topbar">
        <button type="button" class="back-btn" @click="clearCategory">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
          <span>Retour aux archives</span>
        </button>

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

      <!-- Onglet actif -->
      <archiveDossiersTab
        v-if="activeCategory === 'dossiers'"
        :searchQuery="searchQuery"
      />

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
import archiveCategoryCard from '../../cards/archiveCategoryCard.vue';
import archiveDossiersTab from './archiveDossiersTab.vue';
import archiveClientsTab from './archiveClientsTab.vue';

import { useClientDossierStore } from '../../../stores/dossierStore';
import { useClientStore } from '../../../stores/clientStore';

type ArchiveCategory = 'dossiers' | 'clients';

const router = useRouter();
const route = useRoute();
const dossierStore = useClientDossierStore();
const clientStore = useClientStore();

const activeCategory = ref<ArchiveCategory | null>(null);
const searchQuery = ref('');

const categories = computed(() => [
  { key: 'dossiers' as const, label: 'Dossiers', count: dossierStore.allDossiers.length },
  { key: 'clients' as const, label: 'Clients', count: clientStore.clients.length },
]);

const headerTitle = computed(() => {
  if (activeCategory.value === 'dossiers') return 'Archives — Dossiers';
  if (activeCategory.value === 'clients') return 'Archives — Clients';
  return 'Archives';
});

const searchPlaceholder = computed(() => {
  if (activeCategory.value === 'dossiers') return 'Rechercher un dossier...';
  if (activeCategory.value === 'clients') return 'Rechercher un client...';
  return 'Rechercher...';
});

function selectCategory(cat: ArchiveCategory) {
  activeCategory.value = cat;
  searchQuery.value = '';
  router.replace({ query: { ...route.query, tab: cat } });
}

function clearCategory() {
  activeCategory.value = null;
  searchQuery.value = '';
  const q = { ...route.query };
  delete q.tab;
  router.replace({ query: q });
}

watch(
  () => route.query.tab,
  (tab) => {
    if (tab === 'dossiers' || tab === 'clients') {
      activeCategory.value = tab;
    } else if (!tab) {
      activeCategory.value = null;
    }
  },
  { immediate: true }
);

onMounted(() => {
  dossierStore.fetchAllDossiers();
  clientStore.fetchClients();
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

/* =====================================================
   HUB DES CARTES (Design inspiré de l'image de référence)
   ===================================================== */
.archives-hub {
  flex: 1;
  width: 100%;
  max-width: 780px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2.75rem;
}

.archives-hub__header {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
}

.archives-hub__title {
  margin: 0;
  font-size: 1.85rem;
  font-weight: 700;
  color: #181e2c;
  letter-spacing: -0.02em;
}

.archives-hub__subtitle {
  margin: 0;
  font-size: 0.95rem;
  color: #646d82;
  font-weight: 400;
}

.archives-hub__cards {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: stretch;
  flex-wrap: wrap;
  gap: 2rem;
}

.archives-hub__footer {
  display: flex;
  justify-content: center;
}

.archives-hub__cta {
  padding: 0.78rem 2rem;
  border-radius: 6px;
  border: none;
  background-color: #161b2e;
  color: #ffffff;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(22, 27, 46, 0.18);
  transition: background-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.archives-hub__cta:hover {
  background-color: var(--primary-color, #005792);
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(0, 87, 146, 0.25);
}

/* =====================================================
   VUE DÉTAILLÉE D'UNE CATÉGORIE
   ===================================================== */
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
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid #e2e8f0;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #334155;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  border-color: var(--primary-color, #005792);
  color: var(--primary-color, #005792);
  transform: translateX(-2px);
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
  padding: 0.4rem 0.9rem;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 0.82rem;
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
