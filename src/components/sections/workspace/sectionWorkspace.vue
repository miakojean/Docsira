<template>
  <div class="main-section gap-2">
    <headerNav title="Workspace" :showToolsButton="true" @handleEvent="isAddOpen = true" v-model="searchQuery" />

    <div v-if="store.allDossiers.length > 0" class="content-container">
      <div class="filters">
        <button
          v-for="f in filters"
          :key="f.value"
          class="filter-chip"
          :class="{ active: statutFilter === f.value }"
          @click="statutFilter = f.value"
        >
          {{ f.label }}
        </button>
      </div>

      <div v-if="filteredDossiers.length > 0" class="dossiers-grid">
        <affairsCards
          v-for="d in filteredDossiers"
          :key="d.id"
          :dossier="d"
          @goTo="openDossier(d)"
          @open="openDossier(d)"
          @details="openDossier(d)"
          @edit="openEdit(d)"
          @rename="openEdit(d)"
          @delete="openDelete(d)"
        />
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

    <div v-else-if="!store.isLoading" class="h-full w-full flex justify-center items-center">
      <emptyCards
        title="Workspace"
        mainText="Vous n'avez aucun dossier."
        subtitle="Créez votre premier dossier et rattachez-le à un client."
        btnLabel="Ajouter un dossier"
        @add="isAddOpen = true"
      />
    </div>

    <addDossierModale :isOpen="isAddOpen" @close="isAddOpen = false" @created="onCreated" />
    <editDossierModale :isOpen="isEditOpen" :dossier="editingDossier" @close="isEditOpen = false" @updated="onUpdated" />

    <deleteModale
      :isOpen="isDeleteOpen"
      :isLoading="isDeleting"
      :isSuccess="isDeleteSuccess"
      :itemName="dossierToDelete?.title || 'ce dossier'"
      :isFolder="true"
      title="Supprimer le dossier"
      description="Êtes-vous sûr de vouloir supprimer définitivement ce dossier ?"
      subtext="Attention, cette action est irréversible."
      @close="isDeleteOpen = false; isDeleteSuccess = false"
      @delete="confirmDelete"
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
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
import affairsCards from '../../cards/affairsCards.vue';
import addDossierModale from '../../modale/addDossierModale.vue';
import editDossierModale from '../../modale/editDossierModale.vue';
import deleteModale from '../../modale/deleteModale.vue';
import SuccesModale from '../../modale/succesModale.vue';
import { useClientDossierStore, type Dossier } from '../../../stores/dossierStore';

const store = useClientDossierStore();
const router = useRouter();

function openDossier(d: Dossier) {
  router.push(`/dashboard/affairs/${d.id}`);
}
const isAddOpen = ref(false);
const isSuccess = ref(false);
const successTitle = ref('');
const successSubtitle = ref('');
const searchQuery = ref('');
const statutFilter = ref('ALL');

// Gestion modification / suppression
const isEditOpen = ref(false);
const editingDossier = ref<Dossier | null>(null);
const isDeleteOpen = ref(false);
const dossierToDelete = ref<Dossier | null>(null);
const isDeleting = ref(false);
const isDeleteSuccess = ref(false);

const filters = [
  { value: 'ALL', label: 'Tous' },
  { value: 'NOUVEAU', label: 'Nouveaux' },
  { value: 'EN_COURS', label: 'En cours' },
  { value: 'EN_ATTENTE', label: 'En attente' },
  { value: 'TERMINE', label: 'Terminés' },
  { value: 'CLOTURE', label: 'Clôturés' },
];

const filteredDossiers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  return store.allDossiers.filter(d =>
    (statutFilter.value === 'ALL' || d.statut === statutFilter.value) &&
    (!q || [d.title, d.reference_affair, d.client?.nom_complet]
      .some(v => (v || '').toLowerCase().includes(q)))
  );
});

function onCreated() {
  isAddOpen.value = false;
  successTitle.value = "Dossier créé avec succès";
  successSubtitle.value = "Le dossier a été rattaché au client.";
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

.filters {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-chip {
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background: #fff;
  font-size: 0.8rem;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-chip:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.filter-chip.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: #fff;
}

.dossiers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 1rem;
  width: 100%;
  padding-bottom: 2rem;
}
</style>
