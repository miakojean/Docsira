<template>
  <section class="main-section w-full">

    <div 
        class="empty-state w-full h-full flex flex-col justify-center items-center gap-4"
        v-if="!myFolders"
    >

        <div class="empty-folder flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
            </svg>
        </div>

        <h3 class="w-full">Aucun dossier dans votre workspace</h3>

        <p class="font-medium">Cliquez sur les boutons pour ajouter et gérer les dossiers de travail</p>

        <div class="actions-btn flex justify-center items-center gap-4 w-full">
          <secondButton label="Ouvrir le dossier" />
          <mainButton label="Ajouter un dossier" @click="file"/>
        </div>

    </div>

    <foldersList :folders="myFolders"/>

  </section>
</template>

<script lang="ts">
import { open } from '@tauri-apps/plugin-dialog';
import { load } from '@tauri-apps/plugin-store';
import { myFolders } from '../../../stores/localManagerStore';
import mainButton from '../../buttons/mainButton.vue';
import secondButton from '../../buttons/secondButton.vue';
import folderCards from '../../cards/folderCards.vue';
import foldersList from '../../tools/foldersList.vue';

import { useRouter } from 'vue-router';

export default {
    components: {
        mainButton,
        secondButton,
        folderCards,
        foldersList
    },
    setup() {
        const router = useRouter();

        const file = async () => {
            // Ouvre l'explorateur de fichiers natif
            const selectedPath = await open({
                directory: true, // Force la sélection d'un dossier et non d'un fichier
                multiple: false, // Empêche la sélection multiple
                title: 'Ajouter un dossier à my workspace'
            });
            // Ajouter le dossier sélectionné à la liste des dossiers
            if (selectedPath) {

                if (!myFolders.value.includes(selectedPath)){
                    myFolders.value.push(selectedPath);

                    // Persistance dans le store tauri
                    const store = await load('store.json');
                    await store.set("myWorkSpaceFolder", myFolders.value)
                    await store.save();
                }

                console.log('Chemin du dossier sélectionné :', selectedPath);

            } else {
                console.log('Sélection annulée par l’utilisateur');
            }
        };

        return {
            router,
            file
        };
    }
}
</script>

<style scoped>

/* empty state */
.empty-folder{
    position: relative;
    background: #f3f3f3;
    border-radius: 1rem;
    padding: 2rem 1rem;
    height: 120px;
    width: 120px;
}

.empty-folder svg{
    color: var(--primary-black-color);
}

.empty-state p{
    color: #6d6d6d
}

.actions-btn {
    max-width: 500px;
}

</style>
