<template>
  <div class="git-panel">
    <!-- Arbre de commit Git des jalons & documents -->
    <div class="git-graph-tree">
      <div
        v-for="(node, idx) in gitNodes"
        :key="node.id"
        class="git-step-item"
        :class="{
          'is-completed': node.status === 'completed',
          'is-head': node.status === 'head',
          'is-pending': node.status === 'pending',
        }"
      >
        <!-- Ligne de rail continue entre les jalons -->
        <div
          v-if="idx < gitNodes.length - 1"
          class="git-main-rail"
          :class="{ 'rail-active': node.status === 'completed' || (node.status === 'head' && currentProgression >= 100) }"
        ></div>

        <!-- Ligne principale du commit (Jalon) -->
        <div class="git-commit-line">
          <!-- Bullet du commit -->
          <div class="git-bullet-slot">
            <div class="git-bullet">
              <svg v-if="node.status === 'completed'" class="bullet-check" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 0 1 .143 1.052l-8 10.5a.75.75 0 0 1-1.127.075l-4.5-4.5a.75.75 0 0 1 1.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 0 1 1.05-.143Z" clip-rule="evenodd" />
              </svg>
              <span v-else-if="node.status === 'head'" class="bullet-pulse-core"></span>
            </div>
          </div>

          <!-- Détail du commit / jalon -->
          <div class="git-commit-meta">
            <div class="git-commit-title-row">
              <span class="git-hash">{{ node.threshold }}%</span>
              <span class="git-step-name">{{ node.label }}</span>
            </div>
          </div>
        </div>

        <!-- Sous-branches Git : Fichiers actifs et supprimés dans ce jalon -->
        <div v-if="node.documents.length > 0 || node.deletedDocuments.length > 0" class="git-sub-branch">
          <!-- Fichiers actifs -->
          <div
            v-for="(doc, docIdx) in node.documents"
            :key="doc.id"
            class="git-doc-row"
          >
            <!-- Connecteur de branche ├── ou └── -->
            <div
              class="git-elbow"
              :class="{ 'is-last': docIdx === node.documents.length - 1 && node.deletedDocuments.length === 0 }"
            ></div>
            
            <button
              type="button"
              class="git-doc-btn"
              :title="`Cliquer pour ouvrir ${doc.title}`"
              @click="emit('openDocument', doc)"
            >
              <div class="git-doc-bullet"></div>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="git-doc-icon" :class="extClass(doc.extension)">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
              <span class="git-doc-name">{{ doc.title }}</span>
              <span class="git-doc-ext">{{ (doc.extension || 'doc').toUpperCase() }}</span>
            </button>
          </div>

          <!-- Fichiers supprimés (visualisables directement dans le graph) -->
          <div
            v-for="(delDoc, delIdx) in node.deletedDocuments"
            :key="delDoc.id"
            class="git-doc-row is-deleted"
          >
            <div
              class="git-elbow is-del-elbow"
              :class="{ 'is-last': delIdx === node.deletedDocuments.length - 1 }"
            ></div>

            <div
              class="git-del-item"
              :title="`Supprimé le ${formatDate(delDoc.timestamp)}`"
            >
              <div class="git-del-bullet"></div>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="git-del-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
              </svg>
              <span class="git-del-name">{{ delDoc.title }}</span>
              <span v-if="delDoc.previous_progression > delDoc.new_progression" class="git-del-drop">
                -{{ delDoc.previous_progression - delDoc.new_progression }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>    

    <!-- Journal Git compact (pliable) -->
    <div class="git-log-section">
      <button
        type="button"
        class="git-log-btn"
        @click="isHistoryOpen = !isHistoryOpen"
      >
        <div class="git-log-btn-left">
          <svg class="size-3-5 text-slate-500" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0a8 8 0 1 0 8 8A8 8 0 0 0 8 0zm0 14.5a6.5 6.5 0 1 1 6.5-6.5 6.51 6.51 0 0 1-6.5 6.5z"/>
            <path d="M8 4a.75.75 0 0 0-.75.75v3.5c0 .2.08.39.22.53l2.5 2.5a.75.75 0 0 0 1.06-1.06L8.75 7.94V4.75A.75.75 0 0 0 8 4z"/>
          </svg>
          <span>git log (historique)</span>
          <span class="git-log-count">{{ siraStore.histories.length }}</span>
        </div>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2.2"
          stroke="currentColor"
          class="git-log-chevron"
          :class="{ rotated: isHistoryOpen }"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
      </button>

      <div v-if="isHistoryOpen" class="git-log-body">
        <div v-if="siraStore.isLoading" class="git-log-empty">
          <span>Chargement des commits...</span>
        </div>
        <div v-else-if="siraStore.histories.length === 0" class="git-log-empty">
          <span>Aucune modification enregistrée.</span>
        </div>
        <div v-else class="git-log-list">
          <div v-for="h in siraStore.histories" :key="h.id" class="git-log-entry">
            <div class="log-dot" :class="getActionClass(h.action_type)"></div>
            <div class="log-info">
              <div class="log-title-row">
                <span class="log-action">{{ formatActionType(h.action_type) }}</span>
                <span class="log-date">{{ formatDate(h.timestamp) }}</span>
              </div>
              <div v-if="h.document_title" class="log-doc">{{ h.document_title }}</div>
              <div class="log-diff">
                <code>{{ h.previous_progression }}% → {{ h.new_progression }}%</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import type { Dossier } from '../../stores/dossierStore';
import type { DossierDocument } from '../../stores/documentStore';
import { useSiraStore } from '../../stores/siraStore';

const props = withDefaults(
  defineProps<{
    currentId: string;
    currentDossier?: Dossier | null;
    documents: DossierDocument[];
  }>(),
  {
    currentDossier: null,
  }
);

const emit = defineEmits<{
  (e: 'openDocument', doc: DossierDocument): void;
}>();

const siraStore = useSiraStore();
const isHistoryOpen = ref(false);

const currentProgression = computed(() => {
  if (props.currentDossier?.statut === 'CLOTURE' || props.currentDossier?.statut === 'TERMINE') {
    return 100;
  }
  return props.currentDossier?.progression ?? 10;
});

const activeMilestoneIndex = computed(() => {
  const p = currentProgression.value;
  if (p >= 100) return 5;
  if (p >= 90) return 4;
  if (p >= 75) return 3;
  if (p >= 60) return 2;
  if (p >= 45) return 1;
  return 0;
});

function getDeletedDocsForCategory(cat: string) {
  const isInit = cat === 'INIT';
  const deletions = siraStore.histories.filter((h) => {
    if (h.action_type !== 'SUPPRESSION_DOCUMENT') return false;
    if (isInit) {
      return !h.category || !['IDENTIFICATION', 'CONSTITUTION', 'PROCEDURES', 'LIVRABLES', 'CLOTURE'].includes(h.category);
    }
    return h.category === cat;
  });

  const seenTitles = new Set<string>();
  const list: Array<{
    id: string;
    title: string;
    timestamp: string;
    previous_progression: number;
    new_progression: number;
  }> = [];

  for (const h of deletions) {
    const title = h.document_title || 'Document';
    if (!seenTitles.has(title)) {
      seenTitles.add(title);
      list.push({
        id: h.id,
        title,
        timestamp: h.timestamp,
        previous_progression: h.previous_progression,
        new_progression: h.new_progression,
      });
    }
  }
  return list;
}

const gitNodes = computed(() => {
  const nodes = [
    {
      id: 'init',
      category: 'INIT',
      threshold: 10,
      label: 'Initialisation',
      documents: props.documents.filter(
        (d) => !d.category || !['IDENTIFICATION', 'CONSTITUTION', 'PROCEDURES', 'LIVRABLES', 'CLOTURE'].includes(d.category)
      ),
      deletedDocuments: getDeletedDocsForCategory('INIT'),
    },
    {
      id: 'identification',
      category: 'IDENTIFICATION',
      threshold: 45,
      label: 'Identification',
      documents: props.documents.filter((d) => d.category === 'IDENTIFICATION'),
      deletedDocuments: getDeletedDocsForCategory('IDENTIFICATION'),
    },
    {
      id: 'constitution',
      category: 'CONSTITUTION',
      threshold: 60,
      label: 'Constitution',
      documents: props.documents.filter((d) => d.category === 'CONSTITUTION'),
      deletedDocuments: getDeletedDocsForCategory('CONSTITUTION'),
    },
    {
      id: 'procedures',
      category: 'PROCEDURES',
      threshold: 75,
      label: 'Procédures',
      documents: props.documents.filter((d) => d.category === 'PROCEDURES'),
      deletedDocuments: getDeletedDocsForCategory('PROCEDURES'),
    },
    {
      id: 'livrables',
      category: 'LIVRABLES',
      threshold: 90,
      label: 'Livrables',
      documents: props.documents.filter((d) => d.category === 'LIVRABLES'),
      deletedDocuments: getDeletedDocsForCategory('LIVRABLES'),
    },
    {
      id: 'cloture',
      category: 'CLOTURE',
      threshold: 100,
      label: 'Clôture',
      documents: props.documents.filter((d) => d.category === 'CLOTURE'),
      deletedDocuments: getDeletedDocsForCategory('CLOTURE'),
    },
  ];

  return nodes.map((n, idx) => {
    let status: 'completed' | 'head' | 'pending' = 'pending';
    if (idx < activeMilestoneIndex.value) {
      status = 'completed';
    } else if (idx === activeMilestoneIndex.value) {
      status = 'head';
    } else {
      status = 'pending';
    }

    return {
      ...n,
      status,
    };
  });
});

function formatActionType(action: string) {
  switch (action) {
    case 'AJOUT_DOCUMENT':
      return 'commit: ajout doc';
    case 'MAJ_DOCUMENT':
      return 'commit: mise à jour';
    case 'SUPPRESSION_DOCUMENT':
      return 'revert: suppression';
    default:
      return action;
  }
}

function getActionClass(action: string) {
  switch (action) {
    case 'AJOUT_DOCUMENT':
      return 'dot-add';
    case 'SUPPRESSION_DOCUMENT':
      return 'dot-del';
    case 'MAJ_DOCUMENT':
      return 'dot-upd';
    default:
      return 'dot-def';
  }
}

function formatDate(iso: string) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function extClass(ext: string) {
  const e = (ext || '').toLowerCase();
  if (e === 'pdf') return 'is-pdf';
  if (['doc', 'docx', 'odt', 'rtf', 'txt'].includes(e)) return 'is-word';
  return '';
}

watch(
  () => [props.currentId, props.documents.length],
  ([id]) => {
    if (id) {
      siraStore.fetchHistory(String(id));
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.currentId) {
    siraStore.fetchHistory(props.currentId);
  }
});
</script>

<style scoped>
/* ==================== VOLET 2 : GRAPH GIT SIRA ==================== */
.git-panel {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0.35rem 0.75rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  scrollbar-width: thin;
}

/* En-tête Git */

.git-branch-icon {
  width: 14px;
  height: 14px;
  color: #64748b;
  flex-shrink: 0;
}

/* Arbre Git Rail */
.git-graph-tree {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.75rem 0.65rem;
}

.git-step-item {
  position: relative;
  display: flex;
  flex-direction: column;
  padding-bottom: 0.85rem;
}

.git-step-item:last-child {
  padding-bottom: 0;
}

/* Rail vertical */
.git-main-rail {
  position: absolute;
  top: 14px;
  left: 9px;
  bottom: 0;
  width: 2px;
  background: #cbd5e1;
  z-index: 0;
  transition: background-color 0.2s ease;
}

.git-main-rail.rail-active {
  background: #2563eb;
}

/* Ligne de commit */
.git-commit-line {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  z-index: 1;
}

.git-bullet-slot {
  width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 1px;
  flex-shrink: 0;
}

.git-bullet {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.is-completed .git-bullet {
  background: #10b981;
  border-color: #10b981;
  color: #ffffff;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.is-head .git-bullet {
  border-color: #2563eb;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
}

.bullet-check {
  width: 10px;
  height: 10px;
}

.bullet-pulse-core {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #2563eb;
}

.git-commit-meta {
  flex: 1;
  min-width: 0;
}

.git-commit-title-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.git-hash {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 0.68rem;
  font-weight: 700;
  color: #475569;
  background: #f1f5f9;
  padding: 0.05rem 0.3rem;
  border-radius: 4px;
}

.git-step-name {
  font-size: 0.84rem;
  font-weight: 700;
  color: #1e293b;
}

.is-head .git-step-name {
  color: #1d4ed8;
}

.is-pending .git-step-name {
  color: #64748b;
}

/* Sous-branches pour les fichiers rattachés */
.git-sub-branch {
  margin-left: 9px;
  padding-left: 11px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.35rem;
  position: relative;
  z-index: 1;
}

.git-doc-row {
  display: flex;
  align-items: center;
  position: relative;
}

.git-elbow {
  position: absolute;
  left: -11px;
  top: -8px;
  width: 10px;
  height: 19px;
  border-left: 2px solid #cbd5e1;
  border-bottom: 2px solid #cbd5e1;
  border-bottom-left-radius: 5px;
}

.git-elbow:not(.is-last)::after {
  content: '';
  position: absolute;
  left: -2px;
  top: 17px;
  bottom: -8px;
  width: 2px;
  background: #cbd5e1;
}

.git-elbow.is-del-elbow {
  border-left-color: #fca5a5;
  border-bottom-color: #fca5a5;
  border-left-style: dashed;
  border-bottom-style: dashed;
}

.git-elbow.is-del-elbow:not(.is-last)::after {
  background: repeating-linear-gradient(
    to bottom,
    #fca5a5 0px,
    #fca5a5 3px,
    transparent 3px,
    transparent 6px
  );
}

.git-doc-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.45rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  min-width: 0;
  flex: 1;
  transition: all 0.15s ease;
}

.git-doc-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateX(2px);
}

.git-doc-bullet {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #94a3b8;
  flex-shrink: 0;
}

.git-doc-btn:hover .git-doc-bullet {
  background: #2563eb;
}

.git-doc-icon {
  width: 13px;
  height: 13px;
  color: #64748b;
  flex-shrink: 0;
}

.git-doc-icon.is-pdf { color: #ef4444; }
.git-doc-icon.is-word { color: #3b82f6; }

.git-doc-name {
  font-size: 0.72rem;
  font-weight: 500;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.git-doc-ext {
  font-size: 0.6rem;
  font-weight: 700;
  color: #64748b;
  background: #f1f5f9;
  padding: 0.05rem 0.25rem;
  border-radius: 3px;
  flex-shrink: 0;
}

/* Fichiers supprimés */
.git-del-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.45rem;
  background: #fef2f2;
  border: 1px dashed #fecaca;
  border-radius: 6px;
  min-width: 0;
  flex: 1;
  opacity: 0.9;
  transition: all 0.15s ease;
}

.git-del-item:hover {
  background: #fee2e2;
  border-color: #f87171;
  opacity: 1;
}

.git-del-bullet {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #ef4444;
  flex-shrink: 0;
}

.git-del-icon {
  width: 12px;
  height: 12px;
  color: #dc2626;
  flex-shrink: 0;
}

.git-del-name {
  font-size: 0.72rem;
  font-weight: 500;
  color: #991b1b;
  text-decoration: line-through;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.git-del-drop {
  font-size: 0.62rem;
  font-weight: 700;
  font-family: ui-monospace, SFMono-Regular, monospace;
  color: #dc2626;
  background: #fee2e2;
  padding: 0.04rem 0.25rem;
  border-radius: 3px;
  flex-shrink: 0;
}

.is-deleted-stat {
  color: #dc2626;
}

/* Section git log */
.git-log-section {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.git-log-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.45rem 0.65rem;
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: ui-monospace, SFMono-Regular, monospace;
}

.git-log-btn:hover {
  background: #f8fafc;
}

.git-log-btn-left {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #334155;
}

.git-log-count {
  font-size: 0.65rem;
  background: #f1f5f9;
  color: #475569;
  padding: 0.05rem 0.35rem;
  border-radius: 999px;
}

.git-log-chevron {
  width: 13px;
  height: 13px;
  color: #94a3b8;
  transition: transform 0.2s ease;
}

.git-log-chevron.rotated {
  transform: rotate(90deg);
}

.git-log-body {
  padding: 0.5rem 0.65rem;
  border-top: 1px solid #f1f5f9;
}

.git-log-empty {
  font-size: 0.72rem;
  color: #94a3b8;
  text-align: center;
  padding: 0.5rem 0;
  font-family: ui-monospace, SFMono-Regular, monospace;
}

.git-log-list {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.git-log-entry {
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
}

.log-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.dot-add { background: #10b981; }
.dot-del { background: #ef4444; }
.dot-upd { background: #3b82f6; }
.dot-def { background: #94a3b8; }

.log-info {
  flex: 1;
  min-width: 0;
}

.log-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.3rem;
}

.log-action {
  font-size: 0.72rem;
  font-weight: 700;
  color: #1e293b;
  font-family: ui-monospace, SFMono-Regular, monospace;
}

.log-date {
  font-size: 0.65rem;
  color: #94a3b8;
}

.log-doc {
  font-size: 0.7rem;
  color: #475569;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 0.05rem;
}

.log-diff code {
  font-size: 0.65rem;
  color: #2563eb;
  background: #eff6ff;
  padding: 0.05rem 0.3rem;
  border-radius: 3px;
}

.size-3-5 {
  width: 0.875rem;
  height: 0.875rem;
}
</style>
