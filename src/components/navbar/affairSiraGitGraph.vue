<template>
  <div class="git-panel">
    <!-- Résumé sobre de l'avancement SIRA (sans pill ni badge) -->
    <div class="sira-summary-card">
      <div class="sira-summary-top">
        <span class="sira-summary-label">Progression SIRA</span>
        <span class="sira-summary-value">{{ currentProgression }}% · {{ currentMilestoneLabel }}</span>
      </div>
      <div class="sira-progress-track" aria-hidden="true">
        <div class="sira-progress-fill" :style="{ width: `${currentProgression}%` }"></div>
      </div>
    </div>

    <!-- Arbre de commit Git des jalons, lignées de documents et versions -->
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
          <div class="git-bullet-slot">
            <div class="git-bullet">
              <svg v-if="node.status === 'completed'" class="bullet-check" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 0 1 .143 1.052l-8 10.5a.75.75 0 0 1-1.127.075l-4.5-4.5a.75.75 0 0 1 1.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 0 1 1.05-.143Z" clip-rule="evenodd" />
              </svg>
              <span v-else-if="node.status === 'head'" class="bullet-pulse-core"></span>
            </div>
          </div>

          <div class="git-commit-meta">
            <div class="git-commit-title-row">
              <span class="git-hash">{{ node.threshold }}%</span>
              <span class="git-step-name">{{ node.label }}</span>
            </div>
          </div>
        </div>

        <!-- Sous-branches Git : Lignées actives et fichiers supprimés -->
        <div v-if="node.lineages.length > 0 || node.deletedDocuments.length > 0" class="git-sub-branch">
          <!-- Lignées de documents actives -->
          <div
            v-for="(lineage, linIdx) in node.lineages"
            :key="lineage.rootId"
            class="git-lineage-block"
          >
            <div class="git-doc-row">
              <div
                class="git-elbow"
                :class="{ 'is-last': linIdx === node.lineages.length - 1 && node.deletedDocuments.length === 0 }"
              ></div>

              <div class="git-doc-wrapper">
                <!-- Bouton dépliage des versions antérieures si v > 1 -->
                <button
                  v-if="lineage.versions.length > 1"
                  type="button"
                  class="lineage-expand-btn"
                  :title="isLineageExpanded(lineage.rootId) ? 'Masquer les versions précédentes' : `Afficher les ${lineage.versions.length} versions`"
                  @click.stop="toggleLineage(lineage.rootId)"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke-width="2.2"
                    stroke="currentColor"
                    class="expand-chevron"
                    :class="{ rotated: isLineageExpanded(lineage.rootId) }"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                  </svg>
                </button>

                <button
                  type="button"
                  class="git-doc-btn"
                  :title="`Voir les détails de ${lineage.latest.title} (v${lineage.latest.version || 1})`"
                  @click="emit('openDetails', lineage.latest)"
                >
                  <div class="git-doc-bullet"></div>
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="git-doc-icon" :class="extClass(lineage.latest.extension)">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                  </svg>
                  <span class="git-doc-name">{{ lineage.latest.title }}</span>
                  <span class="git-doc-ver">v{{ lineage.latest.version || 1 }}</span>
                </button>

                <button
                  type="button"
                  class="git-ver-trigger"
                  title="Gérer les versions"
                  aria-label="Gérer les versions"
                  @click.stop="emit('openVersions', lineage.latest)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="ver-trigger-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Liste des commits de versions antérieures (v2, v1...) -->
            <ul v-if="lineage.versions.length > 1 && isLineageExpanded(lineage.rootId)" class="git-versions-branch">
              <li
                v-for="ver in lineage.versions.slice(1)"
                :key="ver.id"
                class="git-version-node"
              >
                <button
                  type="button"
                  class="git-version-btn"
                  :title="ver.version_note ? `v${ver.version} : ${ver.version_note}` : `Voir les détails de la version v${ver.version || 1}`"
                  @click="emit('openDetails', ver)"
                >
                  <span class="ver-branch-dot"></span>
                  <span class="ver-tag">v{{ ver.version || 1 }}</span>
                  <span class="ver-meta">{{ ver.version_note || formatDate(ver.uploaded_at) }}</span>
                </button>
              </li>
            </ul>
          </div>

          <!-- Fichiers supprimés -->
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
              :title="`Supprimé${delDoc.author ? ` par ${delDoc.author}` : ''} le ${formatDate(delDoc.timestamp)}`"
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import type { Dossier } from '../../stores/dossierStore';
import { buildDocumentVersionLineages, type DossierDocument } from '../../stores/documentStore';
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
  (e: 'openDetails', doc: DossierDocument): void;
  (e: 'openVersions', doc: DossierDocument): void;
}>();

const siraStore = useSiraStore();
const expandedLineages = ref<Set<string>>(new Set());

const currentProgression = computed(() => {
  if (props.currentDossier?.statut === 'CLOTURE' || props.currentDossier?.statut === 'TERMINE') {
    return 100;
  }
  return props.currentDossier?.progression ?? 10;
});

const currentMilestoneLabel = computed(() => {
  const p = currentProgression.value;
  if (p >= 100) return 'Clôture';
  if (p >= 90) return 'Livrables';
  if (p >= 75) return 'Procédures';
  if (p >= 60) return 'Constitution';
  if (p >= 45) return 'Identification';
  return 'Initialisation';
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

const allLineages = computed(() => buildDocumentVersionLineages(props.documents));

function isLineageExpanded(rootId: string) {
  return expandedLineages.value.has(rootId);
}

function toggleLineage(rootId: string) {
  if (expandedLineages.value.has(rootId)) {
    expandedLineages.value.delete(rootId);
  } else {
    expandedLineages.value.add(rootId);
  }
}

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
    author?: string | null;
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
        author: h.author,
        timestamp: h.timestamp,
        previous_progression: h.previous_progression,
        new_progression: h.new_progression,
      });
    }
  }
  return list;
}

const gitNodes = computed(() => {
  const known = ['IDENTIFICATION', 'CONSTITUTION', 'PROCEDURES', 'LIVRABLES', 'CLOTURE'];
  const nodes = [
    {
      id: 'init',
      category: 'INIT',
      threshold: 10,
      label: 'Initialisation',
      lineages: allLineages.value.filter((l) => !l.latest.category || !known.includes(l.latest.category)),
      deletedDocuments: getDeletedDocsForCategory('INIT'),
    },
    {
      id: 'identification',
      category: 'IDENTIFICATION',
      threshold: 45,
      label: 'Identification',
      lineages: allLineages.value.filter((l) => l.latest.category === 'IDENTIFICATION'),
      deletedDocuments: getDeletedDocsForCategory('IDENTIFICATION'),
    },
    {
      id: 'constitution',
      category: 'CONSTITUTION',
      threshold: 60,
      label: 'Constitution',
      lineages: allLineages.value.filter((l) => l.latest.category === 'CONSTITUTION'),
      deletedDocuments: getDeletedDocsForCategory('CONSTITUTION'),
    },
    {
      id: 'procedures',
      category: 'PROCEDURES',
      threshold: 75,
      label: 'Procédures',
      lineages: allLineages.value.filter((l) => l.latest.category === 'PROCEDURES'),
      deletedDocuments: getDeletedDocsForCategory('PROCEDURES'),
    },
    {
      id: 'livrables',
      category: 'LIVRABLES',
      threshold: 90,
      label: 'Livrables',
      lineages: allLineages.value.filter((l) => l.latest.category === 'LIVRABLES'),
      deletedDocuments: getDeletedDocsForCategory('LIVRABLES'),
    },
    {
      id: 'cloture',
      category: 'CLOTURE',
      threshold: 100,
      label: 'Clôture',
      lineages: allLineages.value.filter((l) => l.latest.category === 'CLOTURE'),
      deletedDocuments: getDeletedDocsForCategory('CLOTURE'),
    },
  ];

  return nodes.map((n, idx) => {
    let status: 'completed' | 'head' | 'pending' = 'pending';
    if (idx < activeMilestoneIndex.value) {
      status = 'completed';
    } else if (idx === activeMilestoneIndex.value) {
      status = 'head';
    }
    return {
      ...n,
      status,
    };
  });
});

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

const documentsSignature = computed(() =>
  props.documents.map((d) => `${d.id}:${d.title}:${d.version}:${d.category}`).join('|')
);

watch(
  () => [props.currentId, documentsSignature.value],
  ([id]) => {
    if (id) {
      void siraStore.fetchHistory(String(id));
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.currentId) {
    void siraStore.fetchHistory(props.currentId);
  }
});
</script>

<style scoped>
.git-panel {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0.45rem 0.75rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  scrollbar-width: thin;
}

.sira-summary-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.6rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.sira-summary-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.sira-summary-label {
  font-weight: 600;
  color: #64748b;
}

.sira-summary-value {
  font-weight: 700;
  color: #0f172a;
}

.sira-progress-track {
  width: 100%;
  height: 3px;
  border-radius: 2px;
  background: #e2e8f0;
  overflow: hidden;
}

.sira-progress-fill {
  height: 100%;
  background: var(--primary-color, #005792);
  transition: width 0.25s ease;
}

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
  background: var(--primary-color, #005792);
}

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
}

.is-head .git-bullet {
  border-color: var(--primary-color, #005792);
  background: #ffffff;
}

.bullet-check {
  width: 10px;
  height: 10px;
}

.bullet-pulse-core {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--primary-color, #005792);
}

.git-commit-meta {
  flex: 1;
  min-width: 0;
}

.git-commit-title-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.git-hash {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748b;
}

.git-step-name {
  font-size: 0.84rem;
  font-weight: 700;
  color: #1e293b;
}

.is-head .git-step-name {
  color: var(--primary-color, #005792);
}

.is-pending .git-step-name {
  color: #64748b;
}

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

.git-lineage-block {
  display: flex;
  flex-direction: column;
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

.git-doc-wrapper {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  gap: 0.15rem;
}

.lineage-expand-btn {
  width: 18px;
  height: 22px;
  border: none;
  background: transparent;
  color: #64748b;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  flex-shrink: 0;
}

.lineage-expand-btn:hover {
  color: #0f172a;
}

.expand-chevron {
  width: 11px;
  height: 11px;
  transition: transform 0.15s ease;
}

.expand-chevron.rotated {
  transform: rotate(90deg);
}

.git-doc-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.35rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  min-width: 0;
  flex: 1;
}

.git-doc-btn:hover {
  background: #f1f5f9;
}

.git-doc-bullet {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #94a3b8;
  flex-shrink: 0;
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
  font-size: 0.74rem;
  font-weight: 500;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.git-doc-ver {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 0.68rem;
  font-weight: 600;
  color: #64748b;
  flex-shrink: 0;
}

.git-ver-trigger {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #94a3b8;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.git-ver-trigger:hover {
  background: #f1f5f9;
  color: var(--primary-color, #005792);
}

.ver-trigger-icon {
  width: 13px;
  height: 13px;
}

.git-versions-branch {
  list-style: none;
  margin: 0.15rem 0 0.25rem 0.9rem;
  padding: 0 0 0 0.6rem;
  border-left: 1px dashed #cbd5e1;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.git-version-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  border: none;
  background: transparent;
  padding: 0.15rem 0.3rem;
  border-radius: 5px;
  cursor: pointer;
  text-align: left;
  min-width: 0;
}

.git-version-btn:hover {
  background: #f8fafc;
}

.ver-branch-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #94a3b8;
  flex-shrink: 0;
}

.ver-tag {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 0.67rem;
  font-weight: 700;
  color: #475569;
  flex-shrink: 0;
}

.ver-meta {
  font-size: 0.68rem;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.git-del-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.4rem;
  min-width: 0;
  flex: 1;
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
  color: #991b1b;
  text-decoration: line-through;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.git-del-drop {
  font-size: 0.68rem;
  font-weight: 700;
  font-family: ui-monospace, SFMono-Regular, monospace;
  color: #dc2626;
  flex-shrink: 0;
}
</style>
