<template>
  <aside class="tree-panel">
    <!-- En-tête -->
    <div class="tree-header">
      <div class="header-title-box">
        <h2 class="tree-title">{{ tab === 'folders' ? 'Dossiers' : 'Historique' }}</h2>
        <span v-if="tab === 'sira' && currentDossier" class="header-dossier-pill" :title="currentDossier.title">
          {{ currentDossier.reference_affair || currentDossier.title }}
        </span>
      </div>

      <div class="header-actions-right">
        <!-- Bouton retour aux affaires -->
        <button type="button" class="icon-btn" title="Retour aux dossiers" @click="router.push('/dashboard/affairs')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Recherche (uniquement pour l'arborescence des dossiers) -->
    <label v-if="tab === 'folders'" class="search-box">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
      </svg>
      <input
        v-model="query"
        type="search"
        placeholder="Rechercher un dossier..."
      />
    </label>

    <!-- Onglets : Dossiers / Suivi SIRA (style Git) -->
    <div class="tabs" role="tablist">
      <button
        type="button"
        role="tab"
        class="tab"
        :class="{ active: tab === 'folders' }"
        @click="switchTab('folders')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="tab-btn-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
        </svg>
        <span>Dossiers</span>
      </button>

      <button
        type="button"
        role="tab"
        class="tab"
        :class="{ active: tab === 'sira' }"
        @click="switchTab('sira')"
      >
        <!-- Icône Git branch -->
        <svg class="tab-btn-icon" viewBox="0 0 16 16" fill="currentColor">
          <path d="M11.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5zm-2.25.75a2.25 2.25 0 1 1 3 2.122V6A2.5 2.5 0 0 1 10 8.5H6a1 1 0 0 0-1 1v1.128a2.251 2.251 0 1 1-1.5 0V5.372a2.25 2.25 0 1 1 1.5 0v1.836A2.493 2.493 0 0 1 6 7h4a1 1 0 0 0 1-1v-.628A2.25 2.25 0 0 1 9.5 3.25zM4.25 12a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5zM3.5 3.25a.75.75 0 1 1 1.5 0 .75.75 0 0 1-1.5 0z" />
        </svg>
        <span>Historique</span>
      </button>
    </div>

    <!-- VOLET 1 : Arborescence des Dossiers -->
    <nav v-if="tab === 'folders'" class="tree">
      <!-- Badge indiquant le client courant -->
      <div v-if="currentClient" class="client-context-bar">
        <div class="client-info" :title="currentClient.nom_complet">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="client-mini-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
          </svg>
          <span class="client-name">{{ currentClient.nom_complet }}</span>
        </div>
      </div>

      <!-- Liste des dossiers appartenant au client actuel -->
      <div v-for="d in filteredClientDossiers" :key="d.id" class="tree-group">
        <button
          type="button"
          class="tree-row"
          :class="{ active: d.id === currentId && currentFolderId === null }"
          @click="goTo(d)"
        >
          <svg
            v-if="d.id === currentId"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            class="row-icon"
          >
            <path d="M19.5 21a3 3 0 0 0 3-3v-4.5a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3V18a3 3 0 0 0 3 3h15ZM1.5 10.146V6a3 3 0 0 1 3-3h5.379a2.25 2.25 0 0 1 1.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 0 1 3 3v1.146A4.483 4.483 0 0 0 19.5 9h-15a4.483 4.483 0 0 0-3 1.146Z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="row-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
          </svg>
          <span class="row-label">{{ d.title }}</span>
          <span
            v-if="typeof d.progression === 'number'"
            class="sira-mini-pill"
            :title="`Progression SIRA : ${d.progression}%`"
          >
            {{ d.progression }}%
          </span>
          <span class="row-count">{{ d.id === currentId ? documents.length : (d.documents_count ?? 0) }}</span>
        </button>

        <!-- Sous-dossiers et documents du dossier actuellement ouvert -->
        <ul v-if="d.id === currentId" class="tree-children">
          <!-- Sous-dossiers de la racine (dépliables) -->
          <affairTreeFolderItem
            v-for="sf in rootSubfolders"
            :key="sf.id"
            :folder="sf"
            :allSubfolders="subfolders || []"
            :allDocuments="documents"
            :docFolderMap="folderStore.docFolderMap"
            :currentFolderId="currentFolderId"
            :expandedFolderIds="expandedFolderIds"
            @selectFolder="onSelectFolder"
            @openDocument="emit('openDocument', $event)"
            @toggleFolder="toggleFolder"
          />

          <!-- Documents de la racine -->
          <li v-for="doc in rootDocuments" :key="doc.id" class="tree-child">
            <button type="button" class="tree-row child" :title="doc.title" @click="emit('openDocument', doc)">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="row-icon" :class="extClass(doc.extension)">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
              <span class="row-label">{{ doc.title }}</span>
            </button>
          </li>
        </ul>
      </div>

      <p v-if="filteredClientDossiers.length === 0" class="tree-empty">Aucun dossier trouvé pour ce client</p>
    </nav>

    <!-- VOLET 2 : GRAPH GIT SIRA (Composant extrait et optimisé) -->
    <affairSiraGitGraph
      v-else
      :currentId="currentId"
      :currentDossier="currentDossier"
      :documents="documents"
      @openDocument="emit('openDocument', $event)"
    />
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useClientDossierStore, type Dossier } from '../../stores/dossierStore';
import { useClientStore, type ClientListItem } from '../../stores/clientStore';
import type { DossierDocument } from '../../stores/documentStore';
import { useAffairFolderStore, type AffairSubfolder } from '../../stores/affairFolderStore';
import { useSiraStore } from '../../stores/siraStore';
import affairTreeFolderItem from './affairTreeFolderItem.vue';
import affairSiraGitGraph from './affairSiraGitGraph.vue';

const props = withDefaults(
  defineProps<{
    currentId: string;
    currentDossier?: Dossier | null;
    documents: DossierDocument[];
    subfolders?: AffairSubfolder[];
    currentFolderId?: string | null;
    activeTab?: 'folders' | 'sira';
  }>(),
  {
    currentDossier: null,
    subfolders: () => [],
    currentFolderId: null,
    activeTab: 'folders',
  }
);

const emit = defineEmits<{
  (e: 'openDocument', doc: DossierDocument): void;
  (e: 'selectFolder', folderId: string | null): void;
  (e: 'update:activeTab', tab: 'folders' | 'sira'): void;
}>();

const router = useRouter();
const store = useClientDossierStore();
const clientStore = useClientStore();
const folderStore = useAffairFolderStore();
const siraStore = useSiraStore();

const query = ref('');
const tab = ref<'folders' | 'sira'>(props.activeTab || 'folders');
const expandedFolderIds = ref<Set<string>>(new Set());

watch(
  () => props.activeTab,
  (newTab) => {
    if (newTab && newTab !== tab.value) {
      tab.value = newTab;
    }
  }
);

function switchTab(newTab: 'folders' | 'sira') {
  tab.value = newTab;
  emit('update:activeTab', newTab);
  if (newTab === 'sira' && props.currentId) {
    siraStore.fetchHistory(props.currentId);
  }
}

// Dossier courant résolu
const currentDossier = computed<Dossier | null>(() => {
  if (props.currentDossier) return props.currentDossier;
  return store.allDossiers.find((d) => d.id === props.currentId) || null;
});

// Identifiant du client courant
const currentClientId = computed<string | null>(() => {
  return currentDossier.value?.client?.id || null;
});

// Client courant
const currentClient = computed<ClientListItem | null>(() => {
  if (currentDossier.value?.client) return currentDossier.value.client;
  if (!currentClientId.value) return null;
  return clientStore.clients.find((c) => c.id === currentClientId.value) || null;
});

// Dossiers du client courant
const clientDossiers = computed<Dossier[]>(() => {
  const cId = currentClientId.value;
  if (!cId) {
    return currentDossier.value ? [currentDossier.value] : [];
  }
  const list = store.allDossiers.filter((d) => d.client?.id === cId);
  if (currentDossier.value && !list.some((d) => d.id === currentDossier.value!.id)) {
    list.unshift(currentDossier.value);
  }
  return list;
});

// Filtrage de la liste des dossiers du client courant
const filteredClientDossiers = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return clientDossiers.value;
  return clientDossiers.value.filter((d) =>
    [d.title, d.reference_affair, d.type_affair].some((v) => (v || '').toLowerCase().includes(q))
  );
});

// Sous-dossiers de premier niveau (racine)
const rootSubfolders = computed(() => {
  return (props.subfolders || []).filter((sf) => !sf.parentId);
});

// Documents situés à la racine
const rootDocuments = computed(() => {
  const subfolderIds = new Set((props.subfolders || []).map((sf) => sf.id));
  return props.documents.filter((doc) => {
    const assignedFolderId = folderStore.docFolderMap[doc.id];
    return !assignedFolderId || !subfolderIds.has(assignedFolderId);
  });
});

// Dépliage automatique du chemin de sous-dossiers
watch(
  () => props.currentFolderId,
  (newId) => {
    if (newId) {
      const path = folderStore.getFolderPath(newId);
      for (const p of path) {
        expandedFolderIds.value.add(p.id);
      }
      expandedFolderIds.value.add(newId);
    }
  },
  { immediate: true }
);

function toggleFolder(folderId: string) {
  if (expandedFolderIds.value.has(folderId)) {
    expandedFolderIds.value.delete(folderId);
  } else {
    expandedFolderIds.value.add(folderId);
  }
}

function onSelectFolder(folderId: string) {
  emit('selectFolder', folderId);
  expandedFolderIds.value.add(folderId);
}

function goTo(d: Dossier) {
  if (d.id !== props.currentId) {
    router.push(`/dashboard/affairs/${d.id}`);
  } else {
    emit('selectFolder', null);
  }
}

function extClass(ext: string) {
  const e = (ext || '').toLowerCase();
  if (e === 'pdf') return 'is-pdf';
  if (['doc', 'docx', 'odt', 'rtf', 'txt'].includes(e)) return 'is-word';
  return '';
}

onMounted(async () => {
  if (store.allDossiers.length === 0) store.fetchAllDossiers();
  if (clientStore.clients.length === 0) clientStore.fetchClients();
  if (!folderStore.isLoaded) folderStore.loadStore();
  if (tab.value === 'sira' && props.currentId) {
    siraStore.fetchHistory(props.currentId);
  }
});
</script>

<style scoped>
.tree-panel {
  width: 290px;
  flex-shrink: 0;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fafafa;
  border-right: 1px solid #e5e7eb;
}

.tree-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1rem 0.75rem;
  border-bottom: 1px solid #eceef1;
}

.header-title-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.tree-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #111827;
  white-space: nowrap;
}

.header-dossier-pill {
  font-size: 0.7rem;
  font-weight: 600;
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 999px;
  padding: 0.1rem 0.45rem;
  max-width: 105px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-actions-right {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.icon-btn {
  background: none;
  border: none;
  color: #6b7280;
  padding: 0.35rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.icon-btn:hover:not(:disabled) {
  background: #eceef1;
  color: #111827;
}

.icon-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 1rem;
  color: #9ca3af;
  border-bottom: 1px solid #eceef1;
}

.search-box input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.85rem;
  color: #111827;
}

.tabs {
  display: flex;
  margin: 0.75rem 0.75rem 0.5rem;
  padding: 3px;
  background: #eef0f2;
  border-radius: 12px;
  gap: 2px;
}

.tab {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.45rem 0.4rem;
  border-radius: 9px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  transition: all 0.2s ease;
}

.tab:hover {
  color: #1e293b;
}

.tab.active {
  background: #ffffff;
  color: #1d4ed8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.tab-btn-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

/* ==================== VOLET 1 : DOSSIERS ==================== */
.client-context-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.45rem 0.6rem;
  margin-bottom: 0.4rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.client-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  min-width: 0;
  flex: 1;
}

.client-mini-icon {
  width: 14px;
  height: 14px;
  color: #64748b;
  flex-shrink: 0;
}

.client-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tree {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0 0.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tree-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.6rem;
  border: none;
  background: transparent;
  border-radius: 10px;
  font-size: 0.88rem;
  color: #1f2937;
  cursor: pointer;
  text-align: left;
  transition: background-color 0.15s ease;
}

.tree-row:hover {
  background: #eef0f2;
}

.tree-row.active {
  background: #e9ebee;
  font-weight: 600;
  color: #2563eb;
}

.row-icon {
  width: 1.1rem;
  height: 1.1rem;
  flex-shrink: 0;
  color: #6b7280;
}

.row-icon.is-pdf { color: #ef4444; }
.row-icon.is-word { color: #3b82f6; }

.row-label {
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-count {
  font-size: 0.78rem;
  font-weight: 500;
  color: #4b5563;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  padding: 0.05rem 0.55rem;
  min-width: 1.6rem;
  text-align: center;
}

.sira-mini-pill {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
  flex-shrink: 0;
  line-height: 1.1;
}

.tree-row.active .row-count {
  background: #ffffff;
}

.tree-children {
  list-style: none;
  margin: 0 0 0 1.25rem;
  padding: 0 0 0 0.4rem;
  border-left: 1px solid #d1d5db;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tree-child {
  position: relative;
}

.tree-children > .tree-child::before {
  content: '';
  position: absolute;
  left: -0.4rem;
  top: 1rem;
  width: 0.5rem;
  border-top: 1px solid #d1d5db;
}

.tree-row.child {
  font-size: 0.85rem;
}

.tree-empty {
  margin: 1.5rem 1rem;
  text-align: center;
  font-size: 0.85rem;
  color: #9ca3af;
}

.size-4 {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 1023px) {
  .tree-panel {
    display: none;
  }
}
</style>
