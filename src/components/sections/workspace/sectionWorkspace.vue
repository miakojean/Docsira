<template>
  <div class="main-section gap-2">
    <headerNav
      title="Workspace"
      :showToolsButton="authStore.canEdit"
      @handleEvent="openAddRoot"
      v-model="searchQuery"
    >
      <template v-if="store.allDossiers.length > 0" #actions>
        <div class="controls-bar">
          <div class="sort-control">
            <div class="sort-select">
              <BaseSelectInput
                v-model="statutFilter"
                :options="DOSSIER_STATUT_OPTIONS"
                inputId="workspace-dossiers-statut"
              />
            </div>
          </div>

          <div class="sort-control">
            <div class="sort-select">
              <BaseSelectInput
                v-model="sortBy"
                :options="DOSSIER_SORT_OPTIONS"
                inputId="workspace-dossiers-sort"
              />
            </div>
          </div>
        </div>
      </template>
    </headerNav>

    <div v-if="store.allDossiers.length > 0" class="content-container">
      <div class="workspace-view-container flex-1 flex flex-col gap-3">
        <!-- Grille de tous les dossiers de tous les clients directement -->
        <div v-if="filteredDossiers.length > 0" class="flex-1 flex flex-col justify-between gap-4">
          <div class="dossiers-grid">
            <affairsCards
              v-for="d in paginatedDossiers"
              :key="d.id"
              :dossier="d"
              :isClientCard="false"
              :canEdit="authStore.canEdit"
              @goTo="openDossier(d)"
              @open="openDossier(d)"
              @details="openDetails(d)"
              @edit="openEdit(d)"
              @rename="openEdit(d)"
              @share="openShareDossier(d)"
              @link="openShareDossier(d)"
              @archive="handleArchiveDossier(d)"
              @delete="openDelete(d)"
            />
          </div>

          <!-- Pagination -->
          <Pagination
            v-model="currentPage"
            :totalItems="filteredDossiers.length"
            :pageSize="pageSize"
            :hideOnSinglePage="false"
          />
          <!-- <paginator/> -->
          
        </div>

        <div v-else class="flex-1 w-full flex justify-center items-center">
          <emptyCards
            title="Workspace"
            mainText="Aucun dossier ne correspond à votre recherche."
            subtitle="Vérifiez l'orthographe ou changez de filtre."
            :showAddButton="false"
          />
        </div>
      </div>
    </div>

    <!-- ÉTAT VIDE GLOBAL DU CABINET -->
    <div v-else-if="store.isLoading" class="h-full w-full flex justify-center items-center">
      <LogoLoader size="lg" label="Chargement des dossiers..." />
    </div>

    <div v-else class="h-full w-full flex justify-center items-center">
      <emptyCards
        title="Workspace"
        mainText="Vous n'avez aucun dossier."
        subtitle="Créez votre premier dossier pour commencer à travailler."
        btnLabel="Ajouter un dossier"
        :showAddButton="authStore.canEdit"
        @add="openAddRoot"
      />
    </div>

    <!-- Modales -->
    <detailsModale
      :isOpen="isDetailsOpen"
      :item="folderDetailsItem"
      @close="isDetailsOpen = false"
      @action="onDetailsAction"
    />

    <addDossierModale
      :isOpen="isAddOpen"
      @close="isAddOpen = false"
      @created="onCreated"
    />

    <editDossierModale
      :isOpen="isEditOpen"
      :dossier="editingDossier"
      @close="isEditOpen = false"
      @updated="onUpdated"
    />

    <deleteModale
      :isOpen="isDeleteOpen"
      :isLoading="isDeleting"
      :isSuccess="isDeleteSuccess"
      :itemName="dossierToDelete?.title || 'ce dossier'"
      :isFolder="true"
      title="Mettre à la corbeille"
      description="Êtes-vous sûr de vouloir déplacer ce dossier dans la corbeille ?"
      subtext="Vous pourrez le restaurer depuis la corbeille du cabinet."
      @close="isDeleteOpen = false; isDeleteSuccess = false"
      @delete="confirmDelete"
    />

    <linkModale
      :isOpen="isShareDossierOpen"
      :targetTitle="dossierToShare ? `${dossierToShare.reference_affair} • ${dossierToShare.title}` : ''"
      description="Créez un lien de partage pour permettre à un collaborateur ou à un client de télécharger l'ensemble des documents de ce dossier (archive ZIP)."
      :links="dossierShareLinks"
      :isLoading="isShareDossierLoading"
      :isCreating="isShareDossierCreating"
      :errorMessage="shareDossierError"
      @close="closeShareDossier"
      @create="createDossierShareLink"
      @revoke="revokeDossierShareLink"
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
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
import affairsCards from '../../cards/affairsCards.vue';
import addDossierModale from '../../modale/addDossierModale.vue';
import editDossierModale from '../../modale/editDossierModale.vue';
import deleteModale from '../../modale/deleteModale.vue';
import detailsModale, { type ItemDetails } from '../../modale/detailsModale.vue';
import linkModale from '../../modale/linkModale.vue';
import SuccesModale from '../../modale/succesModale.vue';
import LogoLoader from '../../tools/LogoLoader.vue';
import Pagination from '../../tools/Pagination.vue';
import BaseSelectInput from '../../BaseInput/BaseSelectInput.vue';
import { useClientDossierStore, type AffairShareLink, type Dossier } from '../../../stores/dossierStore';
import { useAuthStore } from '../../../stores/authStore';
import { DOSSIER_STATUT_OPTIONS, DOSSIER_SORT_OPTIONS, sortDossiers } from '../../../helpers/dossierSort';

const store = useClientDossierStore();
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const isAddOpen = ref(false);
const isSuccess = ref(false);
const successTitle = ref('');
const successSubtitle = ref('');
const searchQuery = ref('');
const statutFilter = ref('ALL');
const sortBy = ref('date_desc');

const currentPage = ref(1);
const pageSize = ref(10);

const isDetailsOpen = ref(false);
const selectedDossier = ref<Dossier | null>(null);

const isEditOpen = ref(false);
const editingDossier = ref<Dossier | null>(null);
const isDeleteOpen = ref(false);
const dossierToDelete = ref<Dossier | null>(null);
const isDeleting = ref(false);
const isDeleteSuccess = ref(false);

// Tous les dossiers filtrés directement
const filteredDossiers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  const filter = statutFilter.value;

  return store.allDossiers.filter((d) => {
    // Statut
    const matchesStatut = filter === 'ALL' || d.statut === filter;
    if (!matchesStatut) return false;

    // Recherche par titre de dossier, référence, type d'affaire ou nom/référence du client
    if (!q) return true;

    const clientName = d.client?.nom_complet || '';
    const clientRef = d.client?.reference_client || '';
    return [d.title, d.reference_affair, d.type_affair, clientName, clientRef].some((v) =>
      (v || '').toLowerCase().includes(q)
    );
  });
});

const sortedDossiers = computed(() => sortDossiers(filteredDossiers.value, sortBy.value));

// Réinitialiser la page quand les filtres ou le tri changent
watch([searchQuery, statutFilter, sortBy], () => {
  currentPage.value = 1;
});

const paginatedDossiers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return sortedDossiers.value.slice(start, start + pageSize.value);
});

function openAddRoot() {
  isAddOpen.value = true;
}

function openDossier(d: Dossier) {
  router.push(`/dashboard/affairs/${d.id}`);
}

const folderDetailsItem = computed<ItemDetails>(() => {
  const d = selectedDossier.value;
  if (!d) return { isFolder: true, name: 'Dossier' };
  return {
    isFolder: true,
    name: d.title,
    path: d.reference_affair ? `Dossier / ${d.reference_affair}` : '/Projets/Docsira',
    size: `${d.documents_count ?? 0} document(s)`,
    fileCount: d.documents_count ?? 0,
    owner: d.client?.nom_complet || 'Client',
    createdBy: d.created_by_name || undefined,
    createdAt: d.creation_date
      ? new Date(d.creation_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })
      : undefined,
    updatedAt: d.statut ? d.statut.replace(/_/g, ' ').toLowerCase() : 'en cours',
    isShared: false,
  };
});

function openDetails(d: Dossier) {
  selectedDossier.value = d;
  isDetailsOpen.value = true;
}

function onDetailsAction() {
  if (selectedDossier.value) {
    isDetailsOpen.value = false;
    openDossier(selectedDossier.value);
  }
}

function onCreated() {
  isAddOpen.value = false;
  successTitle.value = "Dossier créé avec succès";
  successSubtitle.value = "Le dossier est maintenant disponible dans votre Workspace.";
  isSuccess.value = true;
}

function openEdit(d: Dossier) {
  editingDossier.value = d;
  isEditOpen.value = true;
}

function onUpdated() {
  isEditOpen.value = false;
  successTitle.value = "Dossier mis à jour";
  successSubtitle.value = "Les informations du dossier ont été modifiées avec succès.";
  isSuccess.value = true;
}

async function handleArchiveDossier(d: Dossier) {
  const ok = await store.archiveDossier(d.id);
  if (ok) {
    successTitle.value = "Dossier archivé";
    successSubtitle.value = "Le dossier a été transféré dans les archives du cabinet.";
    isSuccess.value = true;
  }
}

// Partage par lien de dossier
const isShareDossierOpen = ref(false);
const dossierToShare = ref<Dossier | null>(null);
const dossierShareLinks = ref<AffairShareLink[]>([]);
const isShareDossierLoading = ref(false);
const isShareDossierCreating = ref(false);
const shareDossierError = ref('');

async function openShareDossier(d: Dossier) {
  dossierToShare.value = d;
  dossierShareLinks.value = [];
  shareDossierError.value = '';
  isShareDossierOpen.value = true;
  isShareDossierLoading.value = true;
  try {
    const existing = await store.fetchAffairShareLinks(d.id);
    if (existing.length > 0) {
      dossierShareLinks.value = existing;
    } else {
      const created = await store.createAffairShareLink(d.id, 7);
      if (created) {
        dossierShareLinks.value = [created];
      } else if (store.errorMessage) {
        shareDossierError.value = store.errorMessage;
      }
    }
  } finally {
    isShareDossierLoading.value = false;
  }
}

function closeShareDossier() {
  isShareDossierOpen.value = false;
  dossierToShare.value = null;
  shareDossierError.value = '';
}

async function createDossierShareLink(expiresInDays: number | null) {
  if (!dossierToShare.value) return;
  isShareDossierCreating.value = true;
  shareDossierError.value = '';
  try {
    const created = await store.createAffairShareLink(dossierToShare.value.id, expiresInDays);
    if (created) {
      dossierShareLinks.value = [created, ...dossierShareLinks.value];
    } else {
      shareDossierError.value = store.errorMessage || 'Impossible de créer le lien.';
    }
  } finally {
    isShareDossierCreating.value = false;
  }
}

async function revokeDossierShareLink(linkId: string) {
  if (!dossierToShare.value) return;
  shareDossierError.value = '';
  const ok = await store.revokeAffairShareLink(dossierToShare.value.id, linkId);
  if (ok) {
    dossierShareLinks.value = dossierShareLinks.value.filter((l) => l.id !== linkId);
  } else {
    shareDossierError.value = store.errorMessage || 'Impossible de révoquer ce lien.';
  }
}

function openDelete(d: Dossier) {
  dossierToDelete.value = d;
  isDeleteSuccess.value = false;
  isDeleteOpen.value = true;
}

async function confirmDelete() {
  if (!dossierToDelete.value) return;
  isDeleting.value = true;
  const ok = await store.deleteDossier(dossierToDelete.value.id);
  isDeleting.value = false;
  if (ok) {
    isDeleteSuccess.value = true;
    setTimeout(() => {
      isDeleteOpen.value = false;
      isDeleteSuccess.value = false;
    }, 1200);
  }
}

// Initialisation recherche si paramètre dans l'URL
watch(
  () => route.query.q,
  (newQ) => {
    if (typeof newQ === 'string') {
      searchQuery.value = newQ;
    }
  },
  { immediate: true }
);

onMounted(() => {
  store.fetchAllDossiers();
});
</script>

<style scoped>
.main-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.content-container {
  padding: 0.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.workspace-view-container {
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

.dossiers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(145px, 1fr));
  gap: 1.25rem 0.75rem;
  width: 100%;
  padding-bottom: 2rem;
}

.dossiers-grid :deep(.folder-visual) {
  transform: scale(0.85);
  transform-origin: top center;
  margin-bottom: -1.36rem;
}

.size-4 {
  width: 1rem;
  height: 1rem;
}
</style>
