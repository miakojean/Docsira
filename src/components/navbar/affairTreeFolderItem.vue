<template>
  <li class="tree-child folder-node">
    <div class="tree-row-wrapper" :class="{ active: currentFolderId === folder.id }">
      <!-- Bouton chevron pour déplier / replier -->
      <button
        type="button"
        class="tree-chevron-btn"
        :class="{ expanded: isExpanded }"
        :title="isExpanded ? 'Replier le dossier' : 'Déplier le dossier'"
        @click.stop="emit('toggleFolder', folder.id)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="chevron-svg">
          <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
      </button>

      <!-- Bouton de sélection du dossier -->
      <button
        type="button"
        class="tree-row child folder-btn"
        :title="folder.name"
        @click="emit('selectFolder', folder.id)"
      >
        <!-- Icône de dossier (ouvert si déplié, fermé sinon) -->
        <svg
          v-if="isExpanded"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          class="row-icon folder-icon is-open"
        >
          <path d="M19.5 21a3 3 0 0 0 3-3v-4.5a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3V18a3 3 0 0 0 3 3h15ZM1.5 10.146V6a3 3 0 0 1 3-3h5.379a2.25 2.25 0 0 1 1.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 0 1 3 3v1.146A4.483 4.483 0 0 0 19.5 9h-15a4.483 4.483 0 0 0-3 1.146Z" />
        </svg>
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.6"
          stroke="currentColor"
          class="row-icon folder-icon"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
        </svg>
        <span class="row-label">{{ folder.name }}</span>
        <span class="row-count mini">{{ childDocuments.length }}</span>
      </button>
    </div>

    <!-- Contenu déplié du sous-dossier -->
    <ul v-if="isExpanded" class="tree-children nested">
      <!-- Sous-dossiers enfants récursifs -->
      <affairTreeFolderItem
        v-for="child in childSubfolders"
        :key="child.id"
        :folder="child"
        :allSubfolders="allSubfolders"
        :allDocuments="allDocuments"
        :docFolderMap="docFolderMap"
        :currentFolderId="currentFolderId"
        :expandedFolderIds="expandedFolderIds"
        @selectFolder="emit('selectFolder', $event)"
        @openDocument="emit('openDocument', $event)"
        @toggleFolder="emit('toggleFolder', $event)"
      />

      <!-- Documents de ce sous-dossier -->
      <li v-for="doc in childDocuments" :key="doc.id" class="tree-child">
        <button
          type="button"
          class="tree-row child doc-row"
          :title="doc.title"
          @click="emit('openDocument', doc)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="row-icon" :class="extClass(doc.extension)">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
          <span class="row-label">{{ doc.title }}</span>
        </button>
      </li>

      <!-- Indicateur discret si vide -->
      <li v-if="childSubfolders.length === 0 && childDocuments.length === 0" class="tree-child empty-node">
        <span class="empty-node-text">(dossier vide)</span>
      </li>
    </ul>
  </li>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { AffairSubfolder } from '../../stores/affairFolderStore';
import type { DossierDocument } from '../../stores/documentStore';

defineOptions({
  name: 'affairTreeFolderItem',
});

const props = defineProps<{
  folder: AffairSubfolder;
  allSubfolders: AffairSubfolder[];
  allDocuments: DossierDocument[];
  docFolderMap: Record<string, string>;
  currentFolderId: string | null;
  expandedFolderIds: Set<string>;
}>();

const emit = defineEmits<{
  selectFolder: [folderId: string];
  openDocument: [doc: DossierDocument];
  toggleFolder: [folderId: string];
}>();

const isExpanded = computed(() => props.expandedFolderIds.has(props.folder.id));

const childSubfolders = computed(() => {
  return props.allSubfolders.filter((f) => f.parentId === props.folder.id);
});

const childDocuments = computed(() => {
  return props.allDocuments.filter((d) => props.docFolderMap[d.id] === props.folder.id);
});

function extClass(ext: string) {
  const e = (ext || '').toLowerCase();
  if (e === 'pdf') return 'is-pdf';
  if (['doc', 'docx', 'odt', 'rtf', 'txt'].includes(e)) return 'is-word';
  return '';
}
</script>

<style scoped>
.folder-node {
  position: relative;
}

.tree-row-wrapper {
  display: flex;
  align-items: center;
  border-radius: 8px;
  transition: background-color 0.15s ease;
  position: relative;
}

.tree-row-wrapper:hover {
  background: #eef0f2;
}

.tree-row-wrapper.active {
  background: #e9ebee;
}

.tree-row-wrapper.active .folder-btn {
  font-weight: 600;
  color: #2563eb;
}

.tree-chevron-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.35rem;
  height: 1.8rem;
  padding: 0;
  margin-left: 0.2rem;
  border: none;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 4px;
  flex-shrink: 0;
  transition: color 0.15s ease;
}

.tree-chevron-btn:hover {
  color: #1f2937;
  background: rgba(0, 0, 0, 0.04);
}

.chevron-svg {
  width: 0.75rem;
  height: 0.75rem;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.tree-chevron-btn.expanded .chevron-svg {
  transform: rotate(90deg);
}

.folder-btn {
  flex: 1;
  min-width: 0;
  padding-left: 0.25rem !important;
}

.folder-icon {
  color: #f59e0b;
}

.tree-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.45rem 0.6rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #1f2937;
  cursor: pointer;
  text-align: left;
  transition: background-color 0.15s ease;
}

.row-icon {
  width: 1.05rem;
  height: 1.05rem;
  flex-shrink: 0;
  color: #6b7280;
}

.row-icon.is-pdf { color: #ef4444; }
.row-icon.is-word { color: #3b82f6; }

.row-label {
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-count.mini {
  font-size: 0.72rem;
  font-weight: 500;
  color: #4b5563;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  padding: 0.02rem 0.45rem;
  min-width: 1.3rem;
  text-align: center;
}

.tree-row-wrapper.active .row-count.mini {
  background: #ffffff;
}

/* Lignes de hiérarchie imbriquée */
.tree-children.nested {
  list-style: none;
  margin: 2px 0 2px 0.85rem;
  padding: 0 0 0 0.4rem;
  border-left: 1px solid #d1d5db;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tree-child {
  position: relative;
}

.tree-children.nested > .tree-child::before {
  content: '';
  position: absolute;
  left: -0.4rem;
  top: 1rem;
  width: 0.5rem;
  border-top: 1px solid #d1d5db;
}

.tree-row.child {
  font-size: 0.83rem;
}

.tree-row.child:hover {
  background: #eef0f2;
}

.empty-node {
  padding: 0.2rem 0.6rem 0.2rem 0.4rem;
}

.empty-node-text {
  font-size: 0.75rem;
  color: #9ca3af;
  font-style: italic;
}
</style>
