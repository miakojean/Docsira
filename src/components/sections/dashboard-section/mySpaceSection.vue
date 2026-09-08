<template>
    <div class="workspace-container flex flex-col justify-center items-center gap-4 p-6">
        <!-- Bouton pour ajouter un dossier -->
        <mainButton label="Nouveau dossier à myWorkspace" @click="addFolder" />

        <div class="mt-8">
            <h3 class="mb-4 text-lg font-bold">Dossiers ouverts</h3>
            
            <!-- Intégration du composant enfant -->
            <foldersList 
                :folders="myOpenedFolders" 
                @remove="removeFolder"
                @open="openFolder"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { open } from '@tauri-apps/plugin-dialog';
import { load } from '@tauri-apps/plugin-store';
import {useRouter} from 'vue-router';

import foldersList from '../../tools/foldersList.vue'; 
import mainButton from '../../buttons/mainButton.vue';

const router = useRouter();

// 1. Déclarer la liste réactive qui stockera les chemins
const myOpenedFolders = ref<string[]>([]);

// 2. Fonction pour ajouter via Tauri
const addFolder = async () => {

    const store = await load('myWorkspaceStore.json', {autoSave: false});

    try {
        const selectedPath = await open({
            directory: true, 
            multiple: false,
            title: 'Sélectionner un dossier'
        });

        if (selectedPath) {
            // Empêcher les doublons
            if (!myOpenedFolders.value.includes(selectedPath)) {
                myOpenedFolders.value.push(selectedPath);
                
                // Enregistrer dans le store
                await store.set('myOpenedFolders', myOpenedFolders.value);
                await store.save();
            }
        }
    } catch (error) {
        console.error("Erreur Tauri :", error);
    }
};

// 3. Retirer un dossier de la liste
const removeFolder = (index: number) => {
    myOpenedFolders.value.splice(index, 1);
};

// 4. Action quand on clique sur la carte du dossier
const openFolder = (fullPath: string) => {
    // On envoie le chemin complet encodé pour pouvoir le récupérer dans la page du dossier.
    router.push(`/dashboard/mySpace/${encodeURIComponent(fullPath)}`);
};

onMounted(async () => {
    const store = await load('myWorkspaceStore.json', {autoSave: false});
    const storedFolders = await store.get('myOpenedFolders') as string[] | undefined;

    if (storedFolders && Array.isArray(storedFolders)) {
        myOpenedFolders.value = storedFolders;
    }
})
</script>

<style scoped>
/* J'ai retiré tout le CSS lié au .empty-state car il est maintenant géré par l'enfant ! */
.workspace-container {
    flex: 1;
    width: 100%;
    padding: 1rem;
    min-height: 0;
    overflow-y: auto;
    align-items: stretch;
}
</style>