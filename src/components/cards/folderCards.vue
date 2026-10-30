<template>
  <div
    class="folder-card"
    :class="{ 'is-drag-target': isDragOver }"
    @click="$emit('open')"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
  >
    <!-- Menu d'actions (Renommer / Supprimer) -->
    <div class="folder-card__actions" @click.stop>
      <button
        type="button"
        class="action-kebab-btn"
        title="Options du dossier"
        @click="isMenuOpen = !isMenuOpen"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
        </svg>
      </button>

      <!-- Dropdown -->
      <div v-if="isMenuOpen" class="actions-dropdown">
        <button type="button" class="dropdown-item" @click="handleRename">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
          </svg>
          <span>Renommer</span>
        </button>
        <button type="button" class="dropdown-item is-danger" @click="handleDelete">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
          </svg>
          <span>Supprimer</span>
        </button>
      </div>
    </div>

    <!-- Icône du dossier -->
    <div class="folder-card__icon-wrapper">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.2" stroke="currentColor" class="folder-icon">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
      </svg>
    </div>

    <!-- Pied de carte -->
    <div class="folder-card__footer">
      <h3 class="folder-card__name" :title="folderName">{{ folderName }}</h3>
      
      <span v-if="itemCount !== undefined" class="folder-card__count">
        {{ itemCount }} {{ itemCount > 1 ? 'documents' : 'document' }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

defineProps<{
  folderName: string;
  itemCount?: number;
}>();

const emit = defineEmits<{
  open: [];
  rename: [];
  delete: [];
  dropDoc: [docId: string];
}>();

const isMenuOpen = ref(false);
const isDragOver = ref(false);

function handleRename() {
  isMenuOpen.value = false;
  emit('rename');
}

function handleDelete() {
  isMenuOpen.value = false;
  emit('delete');
}

function onDragOver(e: DragEvent) {
  isDragOver.value = true;
  if (e.dataTransfer) {
    e.dataTransfer.dropEffect = 'move';
  }
}

function onDragLeave() {
  isDragOver.value = false;
}

function onDrop(e: DragEvent) {
  isDragOver.value = false;
  const docId = e.dataTransfer?.getData('text/plain');
  if (docId) {
    emit('dropDoc', docId);
  }
}

function onWindowClick() {
  if (isMenuOpen.value) isMenuOpen.value = false;
}

onMounted(() => {
  window.addEventListener('click', onWindowClick);
});

onUnmounted(() => {
  window.removeEventListener('click', onWindowClick);
});
</script>

<style scoped>
:root {
  --primary-color: #2563eb;
}

.folder-card {
  width: 100%;
  max-width: 260px;
  min-height: 220px;
  aspect-ratio: 1 / 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  padding: 1.25rem;
  background: #ffffff;
  border-radius: 16px;
  border: 2px solid transparent;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.folder-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.12);
  border-color: #2563eb;
}

.folder-card.is-drag-target {
  border-color: #2563eb;
  background: #eff6ff;
  transform: scale(1.03);
}

/* --- Bouton d'options 3 points --- */
.folder-card__actions {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  z-index: 5;
}

.action-kebab-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-kebab-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.actions-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.25rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  padding: 0.35rem;
  min-width: 140px;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.65rem;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #374151;
  font-size: 0.85rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.dropdown-item:hover {
  background: #f3f4f6;
  color: #111827;
}

.dropdown-item.is-danger {
  color: #dc2626;
}

.dropdown-item.is-danger:hover {
  background: #fef2f2;
}

/* --- Zone de l'icône --- */
.folder-card__icon-wrapper {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.folder-icon {
  width: 72px;
  height: 72px;
}

.folder-card:hover .folder-card__icon-wrapper {
  color: #2563eb;
  transform: scale(1.1);
}

/* --- Zone du texte --- */
.folder-card__footer {
  width: 100%;
  text-align: center;
  margin-top: 0.75rem;
}

.folder-card__name {
  margin: 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.3s ease;
}

.folder-card:hover .folder-card__name {
  color: #2563eb;
}

.folder-card__count {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.78rem;
  color: #6b7280;
  font-weight: 500;
}
</style>