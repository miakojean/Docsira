<template>
  <div class="main-layout">
    <!-- Barre latérale -->
    <sidebar :defaultReduced="true" />

    <!-- Arborescence des dossiers et documents -->
    <affairTree :currentId="affairId" :documents="documents" @openDocument="openDocument" />

    <!-- Contenu principal -->
    <main class="main-content">
      <!-- En-tête de l'affaire -->
      <header class="affair-header">
            <div class="header-left">
                <button type="button" class="back-btn" title="Retour aux dossiers" @click="goBack">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
                    </svg>
                </button>

            <div class="header-info">

                <div class="header-title-row">
                    <h1 class="page-title">{{ dossier?.title || 'Dossier' }}</h1>
                    <span v-if="dossier" class="status-badge" :class="dossier.statut.toLowerCase()">
                        {{ statutLabels[dossier.statut] || dossier.statut }}
                    </span>
                </div>
                <p v-if="dossier" class="page-subtitle">
                  <span class="ref-text">{{ dossier.reference_affair }}</span>
                  <template v-if="dossier.client"> · {{ dossier.client.nom_complet }}</template>
                  <span class="meta-dot">·</span>
                  <span class="doc-count">{{ documents.length }} document(s)</span>
                </p>
          </div>
        </div>

        <div class="header-actions">
          <!-- Bouton Ajouter un document -->
        <button
            type="button"
            class="add-btn"
            :disabled="docStore.isUploading"
            title="Ajouter un document depuis votre ordinateur"
            @click="pickFromDisk"
        >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            <span>{{ docStore.isUploading ? 'Ajout en cours...' : 'Ajouter un document' }}</span>
        </button>
        </div>
      </header>

      <!-- Message d'erreur éventuel -->
      <div v-if="docStore.errorMessage" class="error-banner">
        <span>{{ docStore.errorMessage }}</span>
        <button type="button" class="error-close" @click="docStore.errorMessage = ''">×</button>
      </div>

      <!-- Zone de contenu des fichiers -->
        <div
            class="files-workspace"
            :class="{ 'is-drag-over': isDraggingOver }"
            @dragover.prevent="isDraggingOver = true"
            @dragleave.prevent="isDraggingOver = false"
            @drop.prevent="onDropFiles"
        >
        <!-- État de chargement initial -->
        <div v-if="docStore.isLoading" class="loading-state">
              <div class="spinner"></div>
              <p>Chargement des documents du dossier...</p>
        </div>

        <!-- ÉTAT VIDE : Aucun document trouvé -->
        <div v-else-if="documents.length === 0" class="empty-state-wrapper">
          <div class="empty-state" @click="pickFromDisk">
            <div class="empty-icon-circle">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.3" stroke="currentColor" class="size-12 empty-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
            </div>
            <h3 class="empty-title">Ce dossier est vide</h3>
            <p class="empty-text">Aucun document n'a encore été ajouté à ce dossier client.</p>

            <button
              type="button"
              class="empty-cta-btn"
              :disabled="docStore.isUploading"
              @click.stop="pickFromDisk"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
              </svg>
              <span>Ajouter un document depuis l'ordinateur</span>
            </button>
            <span class="empty-hint">Ou glissez-déposez directement vos fichiers ici</span>
          </div>
        </div>

        <!-- LISTE / GRILLE DES FICHIERS -->
        <div v-else class="files-content-area file-list--grid">
      
          <myfileCards 
            v-for="doc in documents"
            :key="doc.id"
            :document="doc"
            @open="openDocument"
            @preview="openDocument"
            @details="openDocDetails"
            @download="downloadDocument"
            @rename="openRename"
            @delete="openDelete"
          />

        </div>

        <!-- Footer identique à Mon Espace avec switcher de vue -->
        <footerSection :view="view" @update:view="view = $event" />
      </div>

      <!-- Input invisible pour sélectionner des fichiers sur le disque (fallback) -->
      <input
        ref="diskFileInputRef"
        type="file"
        multiple
        class="hidden-file-input"
        @change="onDiskFileInputChange"
      />

      <!-- MODALE DE VISUALISATION (PDF / Images) -->
      <Teleport to="body">
        <Transition name="modal-fade">
          <div v-if="preview" class="preview-backdrop" @click.self="closePreview">
            <div class="preview-modal">
              <div class="preview-header">
                <div class="preview-title-box truncate">
                  <h3 class="preview-title truncate">{{ preview.title }}</h3>
                </div>
                <div class="preview-actions">
                  <button type="button" class="preview-action-btn" title="Télécharger" @click="downloadDocument(preview.doc)">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                    </svg>
                    <span>Télécharger</span>
                  </button>
                  <button type="button" class="preview-close-btn" aria-label="Fermer" @click="closePreview">×</button>
                </div>
              </div>

              <div class="preview-body">
                <img v-if="preview.kind === 'image'" :src="preview.url" :alt="preview.title" class="preview-img" />
                <iframe v-else-if="preview.kind === 'pdf'" :src="preview.url" class="preview-frame"></iframe>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- MODALE DE RENOMMAGE -->
      <Teleport to="body">
        <Transition name="modal-fade">
          <div v-if="renamingDoc" class="modal-backdrop" @click.self="renamingDoc = null">
            <div class="modal-box">
              <div class="modal-box-header">
                <h3 class="modal-box-title">Renommer le document</h3>
                <button type="button" class="modal-box-close" @click="renamingDoc = null">x</button>
              </div>
              <div class="modal-box-body">
                <label class="input-label" for="renameDocInput">Titre du document</label>
                <input
                  id="renameDocInput"
                  type="text"
                  v-model="renameValue"
                  class="text-input"
                  placeholder="Nom du document"
                  @keyup.enter="confirmRename"
                  autofocus
                />
              </div>
              <div class="modal-box-footer">
                <button type="button" class="btn btn-secondary" @click="renamingDoc = null">Annuler</button>
                <button
                  type="button"
                  class="btn btn-primary"
                  :disabled="!renameValue.trim() || renameValue.trim() === renamingDoc.title"
                  @click="confirmRename"
                >
                  Enregistrer
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- MODALE DE DÉTAILS DU DOCUMENT -->
      <detailsModale
        :isOpen="isDetailsOpen"
        :item="docDetailsItem"
        @close="isDetailsOpen = false"
        @action="onDetailsAction"
      />

      <!-- MODALE DE SUPPRESSION -->
      <deleteModale
        :isOpen="isDeleteOpen"
        :isLoading="isDeleting"
        :isSuccess="false"
        :itemName="docToDelete?.title || 'ce document'"
        :isFolder="false"
        title="Supprimer le document"
        description="Êtes-vous sûr de vouloir supprimer définitivement ce document ?"
        subtext="Attention, cette action est irréversible."
        @close="isDeleteOpen = false"
        @delete="confirmDelete"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { open as openDialog, save as saveDialog } from '@tauri-apps/plugin-dialog';
import { readFile, writeFile } from '@tauri-apps/plugin-fs';
import sidebar from '../../components/navbar/sidebar.vue';
import affairTree from '../../components/navbar/affairTree.vue';
import footerSection from '../../components/layout/footerSection.vue';
import myfileCards from '../../components/cards/myfileCards.vue'
import fileCards from '../../components/cards/fileCards.vue';
import deleteModale from '../../components/modale/deleteModale.vue';
import detailsModale, { type ItemDetails } from '../../components/modale/detailsModale.vue';
import { useClientDossierStore, type Dossier } from '../../stores/dossierStore';
import { useDocumentStore, type DossierDocument } from '../../stores/documentStore';

const route = useRoute();
const router = useRouter();
const dossierStore = useClientDossierStore();
const docStore = useDocumentStore();

const affairId = computed(() => String(route.params.id));
const dossier = ref<Dossier | null>(null);

// Vue par défaut en 'list', avec possibilité de basculer en 'grid'
const view = ref<'list' | 'grid'>('list');
const isDraggingOver = ref(false);
const diskFileInputRef = ref<HTMLInputElement | null>(null);

const documents = computed(() => docStore.documents);

const statutLabels: Record<string, string> = {
  NOUVEAU: 'Nouveau',
  EN_COURS: 'En cours',
  EN_ATTENTE: 'En attente',
  BLOQUE: 'Bloqué',
  TERMINE: 'Terminé',
  CLOTURE: 'Clôturé',
  ANNULE: 'Annulé',
};

const mimeByExt: Record<string, string> = {
  pdf: 'application/pdf',
  png: 'image/png',
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  gif: 'image/gif',
  webp: 'image/webp',
  svg: 'image/svg+xml',
  txt: 'text/plain',
};

function extOf(name: string) {
  const i = name.lastIndexOf('.');
  return i === -1 ? '' : name.slice(i + 1).toLowerCase();
}

function goBack() {
  router.push('/dashboard/affairs');
}

async function refreshDossier() {
  if (!affairId.value) return;
  const fetched = await dossierStore.fetchDossier(affairId.value);
  if (fetched) {
    dossier.value = fetched;
  } else {
    dossier.value = dossierStore.allDossiers.find((d: Dossier) => d.id === affairId.value) ?? null;
  }
}

// ---------- Sélection et Import de fichiers depuis l'ordinateur ----------
async function pickFromDisk() {
  try {
    const selected = await openDialog({
      multiple: true,
      directory: false,
      title: 'Choisir des documents sur votre ordinateur',
    });
    if (!selected) return;
    const paths = Array.isArray(selected) ? selected : [selected];
    if (paths.length > 0) {
      await importPaths(paths);
    }
  } catch (error) {
    console.warn('openDialog non disponible, passage par le sélecteur HTML :', error);
    if (diskFileInputRef.value) {
      diskFileInputRef.value.value = '';
      diskFileInputRef.value.click();
    }
  }
}

async function importPaths(paths: string[]) {
  if (paths.length === 0) return;
  const files: File[] = [];
  for (const path of paths) {
    try {
      const bytes = await readFile(path);
      const name = path.split(/[\\/]/).pop() || 'document';
      files.push(new File([bytes], name, { type: mimeByExt[extOf(name)] || 'application/octet-stream' }));
    } catch (error) {
      console.error(`Lecture impossible du fichier : ${path}`, error);
    }
  }
  if (files.length === 0) {
    if (diskFileInputRef.value) {
      diskFileInputRef.value.value = '';
      diskFileInputRef.value.click();
    }
    return;
  }
  if (await docStore.uploadDocuments(affairId.value, files)) {
    await refreshDossier();
  }
}

async function onDiskFileInputChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const files = Array.from(target.files ?? []);
  target.value = '';
  if (files.length === 0) return;
  if (await docStore.uploadDocuments(affairId.value, files)) {
    await refreshDossier();
  }
}

async function onDropFiles(e: DragEvent) {
  isDraggingOver.value = false;
  const dt = e.dataTransfer;
  if (!dt) return;
  const files = Array.from(dt.files);
  if (files.length > 0) {
    if (await docStore.uploadDocuments(affairId.value, files)) {
      await refreshDossier();
    }
  }
}

// ---------- Visualisation et Téléchargement ----------
const preview = ref<{ url: string; title: string; kind: 'image' | 'pdf'; doc: DossierDocument } | null>(null);

async function typedBlob(doc: DossierDocument) {
  const blob = await docStore.fetchFileBlob(doc.id);
  if (!blob) return null;
  const type = mimeByExt[doc.extension];
  return type ? new Blob([blob], { type }) : blob;
}

async function openDocument(doc: DossierDocument) {
    const ext = (doc.extension || '').toLowerCase();
    const isImg = ['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg'].includes(ext);
    const isPdf = ext === 'pdf';

    if (!isImg && !isPdf) {
        return downloadDocument(doc);
    }

    const blob = await typedBlob(doc);
        if (!blob) {
            docStore.errorMessage = 'Impossible de charger le document pour la visualisation.';
        return;
    }

  closePreview();
  preview.value = {
    url: URL.createObjectURL(blob),
    title: doc.title,
    kind: isImg ? 'image' : 'pdf',
    doc,
  };
}

function closePreview() {
  if (preview.value) URL.revokeObjectURL(preview.value.url);
  preview.value = null;
}

async function downloadDocument(doc: DossierDocument) {
  try {
    const target = await saveDialog({ defaultPath: doc.file_name || doc.title });
    if (!target) return;
    const blob = await docStore.fetchFileBlob(doc.id);
    if (!blob) {
      docStore.errorMessage = 'Impossible de télécharger le document';
      return;
    }
    await writeFile(target, new Uint8Array(await blob.arrayBuffer()));
  } catch (error) {
    console.error('Erreur téléchargement :', error);
    docStore.errorMessage = "Impossible d'enregistrer le fichier sur le disque";
  }
}

// ---------- Renommage ----------
const renamingDoc = ref<DossierDocument | null>(null);
const renameValue = ref('');

function openRename(doc: DossierDocument) {
  renamingDoc.value = doc;
  renameValue.value = doc.title;
}

async function confirmRename() {
  if (!renamingDoc.value || !renameValue.value.trim()) return;
  if (await docStore.renameDocument(renamingDoc.value.id, renameValue.value.trim())) {
    renamingDoc.value = null;
  }
}

// ---------- Détails ----------
const isDetailsOpen = ref(false);
const docForDetails = ref<DossierDocument | null>(null);

function formatSize(bytes?: number) {
  if (!bytes || bytes <= 0) return '0 Ko';
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} Ko`;
  return `${(kb / 1024).toFixed(1)} Mo`;
}

function formatDate(iso?: string) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

const docDetailsItem = computed<ItemDetails>(() => {
  const doc = docForDetails.value;
  if (!doc) {
    return { isFolder: false, name: 'Document' };
  }
  return {
    isFolder: false,
    name: doc.title || doc.file_name || 'Document',
    path: `Dossier: ${dossier.value?.title || 'Dossier'} / ${doc.file_name || ''}`,
    size: formatSize(doc.size),
    owner: dossier.value?.client?.nom_complet || 'Cabinet',
    createdAt: formatDate(doc.uploaded_at),
    updatedAt: doc.version && doc.version > 1 ? `Version ${doc.version}` : 'Version originale (v1)',
    isShared: false,
  };
});

function openDocDetails(doc: DossierDocument) {
  docForDetails.value = doc;
  isDetailsOpen.value = true;
}

function onDetailsAction() {
  if (docForDetails.value) {
    isDetailsOpen.value = false;
    downloadDocument(docForDetails.value);
  }
}

// ---------- Suppression ----------
const isDeleteOpen = ref(false);
const docToDelete = ref<DossierDocument | null>(null);
const isDeleting = ref(false);

function openDelete(doc: DossierDocument) {
  docToDelete.value = doc;
  isDeleteOpen.value = true;
}

async function confirmDelete() {
  if (!docToDelete.value) return;
  isDeleting.value = true;
  try {
    const ok = await docStore.deleteDocument(docToDelete.value.id);
    if (ok) {
      isDeleteOpen.value = false;
      docToDelete.value = null;
      await refreshDossier();
    }
  } finally {
    isDeleting.value = false;
  }
}

onMounted(async () => {
  await Promise.all([refreshDossier(), docStore.fetchDocuments(affairId.value)]);
});

// Navigation d'un dossier à l'autre depuis l'arborescence
watch(affairId, async () => {
  closePreview();
  await Promise.all([refreshDossier(), docStore.fetchDocuments(affairId.value)]);
});

onUnmounted(() => {
  closePreview();
});
</script>

<style scoped>
/* === LAYOUT PRINCIPAL === */
.main-layout {
  display: flex;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: #f9fafb;
}

.main-content {
  flex: 1;
  width: 100%;
  min-width: 0;
  min-height: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f1f3f5;
}

/* === EN-TÊTE === */
.affair-header {
  padding: 1rem 1.5rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 0;
}

.back-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.back-btn:hover {
  background: #f3f4f6;
  color: #111827;
  border-color: #d1d5db;
}

.header-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.page-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.page-subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.ref-text {
  font-weight: 600;
  color: #4b5563;
}

.meta-dot {
  color: #cbd5e1;
}

.status-badge {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.55rem;
  border-radius: 9999px;
  background: #f3f4f6;
  color: #4b5563;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-badge.nouveau { background: #eff6ff; color: #2563eb; }
.status-badge.en_cours { background: #fef3c7; color: #d97706; }
.status-badge.termine { background: #ecfdf5; color: #059669; }
.status-badge.bloque { background: #fee2e2; color: #dc2626; }

/* === ACTIONS D'EN-TÊTE === */
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.view-toggle {
  display: flex;
  background: #f1f5f9;
  padding: 0.2rem;
  border-radius: 10px;
  gap: 0.2rem;
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn:hover {
  color: #1e293b;
}

.view-btn.active {
  background: #ffffff;
  color: var(--primary-color, #2563eb);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.view-icon {
  font-size: 0.95rem;
  line-height: 1;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  background: var(--primary-color, #2563eb);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2);
}

.add-btn:hover:not(:disabled) {
  background: var(--primary-color-dark, #1d4ed8);
}

.add-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* === BANNIÈRE D'ERREUR === */
.error-banner {
  margin: 0.75rem 1.5rem 0;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.error-close {
  background: none;
  border: none;
  color: #dc2626;
  font-size: 1.25rem;
  cursor: pointer;
  line-height: 1;
}

/* === ESPACE DES FICHIERS === */
.files-workspace {
  flex: 1;
  width: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: background-color 0.2s ease;
}

.files-workspace.is-drag-over {
  background: #e0e7ff;
}

.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: #64748b;
  font-size: 0.95rem;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--primary-color, #2563eb);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* === ÉTAT VIDE ÉLÉGANT === */
.empty-state-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.empty-state {
  width: 100%;
  max-width: 540px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3.5rem 2rem;
  background: #ffffff;
  border: 2px dashed #cbd5e1;
  border-radius: 20px;
  text-align: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.25s ease;
}

.empty-state:hover {
  border-color: var(--primary-color, #2563eb);
  background: #f8faff;
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.08);
}

.empty-icon-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #eff6ff;
  color: var(--primary-color, #2563eb);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
  transition: transform 0.25s ease;
}

.empty-state:hover .empty-icon-circle {
  transform: scale(1.08);
}

.empty-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.empty-text {
  margin: 0;
  font-size: 0.9rem;
  color: #64748b;
  max-width: 380px;
}

.empty-cta-btn {
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.4rem;
  background: var(--primary-color, #2563eb);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
  transition: all 0.2s ease;
}

.empty-cta-btn:hover:not(:disabled) {
  background: var(--primary-color-dark, #1d4ed8);
  transform: translateY(-1px);
}

.empty-hint {
  font-size: 0.78rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

/* === LISTE ET GRILLE DES FICHIERS === */
.files-content-area {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  scrollbar-width: thin;
  padding: 0.75rem;
}

.file-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.file-list--list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.file-list--grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.25rem;
}

.hidden-file-input {
  display: none !important;
}

/* === MODALE DE PREVIEW === */
.preview-backdrop {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.preview-modal {
  width: 100%;
  max-width: 900px;
  height: 85vh;
  background: #ffffff;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.preview-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.preview-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #111827;
}

.preview-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preview-action-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  background: #eff6ff;
  color: var(--primary-color, #2563eb);
  border: 1px solid #bfdbfe;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.preview-action-btn:hover {
  background: #dbeafe;
}

.preview-close-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f3f4f6;
  color: #6b7280;
  font-size: 1.4rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.preview-close-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.preview-body {
  flex: 1;
  min-height: 0;
  background: #0f172a;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: none;
  background: #ffffff;
}

/* === MODALE DE RENOMMAGE === */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal-box {
  width: 100%;
  max-width: 440px;
  background: #ffffff;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-box-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-box-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: #111827;
}

.modal-box-close {
  background: none;
  border: none;
  font-size: 1.4rem;
  color: #9ca3af;
  cursor: pointer;
  line-height: 1;
}

.modal-box-close:hover {
  color: #4b5563;
}

.input-label {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #6b7280;
}

.text-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.7rem 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  font-size: 0.92rem;
  outline: none;
  background: #f9fafb;
  color: #111827;
  transition: all 0.2s ease;
}

.text-input:focus {
  border-color: var(--primary-color, #2563eb);
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.modal-box-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn {
  padding: 0.6rem 1.1rem;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.btn-secondary {
  background: #f3f4f6;
  color: #4b5563;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: var(--primary-color, #2563eb);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-dark, #1d4ed8);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.size-4 {
  width: 1rem;
  height: 1rem;
}

.size-12 {
  width: 3rem;
  height: 3rem;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
