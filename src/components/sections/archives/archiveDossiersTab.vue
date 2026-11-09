<template>
  <div class="archive-tab-content">
    <div v-if="dossierStore.isLoading && dossierStore.allDossiers.length === 0" class="loader-area">
      <LogoLoader size="lg" label="Chargement des dossiers..." />
    </div>

    <div v-else-if="dossierStore.allDossiers.length > 0" class="content-container">
      <!-- Filtres par statut -->
      <div class="filters">
        <button
          v-for="f in dossierFilters"
          :key="f.value"
          type="button"
          class="filter-chip"
          :class="{ active: dossierStatutFilter === f.value }"
          @click="dossierStatutFilter = f.value"
        >
          {{ f.label }}
        </button>
      </div>

      <div v-if="filteredDossiers.length > 0" class="flex flex-col gap-4">
        <div class="dossiers-grid">
          <affairsCards
            v-for="d in paginatedDossiers"
            :key="d.id"
            :dossier="d"
            :isClientCard="false"
            @goTo="openDossier(d)"
            @open="openDossier(d)"
            @details="openDossierDetails(d)"
            @edit="openDossierEdit(d)"
            @rename="openDossierEdit(d)"
            @delete="openDossierDelete(d)"
          />
        </div>

        <Pagination
          v-model="currentPage"
          :totalItems="filteredDossiers.length"
          :pageSize="pageSize"
          :hideOnSinglePage="false"
        />
      </div>

      <div v-else class="empty-area">
        <emptyCards
          title="Dossiers archivés"
          mainText="Aucun dossier ne correspond à votre recherche."
          subtitle="Vérifiez l'orthographe ou changez de filtre."
          :showAddButton="false"
        />
      </div>
    </div>

    <div v-else class="empty-area">
      <emptyCards
        title="Dossiers archivés"
        mainText="Aucun dossier disponible."
        subtitle="Vos dossiers archivés apparaîtront ici."
        :showAddButton="false"
      />
    </div>

    <!-- Modales Dossiers -->
    <detailsModale
      :isOpen="isDossierDetailsOpen"
      :item="dossierDetailsItem"
      @close="isDossierDetailsOpen = false"
      @action="onDossierDetailsAction"
    />

    <editDossierModale
      :isOpen="isDossierEditOpen"
      :dossier="editingDossier"
      @close="isDossierEditOpen = false"
      @updated="onDossierUpdated"
    />

    <deleteModale
      :isOpen="isDossierDeleteOpen"
      :isLoading="isDeletingDossier"
      :isSuccess="isDeleteDossierSuccess"
      :itemName="dossierToDelete?.title || 'ce dossier'"
      :isFolder="true"
      title="Supprimer le dossier"
      description="Êtes-vous sûr de vouloir supprimer définitivement ce dossier ?"
      subtext="Attention, cette action est irréversible."
      @close="isDossierDeleteOpen = false; isDeleteDossierSuccess = false"
      @delete="confirmDeleteDossier"
    />

    <SuccesModale
      modaleTitle="Succès"
      :isOpen="isSuccess"
      :title="successTitle"
      :subtitle="successSubtitle"
      actionText="continuer"
      @close="isSuccess = false"
      @handleEvent="isSuccess = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import affairsCards from '../../cards/affairsCards.vue';
import emptyCards from '../../cards/emptyCards.vue';
import LogoLoader from '../../tools/LogoLoader.vue';
import Pagination from '../../tools/Pagination.vue';
import detailsModale, { type ItemDetails } from '../../modale/detailsModale.vue';
import editDossierModale from '../../modale/editDossierModale.vue';
import deleteModale from '../../modale/deleteModale.vue';
import SuccesModale from '../../modale/succesModale.vue';
import { useClientDossierStore, type Dossier } from '../../../stores/dossierStore';

const props = withDefaults(
  defineProps<{
    searchQuery?: string;
  }>(),
  {
    searchQuery: '',
  }
);

const router = useRouter();
const dossierStore = useClientDossierStore();

const pageSize = 10;
const currentPage = ref(1);
const dossierStatutFilter = ref('ALL');

const dossierFilters = [
  { value: 'ALL', label: 'Tous' },
  { value: 'NOUVEAU', label: 'Nouveaux' },
  { value: 'EN_COURS', label: 'En cours' },
  { value: 'EN_ATTENTE', label: 'En attente' },
  { value: 'TERMINE', label: 'Terminés' },
  { value: 'CLOTURE', label: 'Clôturés' },
];

watch([() => props.searchQuery, dossierStatutFilter], () => {
  currentPage.value = 1;
});

const filteredDossiers = computed(() => {
  const q = props.searchQuery.trim().toLowerCase();
  const filter = dossierStatutFilter.value;

  return dossierStore.allDossiers.filter((d) => {
    const matchesStatut = filter === 'ALL' || d.statut === filter;
    if (!matchesStatut) return false;
    if (!q) return true;

    const clientName = d.client?.nom_complet || '';
    const clientRef = d.client?.reference_client || '';
    return [d.title, d.reference_affair, d.type_affair, clientName, clientRef].some((v) =>
      (v || '').toLowerCase().includes(q)
    );
  });
});

const paginatedDossiers = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return filteredDossiers.value.slice(start, start + pageSize);
});

// Modales state
const isDossierDetailsOpen = ref(false);
const selectedDossier = ref<Dossier | null>(null);
const isDossierEditOpen = ref(false);
const editingDossier = ref<Dossier | null>(null);
const isDossierDeleteOpen = ref(false);
const dossierToDelete = ref<Dossier | null>(null);
const isDeletingDossier = ref(false);
const isDeleteDossierSuccess = ref(false);

const isSuccess = ref(false);
const successTitle = ref('');
const successSubtitle = ref('');

const dossierDetailsItem = computed<ItemDetails>(() => {
  const d = selectedDossier.value;
  if (!d) return { isFolder: true, name: 'Dossier' };
  return {
    isFolder: true,
    name: d.title,
    path: d.reference_affair ? `Dossier / ${d.reference_affair}` : '/Archives/Docsira',
    size: `${d.documents_count ?? 0} document(s)`,
    fileCount: d.documents_count ?? 0,
    owner: d.client?.nom_complet || 'Client',
    createdAt: d.creation_date
      ? new Date(d.creation_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })
      : undefined,
    updatedAt: d.statut ? d.statut.replace(/_/g, ' ').toLowerCase() : 'en cours',
    isShared: false,
  };
});

function openDossier(d: Dossier) {
  router.push(`/dashboard/affairs/${d.id}`);
}

function openDossierDetails(d: Dossier) {
  selectedDossier.value = d;
  isDossierDetailsOpen.value = true;
}

function onDossierDetailsAction() {
  if (selectedDossier.value) {
    isDossierDetailsOpen.value = false;
    openDossier(selectedDossier.value);
  }
}

function openDossierEdit(d: Dossier) {
  editingDossier.value = d;
  isDossierEditOpen.value = true;
}

function onDossierUpdated() {
  isDossierEditOpen.value = false;
  successTitle.value = 'Dossier mis à jour';
  successSubtitle.value = 'Les informations du dossier ont été modifiées avec succès.';
  isSuccess.value = true;
}

function openDossierDelete(d: Dossier) {
  dossierToDelete.value = d;
  isDeleteDossierSuccess.value = false;
  isDossierDeleteOpen.value = true;
}

async function confirmDeleteDossier() {
  if (!dossierToDelete.value) return;
  isDeletingDossier.value = true;
  const ok = await dossierStore.deleteDossier(dossierToDelete.value.id);
  isDeletingDossier.value = false;
  if (ok) {
    isDeleteDossierSuccess.value = true;
    setTimeout(() => {
      isDossierDeleteOpen.value = false;
      isDeleteDossierSuccess.value = false;
    }, 1200);
  }
}
</script>

<style scoped>
.archive-tab-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.content-container {
  padding: 0.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.loader-area,
.empty-area {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.filters {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-chip {
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  font-size: 0.8rem;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-chip:hover {
  border-color: var(--primary-color, #005792);
  color: var(--primary-color, #005792);
}

.filter-chip.active {
  background: var(--primary-color, #005792);
  border-color: var(--primary-color, #005792);
  color: #ffffff;
}

.dossiers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(245px, 1fr));
  gap: 1.25rem 0.75rem;
  width: 100%;
  padding-bottom: 1rem;
}
</style>

