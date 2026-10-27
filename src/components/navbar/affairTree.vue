<template>
  <aside class="tree-panel">
    <!-- En-tête -->
    <div class="tree-header">
      <h2 class="tree-title">Dossiers</h2>
      <button type="button" class="icon-btn" title="Retour aux dossiers" @click="router.push('/dashboard/affairs')">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
        </svg>
      </button>
    </div>

    <!-- Recherche -->
    <label class="search-box">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
      </svg>
      <input v-model="query" type="search" placeholder="Rechercher..." />
    </label>

    <!-- Onglets -->
    <div class="tabs" role="tablist">
      <button type="button" role="tab" class="tab" :class="{ active: tab === 'folders' }" @click="tab = 'folders'">Dossiers</button>
      <button type="button" role="tab" class="tab" :class="{ active: tab === 'files' }" @click="tab = 'files'">Documents</button>
    </div>

    <!-- Arborescence -->
    <nav v-if="tab === 'folders'" class="tree">
      <div v-for="d in filteredDossiers" :key="d.id" class="tree-group">
        <button
          type="button"
          class="tree-row"
          :class="{ active: d.id === currentId }"
          @click="goTo(d)"
        >
          <svg
            v-if="d.id === currentId"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            class="row-icon"
          >
            <path d="M19.5 21a3 3 0 0 0 3-3v-4.5a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3V18a3 3 0 0 0 3 3h15ZM1.5 10.146V6a3 3 0 0 1 3-3h5.379a2.25 2.25 0 0 1 1.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 0 1 3 3v1.146A4.483 4.483 0 0 0 19.5 9h-15a4.483 4.483 0 0 0-3 1.146Z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="row-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
          </svg>
          <span class="row-label">{{ d.client?.nom_complet || d.title }}</span>
          <span class="row-count">{{ d.id === currentId ? documents.length : (d.documents_count ?? 0) }}</span>
        </button>

        <!-- Documents du dossier ouvert -->
        <ul v-if="d.id === currentId && documents.length" class="tree-children">
          <li v-for="doc in documents" :key="doc.id" class="tree-child">
            <button type="button" class="tree-row child" :title="doc.title" @click="emit('openDocument', doc)">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="row-icon" :class="extClass(doc.extension)">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
              <span class="row-label">{{ doc.title }}</span>
            </button>
          </li>
        </ul>
      </div>

      <p v-if="filteredDossiers.length === 0" class="tree-empty">Aucun dossier trouvé</p>
    </nav>

    <!-- Liste à plat des documents du dossier courant -->
    <nav v-else class="tree">
      <ul class="tree-children flat">
        <li v-for="doc in filteredDocuments" :key="doc.id" class="tree-child">
          <button type="button" class="tree-row" :title="doc.title" @click="emit('openDocument', doc)">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="row-icon" :class="extClass(doc.extension)">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
            <span class="row-label">{{ doc.title }}</span>
          </button>
        </li>
      </ul>
      <p v-if="filteredDocuments.length === 0" class="tree-empty">Aucun document</p>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useClientDossierStore, type Dossier } from '../../stores/dossierStore';
import type { DossierDocument } from '../../stores/documentStore';

const props = defineProps<{
  currentId: string;
  documents: DossierDocument[];
}>();

const emit = defineEmits<{
  openDocument: [doc: DossierDocument];
}>();

const router = useRouter();
const store = useClientDossierStore();

const query = ref('');
const tab = ref<'folders' | 'files'>('folders');

const filteredDossiers = computed(() => {
  const q = query.value.trim().toLowerCase();
  return store.allDossiers.filter(
    (d) =>
      !q ||
      [d.title, d.reference_affair, d.client?.nom_complet].some((v) => (v || '').toLowerCase().includes(q))
  );
});

const filteredDocuments = computed(() => {
  const q = query.value.trim().toLowerCase();
  return props.documents.filter((d) => !q || d.title.toLowerCase().includes(q));
});

function goTo(d: Dossier) {
  if (d.id !== props.currentId) router.push(`/dashboard/affairs/${d.id}`);
}

function extClass(ext: string) {
  const e = (ext || '').toLowerCase();
  if (e === 'pdf') return 'is-pdf';
  if (['doc', 'docx', 'odt', 'rtf', 'txt'].includes(e)) return 'is-word';
  return '';
}

onMounted(() => {
  if (store.allDossiers.length === 0) store.fetchAllDossiers();
});
</script>

<style scoped>
.tree-panel {
  width: 280px;
  flex-shrink: 0;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fafafa;
  border-right: 1px solid #e5e7eb;
}

.tree-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1rem 0.75rem;
  border-bottom: 1px solid #eceef1;
}

.tree-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #1f2937;
}

.icon-btn {
  background: none;
  border: none;
  color: #6b7280;
  padding: 0.3rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
}

.icon-btn:hover {
  background: #eceef1;
  color: #111827;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 1rem;
  color: #9ca3af;
  border-bottom: 1px solid #eceef1;
}

.search-box input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.9rem;
  color: #111827;
}

.tabs {
  display: flex;
  margin: 0.75rem;
  padding: 3px;
  background: #eef0f2;
  border-radius: 12px;
}

.tab {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.4rem 0;
  border-radius: 9px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab.active {
  background: #ffffff;
  color: #111827;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tree {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0 0.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tree-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.6rem;
  border: none;
  background: transparent;
  border-radius: 10px;
  font-size: 0.88rem;
  color: #1f2937;
  cursor: pointer;
  text-align: left;
  transition: background-color 0.15s ease;
}

.tree-row:hover {
  background: #eef0f2;
}

.tree-row.active {
  background: #e9ebee;
  font-weight: 500;
}

.row-icon {
  width: 1.1rem;
  height: 1.1rem;
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

.row-count {
  font-size: 0.78rem;
  font-weight: 500;
  color: #4b5563;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  padding: 0.05rem 0.55rem;
  min-width: 1.6rem;
  text-align: center;
}

.tree-row.active .row-count {
  background: #ffffff;
}

/* Lignes d'arborescence */
.tree-children {
  list-style: none;
  margin: 0 0 0 1.25rem;
  padding: 0 0 0 0.4rem;
  border-left: 1px solid #d1d5db;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tree-children.flat {
  margin: 0;
  padding: 0;
  border-left: none;
}

.tree-child {
  position: relative;
}

.tree-children:not(.flat) .tree-child::before {
  content: '';
  position: absolute;
  left: -0.4rem;
  top: 50%;
  width: 0.5rem;
  border-top: 1px solid #d1d5db;
}

.tree-row.child {
  font-size: 0.85rem;
}

.tree-empty {
  margin: 1rem;
  text-align: center;
  font-size: 0.85rem;
  color: #9ca3af;
}

@media (max-width: 1023px) {
  .tree-panel {
    display: none;
  }
}
</style>
