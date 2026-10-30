<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen && document" class="modal-backdrop" @click.self="$emit('close')">
        <div class="modal-box">
          <div class="modal-box-header">
            <h3 class="modal-box-title">Déplacer le document</h3>
            <button type="button" class="modal-box-close" @click="$emit('close')">&times;</button>
          </div>
          <div class="modal-box-body">
            <p class="destination-hint">
              Sélectionnez l'emplacement de destination pour <strong>{{ document.title || document.file_name }}</strong> :
            </p>

            <div class="folder-destination-list">
              <label
                class="destination-option"
                :class="{ selected: selectedFolderId === null }"
              >
                <input
                  type="radio"
                  name="destFolder"
                  :value="null"
                  v-model="selectedFolderId"
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
                :class="{ selected: selectedFolderId === sf.id }"
              >
                <input
                  type="radio"
                  name="destFolder"
                  :value="sf.id"
                  v-model="selectedFolderId"
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
            <button type="button" class="btn btn-secondary" @click="$emit('close')">Annuler</button>
            <button type="button" class="btn btn-primary" @click="handleConfirm">Déplacer ici</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import type { DossierDocument } from '../../stores/documentStore';
import type { AffairSubfolder } from '../../stores/affairFolderStore';

const props = defineProps<{
  isOpen: boolean;
  document: DossierDocument | null;
  subfolders: AffairSubfolder[];
  initialFolderId?: string | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'confirm', targetFolderId: string | null): void;
}>();

const selectedFolderId = ref<string | null>(null);

watch(
  () => [props.isOpen, props.initialFolderId],
  () => {
    if (props.isOpen) {
      selectedFolderId.value = props.initialFolderId ?? null;
    }
  },
  { immediate: true }
);

function handleConfirm() {
  emit('confirm', selectedFolderId.value);
}
</script>

<style scoped>
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
