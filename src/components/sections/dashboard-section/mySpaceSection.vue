<template>
    <div class="workspace-container flex flex-col justify-center items-center gap-4 p-6">
        <!-- Bouton pour ajouter un dossier -->


        <div class="w-full flex flex-col items-center justify-center gap-2">

            <h3 class="mb-4 text-sm font-bold">Dossiers ouverts</h3>

            <div class="w-full flex justify-center items-center gap-4">
                <addItemButton @click="addFolder"/>
                <secondButton @click="() => { newDirModal = true }" label="Nouveau dossier"/>
            </div>
            <!-- Intégration du composant enfant -->
            <foldersList
                :folders="myOpenedFolders"
                @remove="removeFolder"
                @open="openFolder"
            />
        </div>

        <renameModale
            title="Nom du dossier"
            :isOpen="newDirModal"
            @rename="handleMakeDir"
            @close="() => { newDirModal = false }"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { open } from '@tauri-apps/plugin-dialog';
import { load } from '@tauri-apps/plugin-store';
import { mkdir, BaseDirectory } from '@tauri-apps/plugin-fs';
import { appDataDir, join } from '@tauri-apps/api/path';
import {useRouter} from 'vue-router';

import foldersList from '../../tools/foldersList.vue';
import addItemButton from '../../buttons/addItemButton.vue';
import secondButton from '../../buttons/secondButton.vue';
import renameModale from '../../modale/renameModale.vue';


const router = useRouter();

// 1. Déclarer la liste réactive qui stockera les chemins
const myOpenedFolders = ref<string[]>([]);

const saveOpenedFolders = async () => {
    const store = await load('myWorkspaceStore.json', {autoSave: false});
    await store.set('myOpenedFolders', myOpenedFolders.value);
    await store.save();
};

// 2. Fonction pour ajouter via Tauri
const addFolder = async () => {
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
                await saveOpenedFolders();
            }
        }
    } catch (error) {
        console.error("Erreur Tauri :", error);
    }
};

// 3. Retirer un dossier de la liste
const removeFolder = async (index: number) => {
    myOpenedFolders.value.splice(index, 1);
    await saveOpenedFolders();
};

// 4. Action quand on clique sur la carte du dossier
const openFolder = (fullPath: string) => {
    // On envoie le chemin complet encodé pour pouvoir le récupérer dans la page du dossier.
    router.push(`/dashboard/mySpace/${encodeURIComponent(fullPath)}`);
};

// 5. Créér un nouveau dossier
//
// Handle modale

const newDirModal = ref<boolean>(false);

const handleMakeDir = async (dirName: string) => {
    try {
        // 1. Créer le dossier physiquement sur le disque
        await mkdir(dirName, {
            baseDir: BaseDirectory.AppData,
            recursive: true
        });

        // 2. Reconstruire le chemin absolu, car mkdir() avec baseDir
        //    ne retourne rien : on doit le calculer nous-mêmes.
        const baseDir = await appDataDir();
        const fullPath = await join(baseDir, dirName);

        // 3. Ajouter à la liste réactive (en évitant les doublons)
        if (!myOpenedFolders.value.includes(fullPath)) {
            myOpenedFolders.value.push(fullPath);

            // 4. Sauvegarder dans le store, comme pour addFolder()
            await saveOpenedFolders();
        }

        console.log("Dossier créé avec succès");
    } catch (error: any) {
        console.error("Une erreur est survenue lors de la création :", error);
    }
}

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
