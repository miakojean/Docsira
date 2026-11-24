<template>
  <div class="main-section trash-section gap-3">
    <!-- Onglets de catégories : Dossiers, Documents, Clients -->
    <div class="trash-topbar">
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

    <!-- ===================== ONGLET 1 : DOSSIERS ===================== -->
    <template v-if="activeCategory === 'dossiers'">
      <div v-if="dossierStore.isLoading && dossierStore.trashDossiers.length === 0" class="state-center">
        <LogoLoader size="lg" label="Chargement des dossiers supprimés..." />
      </div>

      <div v-else-if="dossierStore.trashDossiers.length > 0" class="content-container">
        <div v-if="filteredDossiers.length > 0" class="flex-1 flex flex-col justify-between gap-4">
          <div class="table-card">
            <table class="clients-table">
              <thead>
                <tr>
                  <th>Référence</th>
                  <th>Titre du dossier</th>
                  <th>Client</th>
                  <th>Progression</th>
                  <th>Statut</th>
                  <th>Mis à la corbeille le</th>
                  <th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="dossier in paginatedDossiers" :key="dossier.id">
                  <td class="ref">{{ dossier.reference_affair }}</td>
                  <td class="name">{{ dossier.title }}</td>
                  <td>{{ dossier.client?.nom_complet || '—' }}</td>
                  <td>
                    <span class="badge prospect">{{ dossier.progression ?? 10 }}%</span>
                  </td>
                  <td>
                    <span class="badge inactif">{{ formatDossierStatut(dossier.statut) }}</span>
                  </td>
                  <td class="muted">{{ formatDate(dossier.deleted_at || dossier.creation_date) }}</td>
                  <td class="actions-cell">
                    <button class="action-btn" @click.stop="toggleMenu('dossier', dossier, $event)">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <Pagination
            v-model="currentPage"
            :totalItems="filteredDossiers.length"
            :pageSize="pageSize"
            :hideOnSinglePage="false"
          />
        </div>

        <div v-else class="state-center">
          <emptyCards
            title="Corbeille — Dossiers"
            :mainText="`Aucun dossier trouvé pour '${searchQuery}'`"
            subtitle="Vérifiez l'orthographe ou essayez un autre terme."
            :showAddButton="false"
          />
        </div>
      </div>

      <div v-else class="state-center">
        <emptyCards
          title="Corbeille — Dossiers"
          mainText="Aucun dossier dans la corbeille."
          subtitle="Les dossiers supprimés apparaîtront ici."
          :showAddButton="false"
        />
      </div>
    </template>

    <!-- ===================== ONGLET 2 : DOCUMENTS ===================== -->
    <template v-else-if="activeCategory === 'documents'">
      <div v-if="docStore.isLoading && docStore.trashDocuments.length === 0" class="state-center">
        <LogoLoader size="lg" label="Chargement des documents supprimés..." />
      </div>

      <div v-else-if="docStore.trashDocuments.length > 0" class="content-container">
        <div v-if="filteredDocuments.length > 0" class="flex-1 flex flex-col justify-between gap-4">
          <div class="table-card">
            <table class="clients-table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Format</th>
                  <th>Dossier rattaché</th>
                  <th>Catégorie SIRA</th>
                  <th>Taille</th>
                  <th>Mis à la corbeille le</th>
                  <th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="doc in paginatedDocuments" :key="doc.id">
                  <td class="name">{{ doc.title || doc.file_name }}</td>
                  <td>
                    <span class="ext-pill">{{ (doc.extension || 'DOC').toUpperCase() }}</span>
                  </td>
                  <td>
                    <div class="name">{{ doc.affair_title || 'Dossier' }}</div>
                    <div class="muted ref">{{ doc.affair_reference || '' }}</div>
                  </td>
                  <td>
                    <span class="badge prospect">{{ getSiraCategoryMeta(doc.category).label }}</span>
                  </td>
                  <td class="muted">{{ formatBytes(doc.size) }}</td>
                  <td class="muted">{{ formatDate(doc.deleted_at || doc.uploaded_at) }}</td>
                  <td class="actions-cell">
                    <button class="action-btn" @click.stop="toggleMenu('document', doc, $event)">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <Pagination
            v-model="currentPage"
            :totalItems="filteredDocuments.length"
            :pageSize="pageSize"
            :hideOnSinglePage="false"
          />
        </div>

        <div v-else class="state-center">
          <emptyCards
            title="Corbeille — Documents"
            :mainText="`Aucun document trouvé pour '${searchQuery}'`"
            subtitle="Vérifiez l'orthographe ou essayez un autre terme."
            :showAddButton="false"
          />
        </div>
      </div>

      <div v-else class="state-center">
        <emptyCards
          title="Corbeille — Documents"
          mainText="Aucun document dans la corbeille."
          subtitle="Les documents supprimés apparaîtront ici."
          :showAddButton="false"
        />
      </div>
    </template>

    <!-- ===================== ONGLET 3 : CLIENTS ===================== -->
    <template v-else>
      <div v-if="clientStore.isLoading && clientStore.trashClients.length === 0" class="state-center">
        <LogoLoader size="lg" label="Chargement des clients supprimés..." />
      </div>

      <div v-else-if="clientStore.trashClients.length > 0" class="content-container">
        <div v-if="filteredClients.length > 0" class="flex-1 flex flex-col justify-between gap-4">
          <div class="table-card">
            <table class="clients-table">
              <thead>
                <tr>
                  <th>Référence</th>
                  <th>Client</th>
                  <th>Type</th>
                  <th>Contact</th>
                  <th>Localisation</th>
                  <th>Statut</th>
                  <th>Créé le</th>
                  <th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="client in paginatedClients" :key="client.id">
                  <td class="ref">{{ client.reference_client }}</td>
                  <td class="name">{{ client.nom_complet }}</td>
                  <td>{{ client.type_client === 'PERSONNE_MORALE' ? 'Personne morale' : 'Personne physique' }}</td>
                  <td>
                    <div>{{ client.telephone_1 }}</div>
                    <div class="muted">{{ client.email }}</div>
                  </td>
                  <td>{{ [client.ville, client.pays].filter(Boolean).join(', ') || '—' }}</td>
                  <td><span class="badge" :class="client.statut.toLowerCase()">{{ statutLabels[client.statut] }}</span></td>
                  <td class="muted">{{ formatDate(client.date_creation) }}</td>
                  <td class="actions-cell">
                    <button class="action-btn" @click.stop="toggleMenu('client', client, $event)">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <Pagination
            v-model="currentPage"
            :totalItems="filteredClients.length"
            :pageSize="pageSize"
            :hideOnSinglePage="false"
          />
        </div>

        <div v-else class="state-center">
          <emptyCards
            title="Corbeille — Clients"
            :mainText="`Aucun client trouvé pour '${searchQuery}'`"
            subtitle="Vérifiez l'orthographe ou essayez un autre terme."
            :showAddButton="false"
          />
        </div>
      </div>

      <div v-else class="state-center">
        <emptyCards
          title="Corbeille — Clients"
          mainText="Aucun client dans la corbeille."
          subtitle="Aucun client n'a été supprimé."
          :showAddButton="false"
        />
      </div>
    </template>

    <!-- ===================== MODALES ===================== -->
    <viewClientModale :isOpen="isViewClientOpen" :client="selectedClient" @close="isViewClientOpen = false" />

    <detailsModale
      :isOpen="isViewDossierOpen"
      :item="dossierDetailsItem"
      @close="isViewDossierOpen = false"
      @action="isViewDossierOpen = false"
    />

    <filePreviewModale
      :preview="docPreview"
      @close="closeDocPreview"
      @download="downloadTrashDoc"
    />

    <restoreModale
      :isOpen="isRestoreOpen"
      :isLoading="isRestoring"
      :isSuccess="isRestoreSuccess"
      :itemName="targetDisplayName"
      :title="restoreCopy.title"
      :description="restoreCopy.description"
      :subtext="restoreCopy.subtext"
      :successTitle="restoreCopy.successTitle"
      :successSubtitle="restoreCopy.successSubtitle"
      @close="isRestoreOpen = false; isRestoreSuccess = false"
      @restore="confirmRestore"
    />

    <deleteModale
      :isOpen="isPermanentDeleteOpen"
      :isLoading="isPermanentDeleting"
      :isSuccess="isPermanentDeleteSuccess"
      :itemName="targetDisplayName"
      :isFolder="actionKind === 'dossier'"
      :title="deleteCopy.title"
      :description="deleteCopy.description"
      subtext="Cette action est irréversible."
      :successTitle="deleteCopy.successTitle"
      :successSubtitle="deleteCopy.successSubtitle"
      @close="isPermanentDeleteOpen = false; isPermanentDeleteSuccess = false"
      @delete="confirmPermanentDelete"
    />

    <errorModale
      :isOpen="isErrorOpen"
      modaleTitle="Action impossible"
      :title="errorTitle"
      :subtitle="errorSubtitle"
      actionText="Compris"
      @close="isErrorOpen = false"
      @handleEvent="isErrorOpen = false"
    />

    <!-- Menu d'actions contextuel (Teleport) -->
    <Teleport to="body">
      <div v-if="activeMenuId" class="dropdown-menu" :style="menuStyle" @click.stop>
        <ul>
          <li @click.stop="handleViewActive">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
            </svg>
            {{ activeKind === 'document' ? 'Visualiser' : 'Voir' }}
          </li>
          <li class="danger" @click.stop="openRestoreModal">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
            Restaurer
          </li>
          <li class="danger2" @click.stop="openPermanentDeleteModal">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
            Supprimer définitivement
          </li>
        </ul>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { save as saveDialog } from '@tauri-apps/plugin-dialog';
import { writeFile } from '@tauri-apps/plugin-fs';
import mammoth from 'mammoth';
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
import viewClientModale from '../../modale/viewClientModale.vue';
import detailsModale, { type ItemDetails } from '../../modale/detailsModale.vue';
import filePreviewModale, { type PreviewData } from '../../modale/filePreviewModale.vue';
import restoreModale from '../../modale/restoreModale.vue';
import deleteModale from '../../modale/deleteModale.vue';
import errorModale from '../../modale/errorModale.vue';
import LogoLoader from '../../tools/LogoLoader.vue';
import Pagination from '../../tools/Pagination.vue';
import { useClientStore } from '../../../stores/clientStore';
import { useClientDossierStore, type Dossier } from '../../../stores/dossierStore';
import { useDocumentStore, type DossierDocument } from '../../../stores/documentStore';
import { getSiraCategoryMeta } from '../../../stores/siraStore';
import { DOCUMENT_MIME_BY_EXT } from '../../../helpers/documentFormats';

type TrashCategory = 'dossiers' | 'documents' | 'clients';
type TrashItemKind = 'dossier' | 'document' | 'client';

const route = useRoute();
const router = useRouter();
const clientStore = useClientStore();
const dossierStore = useClientDossierStore();
const docStore = useDocumentStore();

const activeCategory = ref<TrashCategory>('dossiers');
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = 10;

watch([activeCategory, searchQuery], () => {
  currentPage.value = 1;
});

const categories = computed(() => [
  { key: 'dossiers' as const, label: 'Dossiers', count: dossierStore.trashDossiers.length },
  { key: 'documents' as const, label: 'Documents', count: docStore.trashDocuments.length },
  { key: 'clients' as const, label: 'Clients', count: clientStore.trashClients.length },
]);

const headerTitle = computed(() => {
  if (activeCategory.value === 'dossiers') return 'Corbeille — Dossiers';
  if (activeCategory.value === 'documents') return 'Corbeille — Documents';
  return 'Corbeille — Clients';
});

const searchPlaceholder = computed(() => {
  if (activeCategory.value === 'dossiers') return 'Rechercher un dossier supprimé...';
  if (activeCategory.value === 'documents') return 'Rechercher un document supprimé...';
  return 'Rechercher un client supprimé...';
});

function selectCategory(cat: TrashCategory) {
  activeCategory.value = cat;
  searchQuery.value = '';
  closeMenu();
  router.replace({ query: { ...route.query, tab: cat } });
}

watch(
  () => route.query.tab,
  (tab) => {
    if (tab === 'clients' || tab === 'documents' || tab === 'dossiers') {
      activeCategory.value = tab;
    }
  },
  { immediate: true }
);

const statutLabels: Record<string, string> = {
  ACTIF: 'Actif',
  INACTIF: 'Inactif',
  PROSPECT: 'Prospect',
  ARCHIVE: 'Archivé',
};

const filteredDossiers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return dossierStore.trashDossiers;
  return dossierStore.trashDossiers.filter((d) =>
    [d.title, d.reference_affair, d.client?.nom_complet, d.type_affair].some((v) =>
      (v || '').toLowerCase().includes(q)
    )
  );
});

const filteredDocuments = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return docStore.trashDocuments;
  return docStore.trashDocuments.filter((doc) =>
    [doc.title, doc.file_name, doc.extension, doc.affair_title, doc.affair_reference].some((v) =>
      (v || '').toLowerCase().includes(q)
    )
  );
});

const filteredClients = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return clientStore.trashClients;
  return clientStore.trashClients.filter((c) =>
    [c.nom_complet, c.reference_client, c.email, c.telephone_1, c.ville].some((v) =>
      (v || '').toLowerCase().includes(q)
    )
  );
});

const paginatedDossiers = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return filteredDossiers.value.slice(start, start + pageSize);
});

const paginatedDocuments = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return filteredDocuments.value.slice(start, start + pageSize);
});

const paginatedClients = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return filteredClients.value.slice(start, start + pageSize);
});

function formatDate(value?: string | null) {
  if (!value) return '—';
  return new Date(value).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function formatDossierStatut(statut?: string) {
  if (!statut) return 'En cours';
  return statut.replace(/_/g, ' ').toLowerCase();
}

function formatBytes(bytes?: number) {
  if (!bytes || bytes <= 0) return '0 Ko';
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} Ko`;
  return `${(kb / 1024).toFixed(1)} Mo`;
}

// ---------- Menu contextuel ----------
const activeMenuId = ref<string | null>(null);
const activeKind = ref<TrashItemKind>('dossier');
const activeItem = ref<any>(null);
const menuStyle = ref({ top: '0px', left: '0px' });

function toggleMenu(kind: TrashItemKind, item: any, event: MouseEvent) {
  if (activeMenuId.value === item.id) {
    closeMenu();
    return;
  }
  activeMenuId.value = item.id;
  activeKind.value = kind;
  activeItem.value = item;

  const button = event.currentTarget as HTMLElement;
  const rect = button.getBoundingClientRect();
  menuStyle.value = {
    top: `${rect.top + window.scrollY + rect.height / 2}px`,
    left: `${rect.left + window.scrollX - 195 - 8}px`,
  };
}

function closeMenu() {
  activeMenuId.value = null;
  activeItem.value = null;
}

// ---------- Voir / Visualiser ----------
const isViewClientOpen = ref(false);
const selectedClient = ref<any>(null);

const isViewDossierOpen = ref(false);
const selectedDossier = ref<Dossier | null>(null);

const dossierDetailsItem = computed<ItemDetails>(() => {
  const d = selectedDossier.value;
  if (!d) return { isFolder: true, name: 'Dossier' };
  return {
    isFolder: true,
    name: d.title,
    path: d.reference_affair ? `Corbeille / ${d.reference_affair}` : 'Corbeille',
    size: `${d.documents_count ?? 0} document(s)`,
    fileCount: d.documents_count ?? 0,
    owner: d.client?.nom_complet || 'Client',
    createdBy: d.created_by_name || undefined,
    createdAt: d.creation_date ? formatDate(d.creation_date) : undefined,
    updatedAt: 'Dans la corbeille',
    isShared: false,
  };
});

const docPreview = ref<PreviewData | null>(null);

function closeDocPreview() {
  if (docPreview.value?.url) URL.revokeObjectURL(docPreview.value.url);
  docPreview.value = null;
}

async function previewTrashDoc(doc: DossierDocument) {
  const ext = (doc.extension || '').toLowerCase();
  const isImg = ['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg'].includes(ext);
  const isPdf = ext === 'pdf';
  const isDocx = ext === 'docx';

  closeDocPreview();
  if (!isImg && !isPdf && !isDocx) {
    docPreview.value = {
      title: doc.title,
      kind: 'unsupported',
      message: "L'aperçu intégré n'est pas disponible pour ce format.",
      doc,
    };
    return;
  }

  docPreview.value = { title: doc.title, kind: 'loading', doc };
  const blob = await docStore.fetchFileBlob(doc.id);
  if (!blob) {
    closeDocPreview();
    return;
  }

  if (isImg) {
    const typed = DOCUMENT_MIME_BY_EXT[ext] ? new Blob([blob], { type: DOCUMENT_MIME_BY_EXT[ext] }) : blob;
    docPreview.value = { title: doc.title, kind: 'image', url: URL.createObjectURL(typed), doc };
  } else if (isPdf) {
    docPreview.value = { title: doc.title, kind: 'pdf', data: await blob.arrayBuffer(), doc };
  } else if (isDocx) {
    try {
      const result = await mammoth.convertToHtml({ arrayBuffer: await blob.arrayBuffer() });
      docPreview.value = { title: doc.title, kind: 'docx', html: result.value, doc };
    } catch {
      docPreview.value = {
        title: doc.title,
        kind: 'unsupported',
        message: 'Impossible de prévisualiser ce fichier Word.',
        doc,
      };
    }
  }
}

async function downloadTrashDoc(doc: DossierDocument) {
  try {
    const target = await saveDialog({ defaultPath: doc.file_name || doc.title });
    if (!target) return;
    const blob = await docStore.fetchFileBlob(doc.id);
    if (!blob) return;
    await writeFile(target, new Uint8Array(await blob.arrayBuffer()));
  } catch (err) {
    console.error(err);
  }
}

function handleViewActive() {
  const item = activeItem.value;
  const kind = activeKind.value;
  closeMenu();
  if (!item) return;

  if (kind === 'client') {
    selectedClient.value = item;
    isViewClientOpen.value = true;
  } else if (kind === 'dossier') {
    selectedDossier.value = item;
    isViewDossierOpen.value = true;
  } else if (kind === 'document') {
    void previewTrashDoc(item);
  }
}

// ---------- Restauration & Suppression définitive ----------
const actionKind = ref<TrashItemKind>('dossier');
const actionTarget = ref<any>(null);

const isRestoreOpen = ref(false);
const isRestoring = ref(false);
const isRestoreSuccess = ref(false);

const isPermanentDeleteOpen = ref(false);
const isPermanentDeleting = ref(false);
const isPermanentDeleteSuccess = ref(false);

const isErrorOpen = ref(false);
const errorTitle = ref('');
const errorSubtitle = ref('');

const targetDisplayName = computed(() => {
  const t = actionTarget.value;
  if (!t) return 'cet élément';
  if (actionKind.value === 'client') return t.nom_complet || 'ce client';
  if (actionKind.value === 'dossier') return t.title || 'ce dossier';
  return t.title || t.file_name || 'ce document';
});

const restoreCopy = computed(() => {
  if (actionKind.value === 'dossier') {
    return {
      title: 'Restaurer le dossier',
      description: 'Êtes-vous sûr de vouloir restaurer ce dossier ?',
      subtext: 'Il réapparaîtra dans votre Workspace.',
      successTitle: 'Dossier restauré',
      successSubtitle: 'Le dossier a été restauré avec succès.',
    };
  }
  if (actionKind.value === 'document') {
    return {
      title: 'Restaurer le document',
      description: 'Êtes-vous sûr de vouloir restaurer ce document ?',
      subtext: "Il réapparaîtra dans son dossier d'origine.",
      successTitle: 'Document restauré',
      successSubtitle: 'Le document a été restauré avec succès.',
    };
  }
  return {
    title: 'Restaurer le client',
    description: 'Êtes-vous sûr de vouloir restaurer ce client ?',
    subtext: 'Il réapparaîtra dans votre liste des clients actifs.',
    successTitle: 'Client restauré',
    successSubtitle: 'Le client a été restauré avec succès.',
  };
});

const deleteCopy = computed(() => {
  if (actionKind.value === 'dossier') {
    return {
      title: 'Supprimer définitivement le dossier',
      description: 'Êtes-vous sûr de vouloir supprimer définitivement ce dossier et ses documents ?',
      successTitle: 'Dossier supprimé',
      successSubtitle: 'Le dossier a été supprimé définitivement.',
    };
  }
  if (actionKind.value === 'document') {
    return {
      title: 'Supprimer définitivement le document',
      description: 'Êtes-vous sûr de vouloir supprimer définitivement ce document ?',
      successTitle: 'Document supprimé',
      successSubtitle: 'Le document a été supprimé définitivement.',
    };
  }
  return {
    title: 'Suppression définitive',
    description: 'Êtes-vous sûr de vouloir supprimer définitivement ce client ?',
    successTitle: 'Client supprimé',
    successSubtitle: 'Le client a été supprimé définitivement.',
  };
});

function openRestoreModal() {
  actionKind.value = activeKind.value;
  actionTarget.value = activeItem.value;
  isRestoreSuccess.value = false;
  closeMenu();
  isRestoreOpen.value = true;
}

function openPermanentDeleteModal() {
  actionKind.value = activeKind.value;
  actionTarget.value = activeItem.value;
  isPermanentDeleteSuccess.value = false;
  closeMenu();
  isPermanentDeleteOpen.value = true;
}

async function confirmRestore() {
  if (!actionTarget.value) return;
  isRestoring.value = true;
  let ok = false;
  if (actionKind.value === 'client') {
    ok = await clientStore.restoreClient(actionTarget.value.id);
  } else if (actionKind.value === 'dossier') {
    ok = await dossierStore.restoreTrashDossier(actionTarget.value.id);
  } else {
    ok = await docStore.restoreTrashDocument(actionTarget.value.id);
  }
  isRestoring.value = false;
  if (ok) {
    isRestoreSuccess.value = true;
  } else {
    isRestoreOpen.value = false;
    errorTitle.value = 'Restauration impossible';
    errorSubtitle.value =
      clientStore.errorMessage || dossierStore.errorMessage || docStore.errorMessage || 'Une erreur est survenue.';
    isErrorOpen.value = true;
  }
}

async function confirmPermanentDelete() {
  if (!actionTarget.value) return;
  isPermanentDeleting.value = true;
  let ok = false;
  let errMsg = '';
  if (actionKind.value === 'client') {
    ok = await clientStore.deleteClientPermanently(actionTarget.value.id);
    errMsg = clientStore.errorMessage;
  } else if (actionKind.value === 'dossier') {
    ok = await dossierStore.deleteDossierPermanently(actionTarget.value.id);
    errMsg = dossierStore.errorMessage;
  } else {
    ok = await docStore.deleteDocumentPermanently(actionTarget.value.id);
    errMsg = docStore.errorMessage;
  }
  isPermanentDeleting.value = false;

  if (ok) {
    isPermanentDeleteSuccess.value = true;
  } else {
    isPermanentDeleteOpen.value = false;
    errorTitle.value = 'Action refusée';
    errorSubtitle.value = errMsg || "Vous n'êtes pas autorisé à réaliser cette action.";
    isErrorOpen.value = true;
  }
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement;
  if (!target.closest('.dropdown-menu') && !target.closest('.action-btn')) {
    closeMenu();
  }
}

onMounted(async () => {
  document.addEventListener('click', handleClickOutside);
  await Promise.all([
    dossierStore.fetchTrashDossiers(),
    docStore.fetchTrashDocuments(),
    clientStore.fetchTrashClients(),
  ]);
  if (!route.query.tab) {
    if (dossierStore.trashDossiers.length > 0) activeCategory.value = 'dossiers';
    else if (docStore.trashDocuments.length > 0) activeCategory.value = 'documents';
    else if (clientStore.trashClients.length > 0) activeCategory.value = 'clients';
  }
});

onUnmounted(() => {
  closeDocPreview();
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.main-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.trash-topbar {
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

.content-container {
  padding: 1rem 0.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.state-center {
  flex: 1;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.table-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  overflow-x: auto;
}

.clients-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  color: #374151;
}

.clients-table th {
  text-align: left;
  padding: 0.9rem 1rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #9ca3af;
  border-bottom: 1px solid #f3f4f6;
  white-space: nowrap;
}

.clients-table td {
  padding: 0.9rem 1rem;
  border-bottom: 1px solid #f9fafb;
  vertical-align: middle;
}

.clients-table tbody tr {
  transition: background 0.15s ease;
}

.clients-table tbody tr:hover {
  background: #f9fafb;
}

.ref {
  font-family: monospace;
  color: #6b7280;
}

.name {
  font-weight: 600;
  color: #111827;
}

.muted {
  color: #9ca3af;
  font-size: 0.8rem;
}

.ext-pill {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.18rem 0.5rem;
  border-radius: 6px;
  background: #eff6ff;
  color: #2563eb;
}

.badge {
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge.actif {
  background: #dcfce7;
  color: #166534;
}

.badge.inactif {
  background: #f3f4f6;
  color: #4b5563;
}

.badge.prospect {
  background: #dbeafe;
  color: #1e40af;
}

.badge.archive {
  background: #fef3c7;
  color: #92400e;
}

.text-right {
  text-align: right !important;
}

.actions-cell {
  position: relative;
  text-align: right;
  vertical-align: middle;
}

.action-btn {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.dropdown-menu {
  position: absolute;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  border: 1px solid #f3f4f6;
  min-width: 195px;
  z-index: 9999;
  padding: 0.5rem;
  text-align: left;
  transform: translateY(-50%);
}

.dropdown-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.dropdown-menu li {
  padding: 0.65rem 0.75rem;
  font-size: 0.875rem;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.dropdown-menu li:hover {
  background-color: #f3f4f6;
  color: #2563eb;
}

.dropdown-menu li.danger {
  color: #325aaf;
}

.dropdown-menu li.danger2 {
  color: #ea580c;
}

.size-4 {
  width: 1rem;
  height: 1rem;
}

.size-5 {
  width: 1.25rem;
  height: 1.25rem;
}
</style>
