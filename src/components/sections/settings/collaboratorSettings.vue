<template>
    <div class="main-section gap-2">
        <headerNav title="Mes collaborateurs"/>

        <div v-if="authStore.collaborators.length > 0" class="content-container">

            <div class="cards-grid">
                <template v-for="(collaborator, index) in authStore.collaborators" :key="collaborator.id || index">
                    <CollaboratorCard
                        v-if="collaborator.status === 'accepted'"
                        :name="collaborator.username || collaborator.email"
                        :email="collaborator.email"
                    />
                    <PendingCollaboratorCard
                        v-else
                        :email="collaborator.email"
                        @resend="handleResend"
                    />
                </template>
            </div>
        </div>

        <div v-else class="h-full w-full flex justify-center items-center">
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
import PendingCollaboratorCard from '../../cards/PendingCollaboratorCard.vue';
import CollaboratorCard from '../../cards/CollaboratorCard.vue';
import inviteModale from '../../modale/inviteModale.vue';
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../../../stores/authStore';
import SuccesModale from '../../modale/succesModale.vue';

const authStore = useAuthStore();

const isOpen = ref<boolean>(false);
const isSuccess = ref<boolean>(false);

onMounted(async () => {
    await authStore.fetchCollaborators();
});

function handleResend(email: string) {
    // Add logic here to resend the invite if needed
    console.log("Resend invite to:", email);
}

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

<style scoped>
.main-section {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.content-container {
    padding: 2rem;
    flex: 1;
}

.actions-bar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 2rem;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #3b82f6; /* Bleu primaire */
  color: #ffffff;
  border: none;
  border-radius: 20px;
  padding: 0.6rem 1.2rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.add-btn:hover {
  background-color: #2563eb;
}

.add-btn:active {
  transform: scale(0.98);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}
</style>
