<template>
    <div class="main-layout">
        <sidebar/>
        <sideTools />
        <main class="main-content">
            <sectionCollaborators />
        </main>
    </div>
</template>

<script setup lang="ts">
import sidebar from '../../components/navbar/sidebar.vue'
import sideTools from '../../components/navbar/sideTools.vue';
import sectionCollaborators from '../../components/sections/settings/sectionCollaborators.vue';
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
    background: #fafbfc;
    scrollbar-width: thin;
}
</style>
