<template>
  <div class="main-section gap-2">
    <headerNav title="Mes clients" :showToolsButton="true" @handleEvent="isOpen = true" v-model="searchQuery">
    </headerNav>

    <div v-if="clientStore.clients.length > 0" class="content-container">
      <div v-if="filteredClients.length > 0" class="clients-grid">
        <customerCard
          v-for="client in filteredClients"
          :key="client.id"
          :client="client"
          @view="viewClient"
          @edit="editClient"
          @share="shareClient"
          @archive="archiveClient"
          @delete="deleteClient"
        />
      </div>

      <div v-else class="flex-1 w-full flex justify-center items-center">
        <emptyCards
          title="Mes clients"
          :mainText="`Aucun client trouvé pour '${searchQuery}'`"
          subtitle="Vérifiez l'orthographe ou essayez un autre terme."
          :showAddButton="false"
        />
      </div>
    </div>

    <div v-else-if="!clientStore.isLoading" class="h-full w-full flex justify-center items-center">
      <emptyCards
        title="Mes clients"
        mainText="Vous n'avez aucun client."
        subtitle="Ajoutez votre premier client."
        btnLabel="Ajouter un client"
        @add="isOpen = true"
      />
    </div>

    <addClientModale :isOpen="isOpen" @close="isOpen = false" @created="onCreated" />
    <viewClientModale :isOpen="isViewOpen" :client="selectedClient" @close="isViewOpen = false" />
    <editClientModale :isOpen="isEditOpen" :client="selectedClient" @close="isEditOpen = false" @updated="onUpdated" />
    <deleteModale
      :isOpen="isDeleteOpen"
      :isLoading="isDeleting"
      :isSuccess="isDeleteSuccess"
      :itemName="clientToDelete?.nom_complet || 'ce client'"
      title="Supprimer le client"
      description="Êtes-vous sûr de vouloir envoyer ce client à la corbeille ?"
      subtext="Vous pourrez le restaurer depuis la corbeille."
      successTitle="Client déplacé vers la corbeille"
      successSubtitle="Le client a été envoyé à la corbeille."
      @close="isDeleteOpen = false; isDeleteSuccess = false"
      @delete="confirmDeleteClient"
    />

    <SuccesModale
      modaleTitle="Succès"
      :isOpen="isSuccess"
      :title="successTitle"
      :subtitle="successSubtitle"
      actionText="continuer"
      @close="isSuccess = false"
      @handleEvent="isSuccess = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
import customerCard from '../../cards/customerCard.vue';
import addClientModale from '../../modale/addClientModale.vue';
import viewClientModale from '../../modale/viewClientModale.vue';
import editClientModale from '../../modale/editClientModale.vue';
import deleteModale from '../../modale/deleteModale.vue';
import SuccesModale from '../../modale/succesModale.vue';
import { useClientStore } from '../../../stores/clientStore';

const clientStore = useClientStore();
const isOpen = ref(false);
const isViewOpen = ref(false);
const isEditOpen = ref(false);
const isDeleteOpen = ref(false);
const isDeleting = ref(false);
const isDeleteSuccess = ref(false);
const isSuccess = ref(false);
const successTitle = ref('');
const successSubtitle = ref('');
const searchQuery = ref('');
const selectedClient = ref<any>(null);
const clientToDelete = ref<any>(null);

const filteredClients = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return clientStore.clients;
  return clientStore.clients.filter(c =>
    [c.nom_complet, c.reference_client, c.email, c.telephone_1, c.ville]
      .some(v => (v || '').toLowerCase().includes(q))
  );
});

function onCreated() {
  isOpen.value = false;
  successTitle.value = "Client créé avec succès";
  successSubtitle.value = "Le nouveau client a été ajouté à votre liste.";
  isSuccess.value = true;
}

function onUpdated() {
  isEditOpen.value = false;
  successTitle.value = "Client mis à jour";
  successSubtitle.value = "Les informations du client ont été modifiées avec succès.";
  isSuccess.value = true;
}

function viewClient(client: any) {
  selectedClient.value = client;
  isViewOpen.value = true;
}

function editClient(client: any) {
  selectedClient.value = client;
  isEditOpen.value = true;
}

function shareClient(client: any) {
  console.log("Partager client", client.id);
}

function archiveClient(client: any) {
  console.log("Archiver client", client.id);
}

function deleteClient(client: any) {
  clientToDelete.value = client;
  isDeleteOpen.value = true;
}

async function confirmDeleteClient() {
  if (clientToDelete.value) {
    isDeleting.value = true;
    const ok = await clientStore.deleteClient(clientToDelete.value.id);
    await new Promise(resolve => setTimeout(resolve, 1000));
    isDeleting.value = false;
    if (ok) {
      isDeleteSuccess.value = true;
    }
  }
}

onMounted(() => {
  clientStore.fetchClients();
});
</script>

<style scoped>
.main-section { display: flex; flex-direction: column; height: 100%; }
.content-container { padding: 0.5rem; flex: 1; display: flex; flex-direction: column; }

.clients-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.5rem;
  width: 100%;
}

@media (min-width: 1200px) {
  .clients-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

.size-4 { width: 1rem; height: 1rem; }
.size-5 { width: 1.25rem; height: 1.25rem; }
</style>