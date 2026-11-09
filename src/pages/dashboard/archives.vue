<template>
  <div class="main-layout">
    <sidebar />
    <main class="main-content">
      <sectionArchives />
    </main>
  </div>
</template>

<script setup lang="ts">
import sidebar from '../../components/navbar/sidebar.vue';
import sectionArchives from '../../components/sections/archives/sectionArchives.vue';
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
  justify-content: flex-start;
  align-items: stretch;
  flex-direction: column;
  overflow: auto;
  background: #f4f6fa;
  scrollbar-width: thin;
}
</style>

