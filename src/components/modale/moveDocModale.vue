<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen && document" class="move-modal-overlay" @click.self="$emit('close')">
        <div class="move-modal-card" role="dialog" aria-modal="true">
          <div class="move-modal-header">
            <h3 class="move-modal-title">Déplacer le document</h3>
            <button type="button" class="move-modal-close" :disabled="isMoving" @click="$emit('close')">&times;</button>
          </div>

          <div class="move-modal-body">
            <p class="destination-hint">
              Choisissez le dossier de destination pour <strong>{{ document.title || document.file_name }}</strong> :
            </p>

            <!-- Autre dossier (affaire) du cabinet -->
            <div class="affair-picker">
              <input
                v-model="affairSearch"
                type="text"
                class="search-input"
                placeholder="Rechercher un dossier par titre ou référence..."
              />

              <div v-if="filteredOtherDossiers.length > 0" class="folder-destination-list">
                <label
                  v-for="target in filteredOtherDossiers"
                  :key="target.id"
                  class="destination-option"
                  :class="{ selected: selectedAffairId === target.id }"
                >
                  <input
                    type="radio"
                    name="destAffair"
                    :value="target.id"
                    v-model="selectedAffairId"
                  />
                  <div class="dest-icon affair">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
                    </svg>
                  </div>
                  <div class="dest-label">
                    <strong>{{ target.title }}</strong>
                    <span>{{ target.reference_affair }}{{ target.client?.nom_complet ? ` • ${target.client.nom_complet}` : '' }}</span>
                  </div>
                </label>
              </div>

              <p v-else class="empty-hint">
                Aucun autre dossier trouvé.
              </p>
            </div>
          </div>

          <div class="move-modal-footer">
            <button type="button" class="btn" :disabled="isMoving" @click="$emit('close')">
              Annuler
            </button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!canConfirm || isMoving"
              @click="handleConfirm"
            >
              {{ isMoving ? 'Déplacement...' : 'Déplacer ici' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { DossierDocument } from '../../stores/documentStore';
import type { Dossier } from '../../stores/dossierStore';

export interface MoveDocPayload {
  targetAffairId: string | null;
}

const props = withDefaults(
  defineProps<{
    isOpen: boolean;
    document: DossierDocument | null;
    otherDossiers?: Dossier[];
    isMoving?: boolean;
  }>(),
  {
    otherDossiers: () => [],
    isMoving: false,
  }
);

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'confirm', payload: MoveDocPayload): void;
}>();

const selectedAffairId = ref<string | null>(null);
const affairSearch = ref('');

const filteredOtherDossiers = computed(() => {
  const q = affairSearch.value.trim().toLowerCase();
  if (!q) return props.otherDossiers;
  return props.otherDossiers.filter(
    (d) =>
      d.title?.toLowerCase().includes(q) ||
      d.reference_affair?.toLowerCase().includes(q) ||
      d.client?.nom_complet?.toLowerCase().includes(q)
  );
});

const canConfirm = computed(() => Boolean(selectedAffairId.value));

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      selectedAffairId.value = null;
      affairSearch.value = '';
    }
  },
  { immediate: true }
);

function handleConfirm() {
  if (!canConfirm.value || props.isMoving) return;
  emit('confirm', { targetAffairId: selectedAffairId.value });
}
</script>

<style scoped>
.move-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.move-modal-card {
  width: 100%;
  max-width: 480px;
  background: #ffffff;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.move-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.move-modal-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: #111827;
}

.move-modal-close {
  background: none;
  border: none;
  font-size: 1.4rem;
  color: #9ca3af;
  cursor: pointer;
  line-height: 1;
}

.move-modal-close:hover {
  color: #4b5563;
}

.destination-hint {
  font-size: 0.88rem;
  color: #4b5563;
  margin: 0 0 0.75rem;
}

.mode-tabs {
  display: flex;
  gap: 0.4rem;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 10px;
  margin-bottom: 0.85rem;
}

.mode-tab {
  flex: 1;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0.48rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mode-tab.active {
  background: #ffffff;
  color: #1e40af;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
}

.affair-picker {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.search-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.55rem 0.85rem;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  font-size: 0.85rem;
  outline: none;
  background: #f9fafb;
  color: #111827;
}

.search-input:focus {
  border-color: var(--primary-color, #2563eb);
  background: #ffffff;
}

.folder-destination-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 260px;
  overflow-y: auto;
  padding: 0.15rem 0;
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

.dest-icon.affair {
  background: #dbeafe;
  color: #1d4ed8;
}

.dest-label {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.dest-label strong {
  font-size: 0.88rem;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dest-label span {
  font-size: 0.76rem;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-hint {
  margin: 0.5rem 0;
  text-align: center;
  font-size: 0.85rem;
  color: #64748b;
}

.move-modal-footer {
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color, #2563eb);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-dark, #1d4ed8);
}

.size-5 {
  width: 1.25rem;
  height: 1.25rem;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
