<template>
    <div class="main-layout">
        <sidebar/>
        <sideTools />
        <main class="main-content">
            <sectionSettings />
        </main>
    </div>
</template>

<script setup lang="ts">
import sidebar from '../../components/navbar/sidebar.vue'
import sideTools from '../../components/navbar/sideTools.vue';
import sectionSettings from '../../components/sections/settings/sectionSettings.vue';

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
    gap: 1rem;
    overflow: hidden;
    overflow-x: hidden;
    background: #e9ebee;
    scrollbar-width: thin;
}

</style>
