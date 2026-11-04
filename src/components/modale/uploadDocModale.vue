<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="300">
      <div v-if="isOpen" class="modal-overlay" @click.self="handleClose">
        <div class="modal-card" role="dialog" aria-modal="true">
          <!-- En-tête -->
          <div class="modal-header">
            <div class="header-titles">
              <h3 class="modal-title">Ajouter un document</h3>
              <p class="modal-subtitle">
                <span class="ref-code">{{ dossier?.reference_affair || 'Dossier' }}</span>
                <span v-if="dossier?.title" class="title-sep">•</span>
                <span class="dossier-name">{{ dossier?.title }}</span>
                <template v-if="targetFolderName">
                  <span class="title-sep">•</span>
                  <span class="folder-target-badge">Sous-dossier : {{ targetFolderName }}</span>
                </template>
              </p>
            </div>
            <button class="close-btn" @click="handleClose" aria-label="Fermer la modale">
              &times;
            </button>
          </div>

          <!-- Corps de la modale -->
          <div class="modal-body">
            <!-- 1. ZONE DE SÉLECTION / DÉPÔT DE FICHIERS -->
            <div class="section-block">
              <label class="section-label">
                <span>Fichier(s) à importer</span>
                <span v-if="selectedFiles.length" class="files-count-badge">
                  {{ selectedFiles.length }} fichier{{ selectedFiles.length > 1 ? 's' : '' }}
                </span>
              </label>

              <!-- Zone de drop si aucun fichier -->
              <div
                v-if="selectedFiles.length === 0"
                class="dropzone-area"
                :class="{ 'is-drag-over': isDragOver }"
                @dragover.prevent="isDragOver = true"
                @dragleave.prevent="isDragOver = false"
                @drop.prevent="onDropFiles"
                @click="browseFiles"
              >
                <div class="dropzone-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
                  </svg>
                </div>
                <p class="dropzone-title">Glissez-déposez vos fichiers ici</p>
                <p class="dropzone-subtitle">ou cliquez pour parcourir votre ordinateur</p>
                <span class="dropzone-formats">PDF, Word, Excel, Images, Textes</span>
              </div>

              <!-- Liste des fichiers sélectionnés -->
              <div v-else class="selected-files-container">
                <div class="files-list">
                  <div
                    v-for="(file, index) in selectedFiles"
                    :key="`${file.name}-${index}`"
                    class="file-row"
                  >
                    <div class="file-ext-badge" :class="extClass(file.name)">
                      {{ getExt(file.name) }}
                    </div>
                    <div class="file-info">
                      <span class="file-name" :title="file.name">{{ file.name }}</span>
                      <span class="file-size">{{ formatBytes(file.size) }}</span>
                    </div>
                    <button
                      type="button"
                      class="remove-file-btn"
                      title="Retirer ce fichier"
                      @click="removeFile(index)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>

                <div class="add-more-row">
                  <button type="button" class="add-more-btn" @click="browseFiles">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                    </svg>
                    <span>Ajouter d'autres fichiers</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- 2. SÉLECTION DIRECTE DE LA CATÉGORIE -->
            <div class="section-block">
              <label class="section-label" for="upload-doc-category">
                <span>Catégorie du document</span>
              </label>

              <div class="select-wrapper">
                <select
                  id="upload-doc-category"
                  v-model="selectedCategory"
                  class="select-input"
                >
                  <option
                    v-for="cat in SIRA_OPTIONS"
                    :key="cat.value"
                    :value="cat.value"
                  >
                    {{ cat.label }}
                  </option>
                </select>
                <div class="select-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                  </svg>
                </div>
              </div>
            </div>

            <!-- Erreur éventuelle -->
            <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
          </div>

          <!-- Pied de page -->
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" :disabled="isUploading" @click="handleClose">
              Annuler
            </button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="selectedFiles.length === 0 || isUploading"
              @click="submitUpload"
            >
              <LogoLoader v-if="isUploading" size="xs" :inline="true" />
              <span>
                {{ isUploading ? 'Importation en cours...' : `Importer ${selectedFiles.length > 0 ? `(${selectedFiles.length})` : ''}` }}
              </span>
            </button>
          </div>

          <!-- Input masqué pour le sélecteur HTML fallback -->
          <input
            ref="fileInputRef"
            type="file"
            multiple
            class="hidden-input"
            @change="onFileInputChange"
          />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { open as openDialog } from '@tauri-apps/plugin-dialog';
import { readFile } from '@tauri-apps/plugin-fs';
import type { Dossier } from '../../stores/dossierStore';
import type { SiraCategory } from '../../stores/documentStore';
import LogoLoader from '../tools/LogoLoader.vue';

const props = withDefaults(
  defineProps<{
    isOpen: boolean;
    dossier: Dossier | null;
    targetFolderName?: string | null;
    initialFiles?: File[];
    isUploading?: boolean;
    errorMessage?: string;
  }>(),
  {
    targetFolderName: null,
    initialFiles: () => [],
    isUploading: false,
    errorMessage: '',
  }
);

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'upload', payload: { files: File[]; category: SiraCategory }): void;
}>();

const selectedFiles = ref<File[]>([]);
const selectedCategory = ref<SiraCategory>('IDENTIFICATION');
const isDragOver = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

const SIRA_OPTIONS = [
  { value: 'IDENTIFICATION' as SiraCategory, label: 'Identification' },
  { value: 'CONSTITUTION' as SiraCategory, label: 'Constitution' },
  { value: 'PROCEDURES' as SiraCategory, label: 'Procédures' },
  { value: 'LIVRABLES' as SiraCategory, label: 'Livrables' },
  { value: 'CLOTURE' as SiraCategory, label: 'Clôture' },
];

const mimeByExt: Record<string, string> = {
  pdf: 'application/pdf',
  png: 'image/png',
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  gif: 'image/gif',
  webp: 'image/webp',
  svg: 'image/svg+xml',
  txt: 'text/plain',
  doc: 'application/msword',
  docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  xls: 'application/vnd.ms-excel',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
};

watch(
  () => props.isOpen,
  (val) => {
    if (val) {
      if (props.initialFiles && props.initialFiles.length > 0) {
        selectedFiles.value = [...props.initialFiles];
      } else {
        selectedFiles.value = [];
      }
      selectedCategory.value = 'IDENTIFICATION';
      isDragOver.value = false;
    }
  },
  { immediate: true }
);

watch(
  () => props.initialFiles,
  (files) => {
    if (files && files.length > 0) {
      selectedFiles.value = [...files];
    }
  }
);

function handleClose() {
  selectedFiles.value = [];
  emit('close');
}

function removeFile(index: number) {
  selectedFiles.value.splice(index, 1);
}

function getExt(name: string): string {
  const i = name.lastIndexOf('.');
  return i === -1 ? 'DOC' : name.slice(i + 1).toUpperCase();
}

function extClass(name: string): string {
  const ext = getExt(name).toLowerCase();
  if (ext === 'pdf') return 'is-pdf';
  if (['doc', 'docx', 'odt'].includes(ext)) return 'is-word';
  if (['xls', 'xlsx', 'csv'].includes(ext)) return 'is-excel';
  if (['png', 'jpg', 'jpeg', 'webp', 'svg'].includes(ext)) return 'is-image';
  return 'is-default';
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'Ko', 'Mo', 'Go'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

async function browseFiles() {
  try {
    const selected = await openDialog({
      multiple: true,
      directory: false,
      title: 'Sélectionner des documents',
    });
    if (!selected) return;
    const paths = Array.isArray(selected) ? selected : [selected];
    for (const path of paths) {
      try {
        const bytes = await readFile(path);
        const name = path.split(/[\\/]/).pop() || 'document';
        const ext = name.split('.').pop()?.toLowerCase() || '';
        selectedFiles.value.push(
          new File([bytes], name, { type: mimeByExt[ext] || 'application/octet-stream' })
        );
      } catch (err) {
        console.error('Erreur de lecture du fichier', err);
      }
    }
  } catch (err) {
    console.warn('Fallback HTML file input', err);
    if (fileInputRef.value) {
      fileInputRef.value.value = '';
      fileInputRef.value.click();
    }
  }
}

function onFileInputChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const files = Array.from(target.files ?? []);
  target.value = '';
  if (files.length > 0) {
    selectedFiles.value.push(...files);
  }
}

function onDropFiles(e: DragEvent) {
  isDragOver.value = false;
  if (!e.dataTransfer?.files) return;
  const files = Array.from(e.dataTransfer.files);
  if (files.length > 0) {
    selectedFiles.value.push(...files);
  }
}

function submitUpload() {
  if (selectedFiles.value.length === 0 || props.isUploading) return;
  emit('upload', {
    files: [...selectedFiles.value],
    category: selectedCategory.value,
  });
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  background: #ffffff;
  border-radius: 20px;
  width: 100%;
  max-width: 640px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(226, 232, 240, 0.8);
  overflow: hidden;
}

/* En-tête */
.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.modal-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #0f172a;
}

.modal-subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.82rem;
  color: #64748b;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.ref-code {
  font-weight: 700;
  color: #2563eb;
  background: #eff6ff;
  padding: 0.05rem 0.4rem;
  border-radius: 4px;
}

.title-sep {
  color: #cbd5e1;
}

.dossier-name {
  font-weight: 500;
  color: #334155;
}

.folder-target-badge {
  color: #059669;
  background: #ecfdf5;
  padding: 0.05rem 0.4rem;
  border-radius: 4px;
  font-weight: 600;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.6rem;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.2rem;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-btn:hover {
  color: #0f172a;
  background: #f1f5f9;
}

/* Corps */
.modal-body {
  padding: 1.25rem 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.section-block {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.section-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.88rem;
  font-weight: 700;
  color: #1e293b;
}

.section-hint {
  font-size: 0.76rem;
  font-weight: 400;
  color: #64748b;
}

.files-count-badge {
  font-size: 0.74rem;
  font-weight: 600;
  background: #eff6ff;
  color: #2563eb;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  border: 1px solid #dbeafe;
}

/* Zone de drop */
.dropzone-area {
  border: 2px dashed #cbd5e1;
  border-radius: 14px;
  padding: 1.75rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dropzone-area:hover,
.dropzone-area.is-drag-over {
  border-color: #3b82f6;
  background: #eff6ff;
}

.dropzone-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #ffffff;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  margin-bottom: 0.6rem;
}

.dropzone-title {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
  color: #1e293b;
}

.dropzone-subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.8rem;
  color: #64748b;
}

.dropzone-formats {
  margin-top: 0.6rem;
  font-size: 0.72rem;
  color: #94a3b8;
  background: #ffffff;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

/* Liste des fichiers sélectionnés */
.selected-files-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.files-list {
  max-height: 160px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding-right: 0.2rem;
}

.file-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.file-ext-badge {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 0.2rem 0.45rem;
  border-radius: 6px;
  letter-spacing: 0.03em;
  line-height: 1;
}

.file-ext-badge.is-pdf {
  background: #fee2e2;
  color: #dc2626;
}

.file-ext-badge.is-word {
  background: #dbeafe;
  color: #2563eb;
}

.file-ext-badge.is-excel {
  background: #dcfce7;
  color: #16a34a;
}

.file-ext-badge.is-image {
  background: #fef3c7;
  color: #d97706;
}

.file-ext-badge.is-default {
  background: #f1f5f9;
  color: #64748b;
}

.file-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 0.72rem;
  color: #64748b;
}

.remove-file-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.3rem;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.remove-file-btn:hover {
  color: #ef4444;
  background: #fee2e2;
}

.add-more-row {
  display: flex;
  justify-content: flex-end;
}

.add-more-btn {
  background: transparent;
  border: 1px dashed #cbd5e1;
  color: #2563eb;
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  transition: all 0.15s ease;
}

.add-more-btn:hover {
  background: #eff6ff;
  border-color: #bfdbfe;
}

/* Sélecteur de catégorie */
.select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.select-input {
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: #1e293b;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
}

.select-input:hover {
  border-color: #cbd5e1;
  background: #ffffff;
}

.select-input:focus {
  border-color: #2563eb;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.select-icon {
  position: absolute;
  right: 1rem;
  pointer-events: none;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-text {
  margin: 0;
  font-size: 0.8rem;
  color: #dc2626;
}

/* Pied de page */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #f1f5f9;
  background: #fafafa;
}

.btn {
  padding: 0.55rem 1.15rem;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  transition: all 0.15s ease;
}

.btn-secondary {
  background: #ffffff;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-primary {
  background: #2563eb;
  border: 1px solid #2563eb;
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.hidden-input {
  display: none;
}
</style>
