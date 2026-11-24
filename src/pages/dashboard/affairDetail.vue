<template>
  <div class="main-layout">
    <!-- Barre latérale -->
    <sidebar :defaultReduced="true" />

    <!-- Arborescence des dossiers et documents + Suivi SIRA -->
    <affairTree
      :currentId="affairId"
      :currentDossier="dossier"
      :documents="documents"
      :subfolders="subfolders"
      :currentFolderId="currentFolderId"
      :activeTab="activeTreeTab"
      @update:activeTab="activeTreeTab = $event"
      @openDocument="openDocument"
      @selectFolder="currentFolderId = $event"
    />

    <!-- Contenu principal -->
    <main class="main-content">
      <affairDetailSection :affair="affair" @showSira="activeTreeTab = 'sira'" />
    </main>

    <!-- Panneau latéral droit : commentaires collaborateurs -->
    <affairCommentsDrawer
      :isOpen="isCommentsOpen"
      :affairId="affairId"
      :documents="documents"
      :initialDocumentId="commentInitialDocId"
      :focusKey="commentFocusKey"
      @toggle="toggleComments"
      @share="openShareDossierModal"
      @openDocument="openDocumentById"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import sidebar from '../../components/navbar/sidebar.vue';
import affairTree from '../../components/navbar/affairTree.vue';
import affairDetailSection from '../../components/sections/workspace/affairDetailSection.vue';
import affairCommentsDrawer from '../../components/sections/workspace/affairCommentsDrawer.vue';
import { useAffairDocuments } from '../../composables/useAffairDocuments';

const affair = useAffairDocuments();
const {
  affairId,
  documents,
  subfolders,
  currentFolderId,
  openDocument,
  dossier,
  isCommentsOpen,
  commentInitialDocId,
  commentFocusKey,
  toggleComments,
  openShareDossierModal,
  openDocumentById,
} = affair;

const activeTreeTab = ref<'folders' | 'sira'>('folders');
</script>

<style scoped>
/* === LAYOUT PRINCIPAL === */
.main-layout {
  display: flex;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: #f9fafb;
}

.main-content {
  flex: 1;
  width: 100%;
  min-width: 0;
  min-height: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f1f3f5;
}
</style>
