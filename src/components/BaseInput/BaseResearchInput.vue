<template>
  <div class="research-wrapper">
    <div class="flex items-center">

      <div class="input-container">
        <input 
          ref="inputRef"
          type="text" 
          class="research-input" 
          :placeholder="placeholder"
          :value="modelValue"
          @input="onInput"
        >
        <button
          v-if="modelValue"
          type="button"
          class="clear-btn"
          aria-label="Effacer la recherche"
          @click="clearInput"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4">
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

withDefaults(
  defineProps<{
    modelValue?: string;
    placeholder?: string;
  }>(),
  {
    modelValue: '',
    placeholder: 'Rechercher...'
  }
);

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
}>();

const inputRef = ref<HTMLInputElement | null>(null);

function onInput(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target) {
    emit('update:modelValue', target.value);
  }
}

function clearInput() {
  emit('update:modelValue', '');
  inputRef.value?.focus();
}
</script>

<style scoped>
.research-wrapper {
  display: inline-flex;
}

.flex {
  display: flex;
  align-items: center;
}

/* ---------- Input container ---------- */
.input-container {
  position: relative;
  display: flex;
  align-items: center;
  margin-left: 0.5rem;
}

/* ---------- Input (always unfolded and visible) ---------- */
.research-input {
  box-sizing: border-box;
  width: 250px;
  height: 40px;
  padding: 0.5rem 2.2rem 0.5rem 1rem;
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--text-color, #222);
  background-color: #fff;
  border: 1px solid #dfdfdf;
  border-radius: 999px;
  outline: none;
  opacity: 1;
  pointer-events: auto;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, width 0.2s ease;
}

.research-input::placeholder {
  color: #9ca3af;
  font-size: 0.9rem;
}

.research-input:hover {
  border-color: #cbd5e1;
}

.research-input:focus {
  border-color: var(--primary-color-ligth, #325aaf);
  box-shadow: 0 0 0 3px rgba(0, 87, 146, 0.12);
  width: 270px;
}

/* ---------- Clear button ---------- */
.clear-btn {
  position: absolute;
  right: 0.65rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  padding: 0;
  color: #9ca3af;
  background: transparent;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.clear-btn:hover {
  color: #4b5563;
  background-color: #f3f4f6;
}
</style>