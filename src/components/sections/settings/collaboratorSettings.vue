<template>
    <div class="main-section gap-2">
        <headerNav title="Mes collaborateurs" :showToolsButton="isOwner" @handleEvent="handleAdd" v-model="searchQuery"/>

        <div v-if="authStore.collaborators.length > 0" class="content-container">

            <div class="cards-grid" v-if="filteredCollaborators.length > 0">
                <template v-for="(collaborator, index) in filteredCollaborators" :key="collaborator.id || index">
                    <CollaboratorCard
                        v-if="collaborator.status === 'accepted'"
                        :name="collaborator.user.username || collaborator.user.email"
                        :email="collaborator.user.email"
                        :typeLabel="String(collaborator.id).startsWith('main_') ? 'Entreprise' : 'Collaborateur'"
                        :canDelete="isOwner"
                        @delete="handleDelete"
                    />
                    <PendingCollaboratorCard
                        v-else
                        :email="collaborator.user.email"
                        :isLoading="resendingEmail === collaborator.user.email"
                        :canDelete="isOwner"
                        @resend="handleResend"
                        @delete="handleDelete"
                    />
                </template>
            </div>
            
            <div v-else class="flex-1 w-full flex justify-center items-center">
                <emptyCards 
                    title="Aucun résultat"
                    :mainText="`Aucun collaborateur trouvé pour '${searchQuery}'`"
                    subtitle="Vérifiez l'orthographe ou essayez un autre terme."
                    :showAddButton="false"
                />
            </div>
        </div>

        <div v-else class="h-full w-full flex justify-center items-center">
            <emptyCards :showAddButton="isOwner" @add="handleAdd"/>
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
            :subtitle="successSubtitle"
            actionText="continuer"
            @close="() => { isSuccess = false }"
            @handleEvent="() => { isSuccess = false }"
        />

        <deleteModale
            :isOpen="isDeleteModalOpen"
            title="Retirer le collaborateur"
            :description="`Êtes-vous sûr de vouloir retirer le collaborateur <strong>${collaboratorToDelete}</strong> ?`"
            subtext="Attention, cette action supprimera tous ses accès à vos dossiers et fichiers partagés."
            @close="() => { isDeleteModalOpen = false }"
            @delete="confirmDeletion"
        />
    </div>
</template>

<script setup lang="ts">
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
import PendingCollaboratorCard from '../../cards/PendingCollaboratorCard.vue';
import CollaboratorCard from '../../cards/CollaboratorCard.vue';
import inviteModale from '../../modale/inviteModale.vue';
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../../../stores/authStore';
import SuccesModale from '../../modale/succesModale.vue';
import deleteModale from '../../modale/deleteModale.vue';

const authStore = useAuthStore();
const isOpen = ref(false);
const isSuccess = ref(false);
const successSubtitle = ref("Une invitation de collaboration a été envoyée dans le mail du collaborateur");
const resendingEmail = ref<string | null>(null);

const isDeleteModalOpen = ref(false);
const collaboratorToDelete = ref<string | null>(null);

const isOwner = computed(() => {
    return !authStore.collaborators.some(c => String(c.id).startsWith('main_'));
});

const searchQuery = ref("");

const filteredCollaborators = computed(() => {
    if (!searchQuery.value) return authStore.collaborators;
    
    const lowerQuery = searchQuery.value.toLowerCase();
    return authStore.collaborators.filter(c => {
        const username = c.user.username ? c.user.username.toLowerCase() : '';
        const email = c.user.email ? c.user.email.toLowerCase() : '';
        return username.includes(lowerQuery) || email.includes(lowerQuery);
    });
});

onMounted(async () => {
    await authStore.fetchCollaborators();
});

async function handleResend(email: string) {
    resendingEmail.value = email;
    try {
        const response = await authStore.addCollaborator(email);
        if (response) {
            successSubtitle.value = "L'invitation a été renvoyée avec succès.";
            isSuccess.value = true;
        }
    } finally {
        resendingEmail.value = null;
    }
}

function handleAdd() {
    if (!isOwner.value) return;
    isOpen.value = true;
}

async function handleDelete(email: string) {
    collaboratorToDelete.value = email;
    isDeleteModalOpen.value = true;
}

async function confirmDeletion() {
    if (collaboratorToDelete.value) {
        const success = await authStore.removeCollaborator(collaboratorToDelete.value);
        isDeleteModalOpen.value = false;
        
        if (success) {
            successSubtitle.value = "Le collaborateur a été retiré avec succès et n'a plus accès à vos données.";
            isSuccess.value = true;
        } else {
            alert(authStore.message.errorMessage || "Une erreur s'est produite lors de la suppression.");
        }
        collaboratorToDelete.value = null;
    }
}

async function handleInvite(email: string) {
    try{
        const response = await authStore.addCollaborator(email);
        if(response){
          successSubtitle.value = "Une invitation de collaboration a été envoyée dans le mail du collaborateur";
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
    display: flex;
    flex-direction: column;
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
