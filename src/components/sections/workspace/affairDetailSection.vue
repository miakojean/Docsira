<template>
  <div class="affair-detail-section">
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
          </div>
          <p v-if="dossier" class="page-subtitle">
            <span class="ref-text">{{ dossier.reference_affair }}</span>
          </p>
        </div>
      </div>

      <div class="header-actions">
        <!-- Bouton Nouveau sous-dossier -->
        <button
          type="button"
          class="new-folder-btn"
          title="Créer un nouveau sous-dossier"
          @click="openCreateFolder"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v6m3-3H9m4.06-7.19-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
          </svg>
          <span>Nouveau dossier</span>
        </button>

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

    <!-- Barre de navigation des dossiers (Fil d'Ariane) -->
    <div class="folder-nav-bar">
      <div class="breadcrumbs">
        <button
          type="button"
          class="breadcrumb-item root"
          :class="{ active: currentFolderId === null }"
          title="Revenir à la racine du dossier"
          @click="currentFolderId = null"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
          </svg>
          <span>Racine</span>
        </button>

        <template v-for="(crumb, idx) in folderBreadcrumbs" :key="crumb.id">
          <span class="breadcrumb-separator">/</span>
          <button
            type="button"
            class="breadcrumb-item"
            :class="{ active: idx === folderBreadcrumbs.length - 1 }"
            @click="currentFolderId = crumb.id"
          >
            {{ crumb.name }}
          </button>
        </template>
      </div>

      <!-- Actions sur le sous-dossier actuel si ouvert -->
      <div v-if="currentFolder" class="current-folder-actions">
        <button
          type="button"
          class="folder-quick-btn"
          title="Renommer ce sous-dossier"
          @click="openRenameFolder(currentFolder)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
          </svg>
          <span>Renommer</span>
        </button>
        <button
          type="button"
          class="folder-quick-btn is-danger"
          title="Supprimer ce sous-dossier"
          @click="openDeleteFolder(currentFolder)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
          </svg>
          <span>Supprimer</span>
        </button>
      </div>
    </div>

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

      <!-- ÉTAT VIDE -->
      <div v-else-if="isEmptyCurrentView" class="empty-state-wrapper">
        <div class="empty-state" @click="pickFromDisk">
          <div class="empty-icon-circle">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.3" stroke="currentColor" class="size-12 empty-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
          </div>
          <h3 class="empty-title">
            {{ currentFolder ? `Le sous-dossier "${currentFolder.name}" est vide` : 'Ce dossier est vide' }}
          </h3>
          <p class="empty-text">
            {{ currentFolder ? 'Vous pouvez y ajouter des documents ou créer des sous-dossiers imbriqués.' : "Aucun document ni sous-dossier n'a encore été ajouté à ce dossier client." }}
          </p>

          <div class="empty-buttons-row" @click.stop>
            <button
              type="button"
              class="empty-cta-btn"
              :disabled="docStore.isUploading"
              @click="pickFromDisk"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
              </svg>
              <span>Ajouter un document</span>
            </button>

            <button
              type="button"
              class="empty-secondary-btn"
              @click="openCreateFolder"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v6m3-3H9m4.06-7.19-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
              </svg>
              <span>Nouveau sous-dossier</span>
            </button>
          </div>
          <span class="empty-hint">Ou glissez-déposez directement vos fichiers ici</span>
        </div>
      </div>

      <!-- LISTE / GRILLE DES FICHIERS ET SOUS-DOSSIERS -->
      <div v-else class="files-content-area file-list--grid">
        <folderCards
          v-for="sf in currentSubfolders"
          :key="sf.id"
          :folderName="sf.name"
          :itemCount="folderStore.getDocCount(sf.id, documents)"
          @open="currentFolderId = sf.id"
          @rename="openRenameFolder(sf)"
          @delete="openDeleteFolder(sf)"
          @dropDoc="onDocDropOnFolder($event, sf.id)"
        />

        <myfileCards 
          v-for="doc in currentDocuments"
          :key="doc.id"
          :document="doc"
          @open="openDocDetails"
          @preview="openDocument"
          @details="openDocDetails"
          @download="downloadDocument"
          @rename="openRename"
          @delete="openDelete"
          @move="openMoveDocModal(doc)"
        />
      </div>
    </div>

    <!-- Input invisible pour sélectionner des fichiers sur le disque (fallback) -->
    <input
      :ref="(el) => { diskFileInputRef = (el as HTMLInputElement | null); }"
      type="file"
      multiple
      class="hidden-file-input"
      @change="onDiskFileInputChange"
    />

    <!-- MODALES -->
    <filePreviewModale
      :preview="preview"
      @close="closePreview"
      @download="downloadDocument"
    />

    <renameDocModale
      :isOpen="!!renamingDoc"
      :initialName="renamingDoc?.title"
      @close="renamingDoc = null"
      @rename="confirmRename"
    />

    <renameModale
      :isOpen="isFolderModalOpen"
      :title="folderModalMode === 'create' ? 'Nouveau sous-dossier' : 'Renommer le sous-dossier'"
      :isFolder="true"
      :currentName="folderModalName"
      @close="isFolderModalOpen = false"
      @rename="confirmSaveFolder"
    />

    <deleteModale
      :isOpen="isDeleteFolderOpen"
      :isLoading="false"
      :isSuccess="false"
      :itemName="folderToDelete?.name || 'ce sous-dossier'"
      :isFolder="true"
      title="Supprimer le sous-dossier"
      description="Êtes-vous sûr de vouloir supprimer définitivement ce sous-dossier ?"
      subtext="Les documents présents dans ce dossier seront replacés à la racine de l'affaire."
      @close="isDeleteFolderOpen = false"
      @delete="confirmDeleteFolder"
    />

    <moveDocModale
      :isOpen="isMoveDocModalOpen"
      :document="docToMove"
      :subfolders="subfolders"
      :initialFolderId="targetFolderIdForMove"
      @close="isMoveDocModalOpen = false"
      @confirm="confirmMoveDoc"
    />

    <detail-modale
      :isOpen="isDetailsOpen"
      :file="docForDetails || {}"
      :folder-name="dossier?.title || ''"
      @close="isDetailsOpen = false"
      @share="openCollaboratorSettings"
      @download="downloadDetailsDocument"
      @edit="renameDetailsDocument"
      @delete="deleteDetailsDocument"
    />

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
  </div>
</template>

<script setup lang="ts">
import folderCards from '../../cards/folderCards.vue';
import myfileCards from '../../cards/myfileCards.vue';
import renameModale from '../../modale/renameModale.vue';
import deleteModale from '../../modale/deleteModale.vue';
import detailModale from '../../modale/detailModale.vue';
import filePreviewModale from '../../modale/filePreviewModale.vue';
import renameDocModale from '../../modale/renameDocModale.vue';
import moveDocModale from '../../modale/moveDocModale.vue';
import type { AffairDocumentsController } from '../../../composables/useAffairDocuments';

const props = defineProps<{
  affair: AffairDocumentsController;
}>();

const {
  dossier,
  docStore,
  folderStore,
  documents,
  currentFolderId,
  subfolders,
  currentSubfolders,
  currentDocuments,
  currentFolder,
  folderBreadcrumbs,
  isEmptyCurrentView,
  isDraggingOver,
  diskFileInputRef,
  isFolderModalOpen,
  folderModalMode,
  folderModalName,
  openCreateFolder,
  openRenameFolder,
  confirmSaveFolder,
  isDeleteFolderOpen,
  folderToDelete,
  openDeleteFolder,
  confirmDeleteFolder,
  isMoveDocModalOpen,
  docToMove,
  targetFolderIdForMove,
  openMoveDocModal,
  confirmMoveDoc,
  onDocDropOnFolder,
  goBack,
  pickFromDisk,
  onDiskFileInputChange,
  onDropFiles,
  preview,
  openDocument,
  closePreview,
  downloadDocument,
  renamingDoc,
  openRename,
  confirmRename,
  isDetailsOpen,
  docForDetails,
  openDocDetails,
  openCollaboratorSettings,
  downloadDetailsDocument,
  renameDetailsDocument,
  deleteDetailsDocument,
  isDeleteOpen,
  docToDelete,
  isDeleting,
  openDelete,
  confirmDelete,
} = props.affair;
</script>

<style scoped>
.affair-detail-section {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 0;
  min-width: 0;
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

/* === ACTIONS D'EN-TÊTE === */
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.new-folder-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  background: #ffffff;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.new-folder-btn:hover {
  background: #f9fafb;
  color: #111827;
  border-color: #9ca3af;
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

/* === BARRE DU FIL D'ARIANE / NAVIGATION SOUS-DOSSIERS === */
.folder-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 1.5rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  gap: 1rem;
  flex-shrink: 0;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.breadcrumb-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 0.85rem;
  font-weight: 500;
  padding: 0.3rem 0.6rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.breadcrumb-item:hover {
  background: #f3f4f6;
  color: #111827;
}

.breadcrumb-item.active {
  color: #2563eb;
  font-weight: 600;
  background: #eff6ff;
}

.breadcrumb-separator {
  color: #cbd5e1;
  font-size: 0.85rem;
  font-weight: 600;
}

.current-folder-actions {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.folder-quick-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.65rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  color: #4b5563;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.folder-quick-btn:hover {
  background: #f3f4f6;
  color: #111827;
  border-color: #d1d5db;
}

.folder-quick-btn.is-danger {
  color: #dc2626;
  border-color: #fecaca;
}

.folder-quick-btn.is-danger:hover {
  background: #fef2f2;
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

.empty-buttons-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}

.empty-cta-btn {
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

.empty-secondary-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.4rem;
  background: #ffffff;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.empty-secondary-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
  color: #111827;
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

.file-list--grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.25rem;
}

.hidden-file-input {
  display: none !important;
}

.size-4 {
  width: 1rem;
  height: 1rem;
}

.size-12 {
  width: 3rem;
  height: 3rem;
}
</style>