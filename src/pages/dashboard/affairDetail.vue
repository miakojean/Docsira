<template>
  <div class="main-layout">
    <!-- Barre latérale -->
    <sidebar :defaultReduced="true" />

    <!-- Arborescence des dossiers et documents -->
    <affairTree
      :currentId="affairId"
      :documents="documents"
      :subfolders="subfolders"
      :currentFolderId="currentFolderId"
      @openDocument="openDocument"
      @selectFolder="currentFolderId = $event"
    />

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
                  <template v-if="subfolders.length > 0">
                    <span class="meta-dot">·</span>
                    <span class="doc-count">{{ subfolders.length }} sous-dossier(s)</span>
                  </template>
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

        <!-- ÉTAT VIDE : Aucun document ni sous-dossier -->
        <div v-else-if="isEmptyCurrentView" class="empty-state-wrapper">
          <div class="empty-state" @click="pickFromDisk">
            <div class="empty-icon-circle">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.3" stroke="currentColor" class="size-12 empty-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
            </div>
            <h3 class="empty-title">{{ currentFolder ? `Le sous-dossier "${currentFolder.name}" est vide` : 'Ce dossier est vide' }}</h3>
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
          <!-- Cartes des sous-dossiers -->
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

          <!-- Cartes des documents -->
          <myfileCards 
            v-for="doc in currentDocuments"
            :key="doc.id"
            :document="doc"
            @open="openDocument"
            @preview="openDocument"
            @details="openDocDetails"
            @detail="openDocDetails"
            @download="downloadDocument"
            @rename="openRename"
            @delete="openDelete"
            @move="openMoveDocModal(doc)"
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

      <!-- MODALE DE CRÉATION / RENOMMAGE DE SOUS-DOSSIER -->
      <renameModale
        :isOpen="isFolderModalOpen"
        :title="folderModalMode === 'create' ? 'Nouveau sous-dossier' : 'Renommer le sous-dossier'"
        :isFolder="true"
        :currentName="folderModalName"
        @close="isFolderModalOpen = false"
        @rename="confirmSaveFolder"
      />

      <!-- MODALE DE SUPPRESSION DE SOUS-DOSSIER -->
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

      <!-- MODALE POUR DÉPLACER UN DOCUMENT VERS UN SOUS-DOSSIER -->
      <Teleport to="body">
        <Transition name="modal-fade">
          <div v-if="isMoveDocModalOpen && docToMove" class="modal-backdrop" @click.self="isMoveDocModalOpen = false">
            <div class="modal-box">
              <div class="modal-box-header">
                <h3 class="modal-box-title">Déplacer le document</h3>
                <button type="button" class="modal-box-close" @click="isMoveDocModalOpen = false">&times;</button>
              </div>
              <div class="modal-box-body">
                <p class="destination-hint">
                  Sélectionnez l'emplacement de destination pour <strong>{{ docToMove.title || docToMove.file_name }}</strong> :
                </p>

                <div class="folder-destination-list">
                  <label
                    class="destination-option"
                    :class="{ selected: targetFolderIdForMove === null }"
                  >
                    <input
                      type="radio"
                      name="destFolder"
                      :value="null"
                      v-model="targetFolderIdForMove"
                    />
                    <div class="dest-icon">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
                      </svg>
                    </div>
                    <div class="dest-label">
                      <strong>Racine de l'affaire</strong>
                      <span>Emplacement principal de l'affaire</span>
                    </div>
                  </label>

                  <label
                    v-for="sf in subfolders"
                    :key="sf.id"
                    class="destination-option"
                    :class="{ selected: targetFolderIdForMove === sf.id }"
                  >
                    <input
                      type="radio"
                      name="destFolder"
                      :value="sf.id"
                      v-model="targetFolderIdForMove"
                    />
                    <div class="dest-icon folder">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
                      </svg>
                    </div>
                    <div class="dest-label">
                      <strong>{{ sf.name }}</strong>
                      <span>Sous-dossier</span>
                    </div>
                  </label>
                </div>
              </div>
              <div class="modal-box-footer">
                <button type="button" class="btn btn-secondary" @click="isMoveDocModalOpen = false">Annuler</button>
                <button type="button" class="btn btn-primary" @click="confirmMoveDoc">Déplacer ici</button>
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
import folderCards from '../../components/cards/folderCards.vue';
import myfileCards from '../../components/cards/myfileCards.vue';
import renameModale from '../../components/modale/renameModale.vue';
import deleteModale from '../../components/modale/deleteModale.vue';
import detailsModale, { type ItemDetails } from '../../components/modale/detailsModale.vue';
import { useClientDossierStore, type Dossier } from '../../stores/dossierStore';
import { useDocumentStore, type DossierDocument } from '../../stores/documentStore';
import { useAffairFolderStore, type AffairSubfolder } from '../../stores/affairFolderStore';

const route = useRoute();
const router = useRouter();
const dossierStore = useClientDossierStore();
const docStore = useDocumentStore();
const folderStore = useAffairFolderStore();

const affairId = computed(() => String(route.params.id));
const dossier = ref<Dossier | null>(null);

// Vue par défaut en 'list', avec possibilité de basculer en 'grid'
const view = ref<'list' | 'grid'>('list');
const isDraggingOver = ref(false);
const diskFileInputRef = ref<HTMLInputElement | null>(null);

const documents = computed(() => docStore.documents);

// ---------- Sous-dossiers de l'affaire ----------
const currentFolderId = ref<string | null>(null);

// Tous les sous-dossiers de cette affaire
const subfolders = computed<AffairSubfolder[]>(() => {
  return folderStore.folders.filter((f) => String(f.affairId) === affairId.value);
});

// Sous-dossiers enfants du niveau actuel
const currentSubfolders = computed<AffairSubfolder[]>(() => {
  return folderStore.getSubfolders(affairId.value, currentFolderId.value);
});

// Documents du niveau actuel
const currentDocuments = computed<DossierDocument[]>(() => {
  return folderStore.getFolderDocuments(affairId.value, currentFolderId.value, documents.value);
});

// Dossier actif
const currentFolder = computed<AffairSubfolder | null>(() => {
  return folderStore.getFolder(currentFolderId.value);
});

// Fil d'Ariane
const folderBreadcrumbs = computed<AffairSubfolder[]>(() => {
  return folderStore.getFolderPath(currentFolderId.value);
});

// État vide : ni sous-dossiers ni documents à ce niveau
const isEmptyCurrentView = computed(() => {
  return currentSubfolders.value.length === 0 && currentDocuments.value.length === 0;
});

// Gestion modale création / renommage de sous-dossier
const isFolderModalOpen = ref(false);
const folderModalMode = ref<'create' | 'rename'>('create');
const folderToRename = ref<AffairSubfolder | null>(null);
const folderModalName = ref('');

function openCreateFolder() {
  folderModalMode.value = 'create';
  folderToRename.value = null;
  folderModalName.value = '';
  isFolderModalOpen.value = true;
}

function openRenameFolder(folder: AffairSubfolder) {
  folderModalMode.value = 'rename';
  folderToRename.value = folder;
  folderModalName.value = folder.name;
  isFolderModalOpen.value = true;
}

function confirmSaveFolder(name: string) {
  if (folderModalMode.value === 'create') {
    folderStore.createFolder(affairId.value, name, currentFolderId.value);
  } else if (folderToRename.value) {
    folderStore.renameFolder(folderToRename.value.id, name);
  }
  isFolderModalOpen.value = false;
}

// Gestion modale suppression de sous-dossier
const isDeleteFolderOpen = ref(false);
const folderToDelete = ref<AffairSubfolder | null>(null);

function openDeleteFolder(folder: AffairSubfolder) {
  folderToDelete.value = folder;
  isDeleteFolderOpen.value = true;
}

function confirmDeleteFolder() {
  if (!folderToDelete.value) return;
  const deletedId = folderToDelete.value.id;
  const parentId = folderToDelete.value.parentId;
  folderStore.deleteFolder(deletedId);
  if (currentFolderId.value === deletedId) {
    currentFolderId.value = parentId;
  }
  isDeleteFolderOpen.value = false;
  folderToDelete.value = null;
}

// Déplacement d'un document dans un sous-dossier
const isMoveDocModalOpen = ref(false);
const docToMove = ref<DossierDocument | null>(null);
const targetFolderIdForMove = ref<string | null>(null);

function openMoveDocModal(doc: DossierDocument) {
  docToMove.value = doc;
  targetFolderIdForMove.value = folderStore.docFolderMap[doc.id] ?? null;
  isMoveDocModalOpen.value = true;
}

function confirmMoveDoc() {
  if (docToMove.value) {
    folderStore.assignDocToFolder(docToMove.value.id, targetFolderIdForMove.value);
    isMoveDocModalOpen.value = false;
    docToMove.value = null;
  }
}

function onDocDropOnFolder(docId: string, folderId: string) {
  folderStore.assignDocToFolder(docId, folderId);
}

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
  const prevDocIds = new Set(docStore.documents.map((d) => d.id));
  if (await docStore.uploadDocuments(affairId.value, files)) {
    // Si on est dans un sous-dossier, lier immédiatement les nouveaux documents à ce sous-dossier
    if (currentFolderId.value) {
      for (const d of docStore.documents) {
        if (!prevDocIds.has(d.id)) {
          folderStore.assignDocToFolder(d.id, currentFolderId.value);
        }
      }
    }
    await refreshDossier();
  }
}

async function onDiskFileInputChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const files = Array.from(target.files ?? []);
  target.value = '';
  if (files.length === 0) return;
  const prevDocIds = new Set(docStore.documents.map((d) => d.id));
  if (await docStore.uploadDocuments(affairId.value, files)) {
    if (currentFolderId.value) {
      for (const d of docStore.documents) {
        if (!prevDocIds.has(d.id)) {
          folderStore.assignDocToFolder(d.id, currentFolderId.value);
        }
      }
    }
    await refreshDossier();
  }
}

async function onDropFiles(e: DragEvent) {
  isDraggingOver.value = false;
  const dt = e.dataTransfer;
  if (!dt) return;
  const files = Array.from(dt.files);
  if (files.length > 0) {
    const prevDocIds = new Set(docStore.documents.map((d) => d.id));
    if (await docStore.uploadDocuments(affairId.value, files)) {
      if (currentFolderId.value) {
        for (const d of docStore.documents) {
          if (!prevDocIds.has(d.id)) {
            folderStore.assignDocToFolder(d.id, currentFolderId.value);
          }
        }
      }
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
  const folderId = folderStore.docFolderMap[doc.id];
  const sf = folderId ? folderStore.getFolder(folderId) : null;
  const pathStr = sf
    ? `Dossier: ${dossier.value?.title || 'Dossier'} / ${sf.name} / ${doc.file_name || ''}`
    : `Dossier: ${dossier.value?.title || 'Dossier'} / ${doc.file_name || ''}`;

  return {
    isFolder: false,
    name: doc.title || doc.file_name || 'Document',
    path: pathStr,
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
      folderStore.assignDocToFolder(docToDelete.value.id, null);
      isDeleteOpen.value = false;
      docToDelete.value = null;
      await refreshDossier();
    }
  } finally {
    isDeleting.value = false;
  }
}

onMounted(async () => {
  await Promise.all([
    refreshDossier(),
    docStore.fetchDocuments(affairId.value),
    folderStore.loadStore(),
  ]);
});

// Navigation d'un dossier à l'autre depuis l'arborescence
watch(affairId, async () => {
  closePreview();
  currentFolderId.value = null;
  await Promise.all([
    refreshDossier(),
    docStore.fetchDocuments(affairId.value),
    folderStore.loadStore(),
  ]);
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

/* === MODALE DESTINATION DÉPLACEMENT FICHIER === */
.destination-hint {
  font-size: 0.88rem;
  color: #4b5563;
  margin-bottom: 0.75rem;
}

.folder-destination-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 260px;
  overflow-y: auto;
  padding: 0.25rem 0;
}

.destination-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.15s ease;
}

.destination-option:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.destination-option.selected {
  background: #eff6ff;
  border-color: #2563eb;
}

.destination-option input[type="radio"] {
  accent-color: #2563eb;
  cursor: pointer;
}

.dest-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  flex-shrink: 0;
}

.dest-icon.folder {
  background: #fef3c7;
  color: #d97706;
}

.dest-label {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.dest-label strong {
  font-size: 0.88rem;
  color: #1f2937;
}

.dest-label span {
  font-size: 0.76rem;
  color: #6b7280;
}
</style>
