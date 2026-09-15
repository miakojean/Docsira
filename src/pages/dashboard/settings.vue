<template>
    <div class="main-layout">
        <sidebar/>
        <sideTools />
        <main class="main-content">
            <sectionSettings @update="handleModal"/>
        </main>
        <succesModale 
            :isOpen="isModaleOpen" 
            @close="handleModal"
            modaleTitle="Informations mises à jour"
            title="Informations mises à jour"
            subtitle="Vos informations ont été mises à jour et sauvegardées. Cliquez sur le bouton pour continuer! "
        />
    </div>
</template>

<script setup lang="ts">
import sidebar from '../../components/navbar/sidebar.vue'
import sideTools from '../../components/navbar/sideTools.vue';
import sectionSettings from '../../components/sections/settings/sectionSettings.vue';
import succesModale from '../../components/modale/succesModale.vue';
import { ref } from 'vue';

const isModaleOpen = ref(false);

function handleModal(){
    isModaleOpen.value = !isModaleOpen.value;
}

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
    background: #fff;
    scrollbar-width: thin;
}

</style>
