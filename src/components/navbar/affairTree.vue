<template>
  <aside class="tree-panel">
    <!-- En-tête -->
    <div class="tree-header">
      <h2 class="tree-title">Dossiers</h2>
      <button type="button" class="icon-btn" title="Retour aux dossiers" @click="router.push('/dashboard/affairs')">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
        </svg>
      </button>
    </div>

    <!-- Recherche -->
    <label class="search-box">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
      </svg>
      <input
        v-model="query"
        type="search"
        :placeholder="tab === 'folders' ? 'Rechercher un dossier...' : 'Rechercher un client...'"
      />
    </label>

    <!-- Onglets -->
    <div class="tabs" role="tablist">
      <button
        type="button"
        role="tab"
        class="tab"
        :class="{ active: tab === 'folders' }"
        @click="tab = 'folders'"
      >
        Dossiers
      </button>
      <button
        type="button"
        role="tab"
        class="tab"
        :class="{ active: tab === 'clients' }"
        @click="tab = 'clients'"
      >
        Clients
      </button>
    </div>

    <!-- VOLET 1 : Dossiers du client courant (dossier actif + autres dossiers du client) -->
    <nav v-if="tab === 'folders'" class="tree">
      <!-- Badge indiquant le client courant -->
      <div v-if="currentClient" class="client-context-bar">
        <div class="client-info" :title="currentClient.nom_complet">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="client-mini-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
          </svg>
          <span class="client-name">{{ currentClient.nom_complet }}</span>
        </div>
        <button
          type="button"
          class="switch-client-btn"
          title="Changer de client"
          @click="tab = 'clients'"
        >
          Clients
        </button>
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

    <!-- VOLET 2 : Clients (permet de naviguer facilement d'un client à l'autre et voir ses dossiers) -->
    <nav v-else class="tree">
      <div v-for="item in filteredClientTree" :key="item.client.id" class="tree-group">
        <!-- Ligne Client (Clic pour déplier/replier et voir ses dossiers) -->
        <button
          type="button"
          class="tree-row client-row"
          :class="{
            'is-current-client': item.client.id === currentClientId,
            'is-expanded': expandedClientIds.has(item.client.id)
          }"
          @click="toggleClient(item.client.id)"
        >
          <!-- Chevron dépliable -->
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2.2"
            stroke="currentColor"
            class="chevron-icon"
            :class="{ rotated: expandedClientIds.has(item.client.id) }"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
          </svg>

          <!-- Icône Client (morale ou physique) -->
          <svg
            v-if="item.client.type_client === 'PERSONNE_MORALE'"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.6"
            stroke="currentColor"
            class="row-icon client-icon"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21" />
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.6"
            stroke="currentColor"
            class="row-icon client-icon"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
          </svg>

          <span class="row-label client-label" :title="item.client.nom_complet">
            {{ item.client.nom_complet }}
          </span>

          <span class="row-count" :title="`${item.dossiers.length} dossier(s)`">
            {{ item.dossiers.length }}
          </span>
        </button>

        <!-- Liste des dossiers appartenant à ce client (si déplié) -->
        <ul v-if="expandedClientIds.has(item.client.id)" class="tree-children">
          <li v-for="cd in item.dossiers" :key="cd.id" class="tree-child">
            <button
              type="button"
              class="tree-row child"
              :class="{ active: cd.id === currentId }"
              :title="cd.title"
              @click="goTo(cd)"
            >
              <svg
                v-if="cd.id === currentId"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                class="row-icon"
              >
                <path d="M19.5 21a3 3 0 0 0 3-3v-4.5a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3V18a3 3 0 0 0 3 3h15ZM1.5 10.146V6a3 3 0 0 1 3-3h5.379a2.25 2.25 0 0 1 1.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 0 1 3 3v1.146A4.483 4.483 0 0 0 19.5 9h-15a4.483 4.483 0 0 0-3 1.146Z" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.6"
                stroke="currentColor"
                class="row-icon"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
              </svg>

              <span class="row-label">{{ cd.title }}</span>
              <span class="row-count">{{ cd.id === currentId ? documents.length : (cd.documents_count ?? 0) }}</span>
            </button>
          </li>

          <!-- Si aucun dossier pour ce client -->
          <li v-if="item.dossiers.length === 0" class="tree-child">
            <span class="empty-client-dossiers">Aucun dossier</span>
          </li>
        </ul>
      </div>

      <p v-if="filteredClientTree.length === 0" class="tree-empty">Aucun client trouvé</p>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useClientDossierStore, type Dossier } from '../../stores/dossierStore';
import { useClientStore, type ClientListItem } from '../../stores/clientStore';
import type { DossierDocument } from '../../stores/documentStore';
import { useAffairFolderStore, type AffairSubfolder } from '../../stores/affairFolderStore';
import affairTreeFolderItem from './affairTreeFolderItem.vue';

interface ClientTreeItem {
  client: ClientListItem;
  dossiers: Dossier[];
}

const props = withDefaults(
  defineProps<{
    currentId: string;
    currentDossier?: Dossier | null;
    documents: DossierDocument[];
    subfolders?: AffairSubfolder[];
    currentFolderId?: string | null;
  }>(),
  {
    currentDossier: null,
    subfolders: () => [],
    currentFolderId: null,
  }
);

const emit = defineEmits<{
  openDocument: [doc: DossierDocument];
  selectFolder: [folderId: string | null];
}>();

const router = useRouter();
const store = useClientDossierStore();
const clientStore = useClientStore();
const folderStore = useAffairFolderStore();

const query = ref('');
const tab = ref<'folders' | 'clients'>('folders');
const expandedFolderIds = ref<Set<string>>(new Set());
const expandedClientIds = ref<Set<string>>(new Set());

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

// Auto-déplier le client courant dans le volet Clients
watch(
  currentClientId,
  (cId) => {
    if (cId) {
      expandedClientIds.value.add(cId);
    }
  },
  { immediate: true }
);

// Dossiers du client courant (le dossier actuel + les autres dossiers de ce client)
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

// Liste arborescente de tous les clients avec leurs dossiers
const clientTreeItems = computed<ClientTreeItem[]>(() => {
  const map = new Map<string, ClientTreeItem>();

  // 1. Initialiser avec les clients enregistrés
  for (const c of clientStore.clients) {
    map.set(c.id, {
      client: c,
      dossiers: [],
    });
  }

  // 2. Associer les dossiers de allDossiers
  for (const d of store.allDossiers) {
    if (d.client?.id) {
      if (!map.has(d.client.id)) {
        map.set(d.client.id, {
          client: d.client,
          dossiers: [],
        });
      }
      const item = map.get(d.client.id)!;
      if (!item.dossiers.some((existing) => existing.id === d.id)) {
        item.dossiers.push(d);
      }
    } else {
      const key = '__sans_client__';
      if (!map.has(key)) {
        map.set(key, {
          client: {
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
          },
          dossiers: [],
        });
      }
      map.get(key)!.dossiers.push(d);
    }
  }

  // 3. S'assurer que le dossier courant figure dans son client
  if (currentDossier.value?.client?.id) {
    const cid = currentDossier.value.client.id;
    if (!map.has(cid)) {
      map.set(cid, {
        client: currentDossier.value.client,
        dossiers: [currentDossier.value],
      });
    } else {
      const item = map.get(cid)!;
      if (!item.dossiers.some((existing) => existing.id === currentDossier.value!.id)) {
        item.dossiers.push(currentDossier.value);
      }
    }
  }

  return Array.from(map.values());
});

// Filtrage du volet Clients
const filteredClientTree = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return clientTreeItems.value;
  return clientTreeItems.value.filter((item) => {
    const matchClient = [item.client.nom_complet, item.client.reference_client, item.client.email]
      .some((v) => (v || '').toLowerCase().includes(q));
    const matchDossier = item.dossiers.some((d) =>
      [d.title, d.reference_affair].some((v) => (v || '').toLowerCase().includes(q))
    );
    return matchClient || matchDossier;
  });
});

// Sous-dossiers de premier niveau (racine)
const rootSubfolders = computed(() => {
  return (props.subfolders || []).filter((sf) => !sf.parentId);
});

// Documents situés à la racine (non assignés à un sous-dossier)
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

function toggleClient(clientId: string) {
  if (expandedClientIds.value.has(clientId)) {
    expandedClientIds.value.delete(clientId);
  } else {
    expandedClientIds.value.add(clientId);
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
});
</script>

<style scoped>
.tree-panel {
  width: 280px;
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
  padding: 1rem 1rem 0.75rem;
  border-bottom: 1px solid #eceef1;
}

.tree-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #1f2937;
}

.icon-btn {
  background: none;
  border: none;
  color: #6b7280;
  padding: 0.3rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
}

.icon-btn:hover {
  background: #eceef1;
  color: #111827;
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
  font-size: 0.88rem;
  color: #111827;
}

.tabs {
  display: flex;
  margin: 0.75rem;
  padding: 3px;
  background: #eef0f2;
  border-radius: 12px;
}

.tab {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.4rem 0;
  border-radius: 9px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab.active {
  background: #ffffff;
  color: #111827;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Bandeau contexte client */
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

.switch-client-btn {
  background: transparent;
  border: none;
  font-size: 0.74rem;
  font-weight: 500;
  color: #2563eb;
  cursor: pointer;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
  flex-shrink: 0;
}

.switch-client-btn:hover {
  background: #dbe2fe;
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

/* Ligne Client dans le volet Clients */
.client-row {
  font-size: 0.86rem;
  color: #1e293b;
}

.client-row.is-current-client {
  background: #eff6ff;
  font-weight: 600;
  color: #174de1;
}

.chevron-icon {
  width: 0.85rem;
  height: 0.85rem;
  flex-shrink: 0;
  color: #d4cccc;
  transition: transform 0.2s ease;
}

.chevron-icon.rotated {
  transform: rotate(90deg);
}

.client-icon {
  width: 1.1rem;
  height: 1.1rem;
  flex-shrink: 0;
  color: #64748b;
}

.client-label {
  font-weight: 600;
  color: #1e293b;
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

.tree-row.active .row-count {
  background: #ffffff;
}

/* Lignes d'arborescence */
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

.empty-client-dossiers {
  display: block;
  font-size: 0.78rem;
  font-style: italic;
  color: #94a3b8;
  padding: 0.35rem 0.6rem;
}

.tree-empty {
  margin: 1.5rem 1rem;
  text-align: center;
  font-size: 0.85rem;
  color: #9ca3af;
}

@media (max-width: 1023px) {
  .tree-panel {
    display: none;
  }
}
</style>
