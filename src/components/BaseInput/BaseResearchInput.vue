<template>
  <div class="research-wrapper">
    <div class="flex">
        <button class="research-btn" type="button" aria-label="Search">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round"
                d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
            </svg>
        </button>

        <input 
            type="text" 
            class="research-input" 
            placeholder="Trouver un collaborateur"
            :value="modelValue"
            @input="onInput"
        >
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:modelValue']);

function onInput(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target) {
    emit('update:modelValue', target.value);
  }
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

/* ---------- Button ---------- */
.research-btn {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color-dark);
  padding: 0.5rem;
  color: #fff;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.research-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgb(0 0 0 / 0.15);
}

/* ---------- Input (collapsed by default) ---------- */
.research-input {
  box-sizing: border-box;
  width: 250px;
  max-width: 0;
  min-width: 0;
  margin-left: 0;
  padding: 0.8rem 0;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--text-color);
  background-color: #fff;
  border: 1px solid #dfdfdf;
  border-radius: 1.5rem;
  outline: none;
  opacity: 0;
  overflow: hidden;
  pointer-events: none;   /* can't click a hidden input */

  transition:
    max-width   0.35s cubic-bezier(0.4, 0, 0.2, 1),
    padding     0.35s cubic-bezier(0.4, 0, 0.2, 1),
    margin-left 0.35s cubic-bezier(0.4, 0, 0.2, 1),
    opacity     0.2s ease,
    border-color 0.15s ease-in-out,
    box-shadow   0.15s ease-in-out;
}

/* ---------- Revealed state ---------- */
.research-wrapper:hover .research-input,
.research-wrapper:focus-within .research-input {
  max-width: 250px;
  padding: 0.8rem;
  margin-left: 0.5rem;
  opacity: 1;
  pointer-events: auto;
}

.research-input:focus {
  border-color: var(--primary-color-ligth);
  box-shadow: 0 0 0 0.2rem rgb(0 0 0 / 0.06);
}
</style>