<template>
  <div class="input-group" :class="{ 'has-error': !!errorMessage, 'is-disabled': disabled }">
    <label v-if="label" :for="inputId" class="input-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>

    <div class="select-wrapper">
      <select
        :id="inputId"
        :value="modelValue"
        :disabled="disabled"
        class="select-input"
        :class="{ 'has-placeholder': !modelValue && placeholder }"
        @change="handleChange"
      >
        <option v-if="placeholder" value="" disabled :selected="!modelValue">
          {{ placeholder }}
        </option>

        <template v-if="groups && groups.length">
          <optgroup
            v-for="group in groups"
            :key="group.category"
            :label="group.category"
          >
            <option
              v-for="opt in group.options"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </option>
          </optgroup>
        </template>

        <template v-else-if="options && options.length">
          <option
            v-for="opt in options"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.label }}
          </option>
        </template>
      </select>

      <div class="select-icon" aria-hidden="true">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="chevron-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
        </svg>
      </div>
    </div>

    <p v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import type { DossierTypeGroup, DossierTypeOption } from '../../helpers/dossierTypes';

withDefaults(
  defineProps<{
    modelValue?: string | number;
    label?: string;
    placeholder?: string;
    errorMessage?: string;
    required?: boolean;
    disabled?: boolean;
    inputId?: string;
    groups?: DossierTypeGroup[];
    options?: DossierTypeOption[];
  }>(),
  {
    modelValue: '',
    label: '',
    placeholder: '',
    errorMessage: '',
    required: false,
    disabled: false,
    inputId: '',
    groups: () => [],
    options: () => [],
  }
);

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'change', value: string): void;
}>();

function handleChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  emit('update:modelValue', target.value);
  emit('change', target.value);
}
</script>

<style scoped>
.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  width: 100%;
}

.input-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #6b7280;
}

.required-mark {
  color: #dc2626;
  margin-left: 0.2rem;
}

.select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.select-input {
  width: 100%;
  box-sizing: border-box;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  padding: 0.7rem 2.5rem 0.7rem 0.9rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.9rem;
  outline: none;
  background: #f9fafb;
  color: #111827;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s, background-color 0.2s;
}

.select-input:hover:not(:disabled) {
  border-color: #cbd5e1;
  background: #ffffff;
}

.select-input:focus {
  border-color: var(--primary-color, #005792);
  box-shadow: 0 0 0 3px rgba(0, 87, 146, 0.12);
  background: #ffffff;
}

.select-input:disabled {
  background-color: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}

.select-icon {
  position: absolute;
  right: 0.85rem;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.chevron-icon {
  width: 16px;
  height: 16px;
}

.error-message {
  margin: 0;
  font-size: 0.8rem;
  color: #dc2626;
}

.input-group.has-error .select-input {
  border-color: #ef4444;
  background-color: #fef2f2;
}

.input-group.has-error .select-input:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
}
</style>
