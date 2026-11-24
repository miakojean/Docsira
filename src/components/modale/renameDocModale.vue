<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen" class="rename-modal-overlay" @click.self="$emit('close')">
        <div class="rename-modal-card" role="dialog" aria-modal="true">
          <div class="rename-modal-header">
            <h3 class="rename-modal-title">{{ title }}</h3>
            <button type="button" class="rename-modal-close" @click="$emit('close')">×</button>
          </div>
          <div class="rename-modal-body">
            <label class="input-label" for="renameDocInput">{{ label }}</label>
            <input
              ref="inputRef"
              id="renameDocInput"
              type="text"
              v-model="renameValue"
              class="text-input"
              :placeholder="placeholder"
              :disabled="isLoading"
              @keyup.enter="handleConfirm"
            />
            <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
          </div>
          <div class="rename-modal-footer">
            <button type="button" class="btn" :disabled="isLoading" @click="$emit('close')">Annuler</button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!isValid || isLoading"
              @click="handleConfirm"
            >
              {{ isLoading ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, computed, nextTick } from 'vue';

const props = withDefaults(
  defineProps<{
    isOpen: boolean;
    initialName?: string;
    title?: string;
    label?: string;
    placeholder?: string;
    isLoading?: boolean;
    errorMessage?: string;
  }>(),
  {
    initialName: '',
    title: 'Renommer le document',
    label: 'Titre du document',
    placeholder: 'Nom du document',
    isLoading: false,
    errorMessage: '',
  }
);

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'rename', newName: string): void;
}>();

const renameValue = ref('');
const inputRef = ref<HTMLInputElement | null>(null);

watch(
  () => [props.isOpen, props.initialName],
  async () => {
    if (props.isOpen) {
      renameValue.value = props.initialName ?? '';
      await nextTick();
      inputRef.value?.focus();
      inputRef.value?.select();
    }
  },
  { immediate: true }
);

const isValid = computed(() => {
  const trimmed = renameValue.value.trim();
  return trimmed.length > 0 && trimmed !== (props.initialName ?? '');
});

function handleConfirm() {
  if (isValid.value && !props.isLoading) {
    emit('rename', renameValue.value.trim());
  }
}
</script>

<style scoped>
.rename-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.rename-modal-card {
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

.rename-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rename-modal-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: #111827;
}

.rename-modal-close {
  background: none;
  border: none;
  font-size: 1.4rem;
  color: #9ca3af;
  cursor: pointer;
  line-height: 1;
}

.rename-modal-close:hover {
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

.error-text {
  margin: 0.45rem 0 0;
  font-size: 0.8rem;
  color: #dc2626;
}

.rename-modal-footer {
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
