<template>
    <div class="main-section gap-2 ">
        <headerNav title="Mes collaborateurs"/>
        <div class="h-full w-full flex justify-center items-center">
            <emptyCards @add="handleAdd"/>
        </div>

        <inviteModale
            :isOpen="isOpen"
            :backendError="authStore.message.errorMessage"
            :isLoading="authStore.isLoading"
            @close="()=> {isOpen = false}"
            @invite="(email:string) => { handleInvite(email)  }"
        />

        <SuccesModale
            modaleTitle="Confirmation effectuée"
            :isOpen="isSuccess"
            :title="authStore.message.succesMessage"
            subtitle="Une invitation de collaboration a été envoyée dans le mail du collaborateur"
            actionText="continuer"
            @close="() => { isSuccess = false }"

        />
    </div>
</template>

<script setup lang="ts">
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
import inviteModale from '../../modale/inviteModale.vue';
import { ref } from 'vue';
import { useAuthStore } from '../../../stores/authStore';
import SuccesModale from '../../modale/succesModale.vue';

const authStore = useAuthStore();

const isOpen = ref<boolean>(false);
const isSuccess = ref<boolean>(false);

function handleAdd() {
    isOpen.value = true;
}

async function handleInvite(email: string) {
    try{
        const response = await authStore.addCollaborator(email);
        if(response){
          isOpen.value = false;
          isSuccess.value = true;
        }
        else {
          isSuccess.value = false;
        }
    } catch (error: any) {
      isSuccess.value = false;
    }
}
</script>

<style scoped >

</style>
