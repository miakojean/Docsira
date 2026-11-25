<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen && document" class="versions-modal-overlay" @click.self="closeModal">
        <div class="versions-modal-card" role="dialog" aria-modal="true" aria-label="Historique des versions">
          <header class="versions-modal-header">
            <div class="header-titles">
              <h3 class="versions-modal-title">Versions du document</h3>
              <p class="versions-modal-subtitle" :title="document.title || document.file_name">
                {{ document.title || document.file_name }}
              </p>
            </div>
            <button type="button" class="versions-modal-close" aria-label="Fermer" @click="closeModal">×</button>
          </header>

          <!-- Zone d'erreur éventuelle -->
          <div v-if="localError || errorMessage" class="error-line">
            <span>{{ localError || errorMessage }}</span>
            <button type="button" class="text-action" @click="localError = ''">Masquer</button>
          </div>

          <!-- Dépôt d'une nouvelle version -->
          <section v-if="canEdit" class="upload-version-box">
            <div class="section-row-head">
              <h4 class="section-label">Déposer la version v{{ nextVersionNumber }}</h4>
            </div>

            <div class="upload-controls">
              <label class="file-picker-btn" :class="{ 'is-disabled': isUploading }">
                <input
                  ref="fileInputRef"
                  type="file"
                  :accept="ALLOWED_DOCUMENT_ACCEPT"
                  class="hidden-input"
                  :disabled="isUploading"
                  @change="onFilePicked"
                />
                <span>{{ selectedFile ? selectedFile.name : 'Choisir un fichier (PDF, Word, Image)...' }}</span>
              </label>

              <input
                v-model="versionNote"
                type="text"
                maxlength="300"
                class="note-input"
                placeholder="Note de version (ex : Correction clause 3) — optionnel"
                :disabled="isUploading"
                @keyup.enter="submitNewVersion"
              />

              <div class="upload-footer">
                <span class="upload-hint">La version précédente reste conservée dans l'historique.</span>
                <button
                  type="button"
                  class="btn-primary"
                  :disabled="!selectedFile || isUploading"
                  @click="submitNewVersion"
                >
                  {{ isUploading ? 'Envoi...' : `Enregistrer v${nextVersionNumber}` }}
                </button>
              </div>
            </div>
          </section>

          <!-- Historique chronologique des versions (style Git sobre) -->
          <section class="versions-history-body">
            <h4 class="section-label">Historique ({{ versions.length }})</h4>

            <div v-if="isLoading" class="state-box">
              <LogoLoader size="md" label="Chargement des versions..." />
            </div>

            <div v-else-if="versions.length === 0" class="empty-note">
              Aucune version trouvée pour ce document.
            </div>

            <ol v-else class="versions-timeline">
              <li
                v-for="(ver, idx) in versions"
                :key="ver.id"
                class="version-item"
                :class="{ 'is-latest': idx === 0 }"
              >
                <div class="timeline-rail" aria-hidden="true">
                  <span class="timeline-dot"></span>
                  <span v-if="idx < versions.length - 1" class="timeline-line"></span>
                </div>

                <div class="version-content">
                  <div class="version-top-row">
                    <span class="version-code">v{{ ver.version || 1 }}</span>
                    <span v-if="idx === 0" class="current-mark">actuelle</span>
                    <span class="meta-sep">·</span>
                    <time class="version-date" :title="formatFullDate(ver.uploaded_at)">
                      {{ formatFullDate(ver.uploaded_at) }}
                    </time>
                  </div>

                  <div class="version-file-line">
                    <span class="version-filename" :title="ver.file_name || ver.title">
                      {{ ver.file_name || ver.title }}
                    </span>
                    <span class="meta-sep">·</span>
                    <span class="version-size">{{ formatSize(ver.size) }}</span>
                  </div>

                  <p v-if="ver.uploaded_by_name" class="version-author">
                    Par {{ ver.uploaded_by_name }}
                  </p>

                  <p v-if="ver.version_note" class="version-note">
                    « {{ ver.version_note }} »
                  </p>

                  <div class="version-actions">
                    <button type="button" class="text-action" @click="$emit('preview', ver)">
                      Visualiser
                    </button>
                    <button type="button" class="text-action" @click="$emit('download', ver)">
                      Télécharger
                    </button>

                    <template v-if="idx > 0 && canEdit">
                      <template v-if="confirmRestoreId === ver.id">
                        <span class="confirm-label">Restaurer v{{ ver.version }} en v{{ nextVersionNumber }} ?</span>
                        <button
                          type="button"
                          class="text-action is-primary"
                          :disabled="isUploading"
                          @click="confirmRestore(ver)"
                        >
                          Confirmer
                        </button>
                        <button type="button" class="text-action" @click="confirmRestoreId = null">
                          Annuler
                        </button>
                      </template>
                      <button
                        v-else
                        type="button"
                        class="text-action is-primary"
                        :disabled="isUploading"
                        @click="confirmRestoreId = ver.id"
                      >
                        Restaurer cette version
                      </button>
                    </template>
                  </div>
                </div>
              </li>
            </ol>
          </section>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { ALLOWED_DOCUMENT_ACCEPT, filterAllowedDocuments } from '../../helpers/documentFormats';
import { useDocumentStore, type DossierDocument } from '../../stores/documentStore';
import LogoLoader from '../tools/LogoLoader.vue';

const props = withDefaults(
  defineProps<{
    isOpen: boolean;
    document: DossierDocument | null;
    isUploading?: boolean;
    errorMessage?: string;
    focusUpload?: boolean;
    canEdit?: boolean;
  }>(),
  {
    isUploading: false,
    errorMessage: '',
    focusUpload: false,
    canEdit: true,
  }
);

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'preview', doc: DossierDocument): void;
  (e: 'download', doc: DossierDocument): void;
  (e: 'uploadVersion', payload: { document: DossierDocument; file: File; versionNote: string }): void;
  (e: 'restoreVersion', doc: DossierDocument): void;
}>();

const docStore = useDocumentStore();

const versions = ref<DossierDocument[]>([]);
const isLoading = ref(false);
const selectedFile = ref<File | null>(null);
const versionNote = ref('');
const localError = ref('');
const confirmRestoreId = ref<string | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);

const nextVersionNumber = computed(() => {
  const maxFromList = versions.value.reduce((acc, v) => Math.max(acc, v.version || 1), 1);
  const baseVer = props.document?.version || 1;
  return Math.max(maxFromList, baseVer) + 1;
});

async function loadVersions() {
  if (!props.document) {
    versions.value = [];
    return;
  }
  isLoading.value = true;
  try {
    const fetched = await docStore.fetchDocumentVersions(props.document.id);
    versions.value = fetched.length > 0 ? fetched : [props.document];
  } finally {
    isLoading.value = false;
  }
}

watch(
  () => [props.isOpen, props.document?.id] as const,
  async ([open]) => {
    if (open && props.document) {
      selectedFile.value = null;
      versionNote.value = '';
      localError.value = '';
      confirmRestoreId.value = null;
      if (fileInputRef.value) fileInputRef.value.value = '';
      await loadVersions();
    }
  },
  { immediate: true }
);

function onFilePicked(event: Event) {
  const input = event.target as HTMLInputElement;
  const files = Array.from(input.files ?? []);
  if (files.length === 0) return;

  const { valid, errorMessage } = filterAllowedDocuments([files[0]]);
  if (errorMessage) {
    localError.value = errorMessage;
    selectedFile.value = null;
    input.value = '';
    return;
  }
  localError.value = '';
  selectedFile.value = valid[0] ?? null;
}

function submitNewVersion() {
  if (!props.document || !selectedFile.value || props.isUploading) return;
  emit('uploadVersion', {
    document: props.document,
    file: selectedFile.value,
    versionNote: versionNote.value.trim(),
  });
}

function confirmRestore(ver: DossierDocument) {
  confirmRestoreId.value = null;
  emit('restoreVersion', ver);
}

function closeModal() {
  if (props.isUploading) return;
  emit('close');
}

function formatSize(bytes?: number) {
  if (!bytes || bytes <= 0) return '0 Ko';
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} Ko`;
  return `${(kb / 1024).toFixed(1)} Mo`;
}

function formatFullDate(iso?: string) {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' });
}

defineExpose({ reload: loadVersions });
</script>

<style scoped>
.versions-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10025;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.versions-modal-card {
  width: 100%;
  max-width: 580px;
  max-height: 86vh;
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 22px 50px rgba(15, 23, 42, 0.22);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.versions-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.header-titles {
  min-width: 0;
}

.versions-modal-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}

.versions-modal-subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.84rem;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.versions-modal-close {
  background: none;
  border: none;
  font-size: 1.45rem;
  line-height: 1;
  color: #64748b;
  cursor: pointer;
  padding: 0.1rem 0.35rem;
}

.versions-modal-close:hover {
  color: #0f172a;
}

.error-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.6rem 1.25rem;
  background: #fef2f2;
  border-bottom: 1px solid #fecaca;
  color: #b91c1c;
  font-size: 0.82rem;
}

.upload-version-box {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #fafafa;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  flex-shrink: 0;
}

.section-label {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: #475569;
}

.upload-controls {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.file-picker-btn {
  display: flex;
  align-items: center;
  padding: 0.55rem 0.8rem;
  border: 1px dashed #cbd5e1;
  border-radius: 9px;
  background: #ffffff;
  color: #334155;
  font-size: 0.84rem;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-picker-btn:hover:not(.is-disabled) {
  border-color: var(--primary-color, #005792);
  color: #0f172a;
}

.file-picker-btn.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.hidden-input {
  display: none;
}

.note-input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #d1d5db;
  border-radius: 9px;
  padding: 0.5rem 0.75rem;
  font-size: 0.84rem;
  color: #0f172a;
  background: #ffffff;
  outline: none;
}

.note-input:focus {
  border-color: var(--primary-color, #005792);
}

.upload-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.upload-hint {
  font-size: 0.76rem;
  color: #64748b;
}

.btn-primary {
  padding: 0.48rem 0.95rem;
  border-radius: 8px;
  border: none;
  background: var(--primary-color, #005792);
  color: #ffffff;
  font-size: 0.83rem;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-dark, #005380);
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.versions-history-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 1rem 1.25rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.state-box,
.empty-note {
  padding: 2rem 1rem;
  text-align: center;
  color: #64748b;
  font-size: 0.85rem;
}

.versions-timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.version-item {
  display: flex;
  gap: 0.75rem;
  position: relative;
}

.timeline-rail {
  width: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  padding-top: 0.35rem;
}

.timeline-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #cbd5e1;
  flex-shrink: 0;
}

.version-item.is-latest .timeline-dot {
  background: var(--primary-color, #005792);
}

.timeline-line {
  width: 1.5px;
  flex: 1;
  background: #e2e8f0;
  margin-top: 0.25rem;
}

.version-content {
  flex: 1;
  min-width: 0;
  padding-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.22rem;
}

.version-item:last-child .version-content {
  padding-bottom: 0;
}

.version-top-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  font-size: 0.82rem;
}

.version-code {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-weight: 700;
  color: #0f172a;
}

.version-item.is-latest .version-code {
  color: var(--primary-color, #005792);
}

.current-mark {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--primary-color, #005792);
}

.meta-sep {
  color: #cbd5e1;
}

.version-date,
.version-size,
.version-author {
  font-size: 0.78rem;
  color: #64748b;
  margin: 0;
}

.version-file-line {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
}

.version-filename {
  font-size: 0.86rem;
  font-weight: 600;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.version-note {
  margin: 0.1rem 0 0;
  font-size: 0.82rem;
  color: #334155;
}

.version-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.25rem;
}

.text-action {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.78rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
}

.text-action:hover:not(:disabled) {
  color: #0f172a;
  text-decoration: underline;
}

.text-action.is-primary {
  color: var(--primary-color, #005792);
}

.text-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-label {
  font-size: 0.76rem;
  color: #475569;
}
</style>

