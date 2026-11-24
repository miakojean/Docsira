<template>
  <div class="main-layout">
    <!-- Barre latérale réduite comme dans le détail d'affaire -->
    <sidebar :defaultReduced="true" />

    <!-- Contenu principal -->
    <main class="main-content">
      <myFolderFileSpace :folderPath="currentFolderPath" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import sidebar from '../../components/navbar/sidebar.vue';
import myFolderFileSpace from '../../components/sections/dashboard-section/myFolderFileSpace.vue';

const route = useRoute();

const currentFolderPath = computed(() => {
  const rawFolder = route.params.folderPath ?? route.params.folderName;
  if (Array.isArray(rawFolder)) {
    return rawFolder[0] ? decodeURIComponent(rawFolder[0]) : '';
  }
  return rawFolder ? decodeURIComponent(String(rawFolder)) : '';
});
</script>

<style scoped>
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
