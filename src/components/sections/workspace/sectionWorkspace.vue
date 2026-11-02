<template>
  <div class="main-section gap-2">
    <headerNav
      title="Workspace"
      :showToolsButton="true"
      @handleEvent="openAddRoot"
      v-model="searchQuery"
    />

    <div v-if="store.allDossiers.length > 0" class="content-container">

      <!-- ========================================== -->
      <!-- VUE DOSSIERS D'UN CLIENT SPÉCIFIQUE       -->
      <!-- ========================================== -->
      <div v-if="currentClient" class="client-view-container flex flex-col gap-3">
        <!-- Barre de navigation du client (Breadcrumb + bouton retour + bouton ajouter) -->
        <div class="client-folder-header">
          <div class="breadcrumb-nav">
            <button
              type="button"
              class="back-pill-btn"
              @click="closeClientFolder"
              title="Retour à tous les clients"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
              </svg>
              <span>Tous les clients</span>
            </button>
            <span class="breadcrumb-separator">/</span>
            <div class="breadcrumb-client-info">
              <span class="breadcrumb-client-name">{{ currentClient.nom_complet }}</span>
              <span v-if="currentClient.reference_client && currentClient.reference_client !== 'GÉNÉRAL'" class="breadcrumb-client-ref">
                {{ currentClient.reference_client }}
              </span>
            </div>
          </div>

          <div class="header-right-actions">
            <button
              type="button"
              class="btn-create-dossier"
              @click="openAddForCurrentClient"
              title="Créer un nouveau dossier pour ce client"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              <span>Nouveau dossier</span>
            </button>
          </div>
        </div>

        <!-- Filtres par statut pour les dossiers du client -->
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

        <!-- Grille des dossiers du client courant -->
        <div v-if="filteredClientDossiers.length > 0" class="dossiers-grid">
          <affairsCards
            v-for="d in filteredClientDossiers"
            :key="d.id"
            :dossier="d"
            :isClientCard="false"
            @goTo="openDossier(d)"
            @open="openDossier(d)"
            @details="openDetails(d)"
            @edit="openEdit(d)"
            @rename="openEdit(d)"
            @delete="openDelete(d)"
          />
        </div>

        <div v-else class="flex-1 w-full flex justify-center items-center">
          <emptyCards
            :title="currentClient.nom_complet"
            mainText="Aucun dossier ne correspond à vos critères."
            subtitle="Vérifiez vos filtres ou ajoutez un nouveau dossier pour ce client."
            btnLabel="Nouveau dossier"
            @add="openAddForCurrentClient"
          />
        </div>
      </div>

      <!-- ========================================== -->
      <!-- VUE RACINE : UNE SEULE CARTE PAR CLIENT   -->
      <!-- ========================================== -->
      <div v-else class="clients-view-container flex flex-col gap-3">
        <!-- Filtres par statut -->
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

        <!-- Grille des cartes dossiers clients -->
        <div v-if="filteredClientGroups.length > 0" class="dossiers-grid">
          <affairsCards
            v-for="group in filteredClientGroups"
            :key="group.client.id"
            :isClientCard="true"
            :title="group.client.nom_complet"
            :subtitle="formatGroupSubtitle(group)"
            :filesCount="group.dossiers.length"
            :progress="group.averageProgress"
            :previewExtensions="group.previewExtensions"
            @goTo="openClientFolder(group.client)"
            @open="openClientFolder(group.client)"
            @addDossier="openAddForClient(group.client)"
          />
        </div>

        <div v-else class="flex-1 w-full flex justify-center items-center">
          <emptyCards
            title="Workspace"
            mainText="Aucun dossier client ne correspond à votre recherche."
            subtitle="Vérifiez l'orthographe ou changez de filtre."
            :showAddButton="false"
          />
        </div>
      </div>
    </div>

    <!-- ÉTAT VIDE GLOBAL DU CABINET -->
    <div v-else-if="!store.isLoading" class="h-full w-full flex justify-center items-center">
      <emptyCards
        title="Workspace"
        mainText="Vous n'avez aucun dossier."
        subtitle="Créez votre premier dossier et rattachez-le à un client."
        btnLabel="Ajouter un dossier"
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
      :defaultClient="clientForAddDossier"
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
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
import affairsCards from '../../cards/affairsCards.vue';
import addDossierModale from '../../modale/addDossierModale.vue';
import editDossierModale from '../../modale/editDossierModale.vue';
import deleteModale from '../../modale/deleteModale.vue';
import detailsModale, { type ItemDetails } from '../../modale/detailsModale.vue';
import SuccesModale from '../../modale/succesModale.vue';
import { useClientDossierStore, type Dossier } from '../../../stores/dossierStore';
import type { ClientListItem } from '../../../stores/clientStore';

interface ClientGroup {
  client: ClientListItem;
  dossiers: Dossier[];
  totalFiles: number;
  averageProgress: number;
  previewExtensions: string[];
}

const store = useClientDossierStore();
const router = useRouter();
const route = useRoute();

const currentClient = ref<ClientListItem | null>(null);
const clientForAddDossier = ref<ClientListItem | null>(null);

const isAddOpen = ref(false);
const isSuccess = ref(false);
const successTitle = ref('');
const successSubtitle = ref('');
const searchQuery = ref('');
const statutFilter = ref('ALL');

const isDetailsOpen = ref(false);
const selectedDossier = ref<Dossier | null>(null);

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

function getDossierProgress(d: Dossier): number {
  switch (d.statut) {
    case 'TERMINE':
    case 'CLOTURE':
      return 100;
    case 'EN_COURS':
      return 60;
    case 'EN_ATTENTE':
      return 35;
    case 'NOUVEAU':
      return 15;
    case 'BLOQUE':
    case 'ANNULE':
      return 0;
    default:
      return 40;
  }
}

// Regroupement de tous les dossiers par client (une seule carte par client)
const clientGroups = computed<ClientGroup[]>(() => {
  const map = new Map<string, ClientGroup>();

  for (const d of store.allDossiers) {
    const clientId = d.client?.id || '__sans_client__';
    const clientData: ClientListItem = d.client || {
      id: '__sans_client__',
      reference_client: 'GÉNÉRAL',
      nom_complet: 'Dossiers généraux',
      nom: 'Général',
      prenoms: '',
      raison_sociale: '',
      telephone_1: '',
      telephone_2: '',
      email: '',
      adresse: '',
      ville: '',
      commune: '',
      charge_de_clientele: null,
      date_creation: '',
      date_premier_contact: null,
      type_client: 'PERSONNE_PHYSIQUE',
      statut: 'ACTIF',
    };

    if (!map.has(clientId)) {
      map.set(clientId, {
        client: clientData,
        dossiers: [],
        totalFiles: 0,
        averageProgress: 0,
        previewExtensions: [],
      });
    }

    const group = map.get(clientId)!;
    group.dossiers.push(d);
    group.totalFiles += d.documents_count ?? 0;

    if (d.documents_preview) {
      for (const ext of d.documents_preview) {
        if (ext && !group.previewExtensions.includes(ext) && group.previewExtensions.length < 2) {
          group.previewExtensions.push(ext);
        }
      }
    }
  }

  const result: ClientGroup[] = [];
  for (const group of map.values()) {
    if (group.dossiers.length > 0) {
      const sum = group.dossiers.reduce((acc, d) => acc + getDossierProgress(d), 0);
      group.averageProgress = Math.round(sum / group.dossiers.length);
    }
    result.push(group);
  }

  return result;
});

// Groupes de clients filtrés pour la vue racine
const filteredClientGroups = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  const filter = statutFilter.value;

  return clientGroups.value.filter((g) => {
    // Statut : le groupe doit comporter au moins un dossier correspondant au filtre
    const matchesStatut =
      filter === 'ALL' || g.dossiers.some((d) => d.statut === filter);
    if (!matchesStatut) return false;

    // Recherche sur le nom/ref du client ou sur le titre/ref de l'un de ses dossiers
    if (!q) return true;

    const matchesClient = [g.client.nom_complet, g.client.reference_client, g.client.email]
      .some((v) => (v || '').toLowerCase().includes(q));
    if (matchesClient) return true;

    const matchesDossier = g.dossiers.some((d) =>
      [d.title, d.reference_affair].some((v) => (v || '').toLowerCase().includes(q))
    );
    return matchesDossier;
  });
});

// Groupe du client actuellement ouvert
const currentClientGroup = computed(() => {
  if (!currentClient.value) return null;
  return clientGroups.value.find((g) => g.client.id === currentClient.value!.id) ?? null;
});

// Dossiers filtrés à l'intérieur du dossier du client
const filteredClientDossiers = computed(() => {
  if (!currentClient.value) return [];
  const group = currentClientGroup.value;
  const dossiers = group ? group.dossiers : [];
  const q = searchQuery.value.trim().toLowerCase();
  const filter = statutFilter.value;

  return dossiers.filter((d) => {
    const matchesStatut = filter === 'ALL' || d.statut === filter;
    if (!matchesStatut) return false;
    if (!q) return true;
    return [d.title, d.reference_affair].some((v) =>
      (v || '').toLowerCase().includes(q)
    );
  });
});

function formatGroupSubtitle(group: ClientGroup): string {
  const count = group.dossiers.length;
  return `${count} ${count > 1 ? 'dossiers' : 'dossier'}`;
}

function openClientFolder(client: ClientListItem) {
  currentClient.value = client;
  router.replace({ query: { ...route.query, client: client.id } });
}

function closeClientFolder() {
  currentClient.value = null;
  const q = { ...route.query };
  delete q.client;
  router.replace({ query: q });
}

function openAddRoot() {
  clientForAddDossier.value = null;
  isAddOpen.value = true;
}

function openAddForCurrentClient() {
  clientForAddDossier.value = currentClient.value;
  isAddOpen.value = true;
}

function openAddForClient(client: ClientListItem) {
  clientForAddDossier.value = client;
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

// Synchroniser avec route.query.client pour ouvrir directement un client (ex: depuis espace client)
watch(
  () => route.query.client,
  (clientId) => {
    if (clientId && typeof clientId === 'string') {
      const found = clientGroups.value.find((g) => g.client.id === clientId);
      if (found) {
        currentClient.value = found.client;
      }
    } else if (!clientId) {
      currentClient.value = null;
    }
  },
  { immediate: true }
);

watch(
  clientGroups,
  (groups) => {
    if (route.query.client && typeof route.query.client === 'string') {
      const found = groups.find((g) => g.client.id === route.query.client);
      if (found) {
        currentClient.value = found.client;
      }
    }
  }
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

/* En-tête lorsqu'on est dans le dossier d'un client */
.client-folder-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.6rem 0.85rem;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.breadcrumb-nav {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  min-width: 0;
}

.back-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.back-pill-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.breadcrumb-separator {
  color: #9ca3af;
  font-size: 0.9rem;
}

.breadcrumb-client-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.breadcrumb-client-name {
  font-weight: 600;
  color: #111827;
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.breadcrumb-client-ref {
  background: #eff6ff;
  color: var(--primary-color, #005792);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  border: 1px solid rgba(0, 87, 146, 0.15);
}

.header-right-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-create-dossier {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.9rem;
  background: var(--primary-color, #005792);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-create-dossier:hover {
  background: var(--primary-color-dark, #005380);
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
  grid-template-columns: repeat(auto-fill, minmax(245px, 1fr));
  gap: 1.25rem 0.75rem;
  width: 100%;
  padding-bottom: 2rem;
}

.size-4 {
  width: 1rem;
  height: 1rem;
}
</style>
