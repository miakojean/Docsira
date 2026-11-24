<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen" class="send-ws-overlay" @click.self="handleClose">
        <div class="send-ws-card" role="dialog" aria-modal="true" aria-label="Envoyer vers le Workspace">
          <header class="send-ws-header">
            <h3 class="send-ws-title">Envoyer vers le Workspace</h3>
            <button type="button" class="send-ws-close" aria-label="Fermer" @click="handleClose">×</button>
          </header>

          <!-- État succès -->
          <div v-if="transferResult" class="send-ws-body send-ws-success">
            <p class="success-title">
              {{ transferResult.uploadedCount }} {{ transferResult.uploadedCount > 1 ? 'fichiers envoyés' : 'fichier envoyé' }} vers le Workspace
            </p>
            <p v-if="transferResult.skippedCount > 0" class="success-sub">
              {{ transferResult.skippedCount }} {{ transferResult.skippedCount > 1 ? 'éléments ignorés' : 'élément ignoré' }} (format non supporté par le Workspace).
            </p>
            <div class="send-ws-footer">
              <button type="button" class="btn-secondary" @click="handleClose">Fermer</button>
              <button type="button" class="btn-primary" @click="openTargetDossier">Ouvrir le dossier</button>
            </div>
          </div>

          <!-- Formulaire -->
          <div v-else class="send-ws-body">
            <div class="source-summary">
              <span class="source-label">{{ isDirectory ? 'Dossier source' : 'Fichier source' }}</span>
              <span class="source-name" :title="sourcePath">{{ sourceName }}</span>
              <span v-if="isDirectory" class="source-hint">
                Seuls les fichiers compatibles (PDF, Word .doc/.docx et images) à la racine de ce dossier seront copiés.
              </span>
            </div>

            <div class="form-field">
              <label for="ws-dossier-search" class="field-label">Dossier de destination dans le Workspace</label>
              <input
                id="ws-dossier-search"
                v-model="dossierSearch"
                type="text"
                class="text-input"
                placeholder="Rechercher un dossier ou client..."
                :disabled="localStore.isMutating || dossierStore.isLoading"
              />
              <select
                v-model="selectedAffairId"
                class="select-field"
                :disabled="localStore.isMutating || dossierStore.isLoading"
              >
                <option value="" disabled>
                  {{ dossierStore.isLoading ? 'Chargement des dossiers...' : 'Sélectionner un dossier cible' }}
                </option>
                <option v-for="d in filteredDossiers" :key="d.id" :value="d.id">
                  {{ d.reference_affair ? `${d.reference_affair} — ` : '' }}{{ d.title }}{{ d.client?.nom_complet ? ` (${d.client.nom_complet})` : '' }}
                </option>
              </select>
            </div>

            <div class="form-field">
              <label for="ws-sira-category" class="field-label">Catégorie SIRA</label>
              <select
                id="ws-sira-category"
                v-model="selectedCategory"
                class="select-field"
                :disabled="localStore.isMutating"
              >
                <option v-for="step in SIRA_STEPS" :key="step.category" :value="step.category">
                  {{ step.label }} — {{ step.description }}
                </option>
              </select>
            </div>

            <p v-if="localStore.errorMessage" class="error-text">{{ localStore.errorMessage }}</p>

            <footer class="send-ws-footer">
              <button
                type="button"
                class="btn-secondary"
                :disabled="localStore.isMutating"
                @click="handleClose"
              >
                Annuler
              </button>
              <button
                type="button"
                class="btn-primary"
                :disabled="!selectedAffairId || localStore.isMutating"
                @click="submitSend"
              >
                {{ localStore.isMutating ? 'Envoi en cours...' : 'Envoyer' }}
              </button>
            </footer>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import type { SiraCategory } from '../../stores/documentStore';
import { useClientDossierStore } from '../../stores/dossierStore';
import { SIRA_STEPS } from '../../stores/siraStore';
import { useLocalManagerStore } from '../../stores/localManagerStore';

const props = defineProps<{
  isOpen: boolean;
  sourceName: string;
  sourcePath: string;
  isDirectory: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'sent', payload: { affairId: string; uploadedCount: number }): void;
}>();

const router = useRouter();
const dossierStore = useClientDossierStore();
const localStore = useLocalManagerStore();

const dossierSearch = ref('');
const selectedAffairId = ref('');
const selectedCategory = ref<SiraCategory>('IDENTIFICATION');
const transferResult = ref<{ uploadedCount: number; skippedCount: number } | null>(null);

const filteredDossiers = computed(() => {
  const q = dossierSearch.value.trim().toLowerCase();
  if (!q) return dossierStore.allDossiers;
  return dossierStore.allDossiers.filter((d) => {
    return [d.title, d.reference_affair, d.client?.nom_complet].some((v) =>
      (v || '').toLowerCase().includes(q)
    );
  });
});

watch(
  () => props.isOpen,
  async (open) => {
    if (open) {
      localStore.clearError();
      dossierSearch.value = '';
      transferResult.value = null;
      selectedCategory.value = 'IDENTIFICATION';
      if (dossierStore.allDossiers.length === 0) {
        await dossierStore.fetchAllDossiers();
      }
      if (!selectedAffairId.value && dossierStore.allDossiers.length > 0) {
        selectedAffairId.value = dossierStore.allDossiers[0].id;
      }
    }
  }
);

watch(filteredDossiers, (list) => {
  if (list.length > 0 && !list.some((d) => d.id === selectedAffairId.value)) {
    selectedAffairId.value = list[0].id;
  }
});

function handleClose() {
  if (localStore.isMutating) return;
  localStore.clearError();
  emit('close');
}

async function submitSend() {
  if (!selectedAffairId.value || !props.sourcePath || localStore.isMutating) return;
  const res = await localStore.sendToWorkspace(
    selectedAffairId.value,
    props.sourcePath,
    props.isDirectory,
    selectedCategory.value
  );
  if (res.ok) {
    transferResult.value = {
      uploadedCount: res.uploadedCount,
      skippedCount: res.skippedCount,
    };
    emit('sent', {
      affairId: selectedAffairId.value,
      uploadedCount: res.uploadedCount,
    });
  }
}

function openTargetDossier() {
  const targetId = selectedAffairId.value;
  transferResult.value = null;
  emit('close');
  if (targetId) {
    router.push(`/dashboard/affairs/${targetId}`);
  }
}
</script>

<style scoped>
.send-ws-overlay {
  position: fixed;
  inset: 0;
  z-index: 10020;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.send-ws-card {
  width: 100%;
  max-width: 470px;
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.2);
  overflow: hidden;
}

.send-ws-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
}

.send-ws-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}

.send-ws-close {
  background: none;
  border: none;
  font-size: 1.4rem;
  line-height: 1;
  color: #64748b;
  cursor: pointer;
  padding: 0.1rem 0.35rem;
}

.send-ws-close:hover {
  color: #0f172a;
}

.send-ws-body {
  padding: 1.15rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.95rem;
}

.source-summary {
  padding: 0.75rem 0.9rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.source-label {
  font-size: 0.74rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.source-name {
  font-size: 0.92rem;
  font-weight: 600;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.source-hint {
  font-size: 0.78rem;
  color: #64748b;
  line-height: 1.4;
  margin-top: 0.15rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.field-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
}

.text-input,
.select-field {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #d1d5db;
  border-radius: 9px;
  padding: 0.55rem 0.75rem;
  font-size: 0.86rem;
  color: #0f172a;
  background: #ffffff;
  outline: none;
}

.text-input:focus,
.select-field:focus {
  border-color: var(--primary-color, #005792);
}

.error-text {
  margin: 0;
  font-size: 0.82rem;
  color: #dc2626;
}

.send-ws-success {
  text-align: center;
  padding-top: 1.5rem;
}

.success-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
}

.success-sub {
  margin: 0;
  font-size: 0.83rem;
  color: #64748b;
}

.send-ws-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  padding-top: 0.35rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.55rem 1rem;
  border-radius: 9px;
  font-size: 0.86rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  border: none;
  background: var(--primary-color, #005792);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-dark, #005380);
}

.btn-secondary {
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #334155;
}

.btn-secondary:hover:not(:disabled) {
  background: #f8fafc;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>

