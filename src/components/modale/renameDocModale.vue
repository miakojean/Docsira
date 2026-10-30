<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen" class="modal-backdrop" @click.self="$emit('close')">
        <div class="modal-box">
          <div class="modal-box-header">
            <h3 class="modal-box-title">Renommer le document</h3>
            <button type="button" class="modal-box-close" @click="$emit('close')">×</button>
          </div>
          <div class="modal-box-body">
            <label class="input-label" for="renameDocInput">Titre du document</label>
            <input
              id="renameDocInput"
              type="text"
              v-model="renameValue"
              class="text-input"
              placeholder="Nom du document"
              @keyup.enter="handleConfirm"
              autofocus
            />
          </div>
          <div class="modal-box-footer">
            <button type="button" class="btn btn-secondary" @click="$emit('close')">Annuler</button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!isValid"
              @click="handleConfirm"
            >
              Enregistrer
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';

const props = defineProps<{
  isOpen: boolean;
  initialName?: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'rename', newName: string): void;
}>();

const renameValue = ref('');

watch(
  () => [props.isOpen, props.initialName],
  () => {
    if (props.isOpen) {
      renameValue.value = props.initialName ?? '';
    }
  },
  { immediate: true }
);

const isValid = computed(() => {
  const trimmed = renameValue.value.trim();
  return trimmed.length > 0 && trimmed !== (props.initialName ?? '');
});

function handleConfirm() {
  if (isValid.value) {
    emit('rename', renameValue.value.trim());
  }
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

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
