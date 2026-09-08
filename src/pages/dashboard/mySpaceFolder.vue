<template>
  <div class="main-layout">
    <!-- Sidebar -->
    <sidebar />

    <!-- Contenu principal -->
    <main class="main-content">

        <navbar/>

        <myFolderFileSpace
            :files="files"
            @open="openFile"
            @rename="renameFile"
            @share="shareFile"
            @delete="deleteFile"
        />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { readDir, remove } from '@tauri-apps/plugin-fs';
import { openPath } from '@tauri-apps/plugin-opener';
import navbar from '../../components/navbar/navbar.vue';
import sidebar from '../../components/navbar/sidebar.vue';
import myFolderFileSpace from '../../components/sections/dashboard-section/myFolderFileSpace.vue';

const route = useRoute();
const files = ref<string[]>([]);

const currentFolderPath = computed(() => {
  const rawFolder = route.params.folderPath ?? route.params.folderName;

  if (Array.isArray(rawFolder)) {
    return rawFolder[0] ? decodeURIComponent(rawFolder[0]) : '';
  }

  return rawFolder ? decodeURIComponent(String(rawFolder)) : '';
});

const sortFiles = (entries: Array<{ name?: string; isFile?: boolean; path?: string }>) => {
  return entries
    .filter((entry) => entry.isFile)
    .map((entry) => {
      if (entry.path) return entry.path;
      if (entry.name && currentFolderPath.value) return `${currentFolderPath.value}/${entry.name}`;
      return '';
    })
    .filter(Boolean)
    .sort((a, b) => a.localeCompare(b));
};

const loadFolderFiles = async () => {
  const folderPath = currentFolderPath.value;

  if (!folderPath) {
    files.value = [];
    return;
  }

  try {
    const entries = await readDir(folderPath);
    files.value = sortFiles(entries);
  } catch (error) {
    console.error('Erreur lors du chargement des fichiers du dossier :', error);
    files.value = [];
  }
};

const openFile = async (filePath: string) => {
  try {
    await openPath(filePath);
  } catch (error) {
    console.error('Erreur ouverture fichier :', error);
  }
};

const renameFile = (filePath: string) => {
  console.log('Renommer le fichier :', filePath);
};

const shareFile = (filePath: string) => {
  console.log('Partager le fichier :', filePath);
};

const deleteFile = async (filePath: string) => {
  try {
    await remove(filePath);
    await loadFolderFiles();
  } catch (error) {
    console.error('Erreur suppression fichier :', error);
  }
};

watch(
  () => route.params.folderPath ?? route.params.folderName,
  () => {
    loadFolderFiles();
  },
  { immediate: true }
);

onMounted(() => {
  loadFolderFiles();
});
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
    justify-content: flex-start;
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
    overflow: hidden;
    overflow-x: hidden;
    background: #e9ebee;
    scrollbar-width: thin;
}

.dashboard-section {
  flex: 1;
}

@media (min-width: 1024px) {
  .main-layout {
    flex-direction: row;
  }
}
</style>
