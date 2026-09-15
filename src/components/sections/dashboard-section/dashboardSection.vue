<template>
  <section class="main-section w-full flex flex-col justify-center items-center gap-4">

    <h3>Bienvenu {{ authStore.user?.username }}, très ravi de vous revoir.</h3>

    <BaseInput placeholder="Trouver votre dossier/client">
      <template #prepend>
        <div class="search-icon-wrapper">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
            />
          </svg>
        </div>
      </template>
    </BaseInput>

    <div class="actions">
      <features-card
        title="Workspace"
        content="Prenez part aux projets de l'équipe. Consultez la progression et les tâches en cours."
        @click="()=> {router.push('/dashboard/affairs')}"
      />
      <features-card
        title="Mon espace"
        content="Consultez votre espace personnel et accédez à vos documents."
        @click="()=> {router.push('/dashboard/mySpace')}"
      />
      <features-card
        title="Archives"
        content="Accéder à tous vos documents archivés en quelques clics"
        @click="()=>{router.push('/dashboard/archives')}"
      />
    </div>

  </section>
</template>

<script lang="ts">
import BaseInput from '../../BaseInput/BaseInput.vue'
import folderCards from '../../cards/folderCards.vue'
import featuresCard from '../../cards/featuresCards.vue'
import { Customer, useAuthStore } from '../../../stores/authStore'
import { load } from "@tauri-apps/plugin-store"

import { useRouter } from 'vue-router'
import { onMounted, ref } from 'vue'
export default {

  components:{
    BaseInput,
    folderCards,
    featuresCard
  },
  setup(){

    const router = useRouter();
    const authStore = useAuthStore();

    const user = ref<Customer>({
      id: undefined,
      email: "",
      first_name: "",
      last_name: "",
      username: "",
      password: "",
    })

    onMounted(async () => {
        // Si le profil n'est pas déjà en mémoire (ex: reload de page),
        // on le récupère via l'API grâce au token persisté.
        if (!authStore.user.username) {
          await authStore.fetchUserProfile();
        }
      });

    return{
      router,
      authStore,
    }

  }

}
</script>

<style scoped>

.main-section {
  flex: 1;
  min-height: 0;
  width: 100%;
  overflow-y: auto;
}

.search-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--primary-color );        /* fond gris clair */
  border-radius: 50%;         /* cercle */
  margin-left: 2px;           /* ajustement si besoin */
  transition: background 0.2s;
}

.search-icon-wrapper svg {
  width: 20px;
  height: 20px;
  color: #ffffff;             /* couleur de l'icône */
}

.actions{
  width: 100%;
  max-width: 900px;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

</style>
