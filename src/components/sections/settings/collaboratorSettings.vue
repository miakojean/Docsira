<template>
    <div class="main-section gap-2">
        <headerNav title="Mes collaborateurs"/>
        
        <div v-if="pendingInvites.length > 0" class="content-container">
            <div class="actions-bar">
                <button class="add-btn" @click="handleAdd">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="btn-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM4 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 0110.374 21c-2.331 0-4.512-.645-6.374-1.766z" />
                    </svg>
                    Inviter un autre collaborateur
                </button>
            </div>
            
            <div class="cards-grid">
                <PendingCollaboratorCard 
                    v-for="(email, index) in pendingInvites" 
                    :key="index" 
                    :email="email"
                    @resend="handleResend" 
                />
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
