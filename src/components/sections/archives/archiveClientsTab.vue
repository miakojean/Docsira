<template>
  <div class="archive-tab-content">
    <div v-if="clientStore.isLoading && clientStore.clients.length === 0" class="loader-area">
      <LogoLoader size="lg" label="Chargement des clients..." />
    </div>

    <div v-else-if="clientStore.clients.length > 0" class="content-container">
      <div v-if="filteredClients.length > 0" class="flex flex-col gap-4">
        <div class="clients-grid">
          <customerCard
            v-for="client in paginatedClients"
            :key="client.id"
            :client="client"
            @view="viewClient"
            @edit="editClient"
            @folders="openClientFolders"
            @delete="openClientDelete"
          />
        </div>

        <Pagination
          v-model="currentPage"
          :totalItems="filteredClients.length"
          :pageSize="pageSize"
          :hideOnSinglePage="false"
        />
      </div>

      <div v-else class="empty-area">
        <emptyCards
          title="Clients archivés"
          :mainText="`Aucun client trouvé pour '${searchQuery}'`"
          subtitle="Vérifiez l'orthographe ou essayez un autre terme."
          :showAddButton="false"
        />
      </div>
    </div>

    <div v-else class="empty-area">
      <emptyCards
        title="Clients archivés"
        mainText="Aucun client disponible."
        subtitle="Vos fiches clients apparaîtront ici."
        :showAddButton="false"
      />
    </div>

    <!-- Modales Clients -->
    <viewClientModale
      :isOpen="isClientViewOpen"
      :client="selectedClient"
      @close="isClientViewOpen = false"
    />

    <clientDossiersModale
      :isOpen="isClientFoldersOpen"
      :client="selectedClient"
      @close="isClientFoldersOpen = false"
    />

    <editClientModale
      :isOpen="isClientEditOpen"
      :client="selectedClient"
      @close="isClientEditOpen = false"
      @updated="onClientUpdated"
    />

    <deleteModale
      :isOpen="isClientDeleteOpen"
      :isLoading="isDeletingClient"
      :isSuccess="isDeleteClientSuccess"
      :itemName="clientToDelete?.nom_complet || 'ce client'"
      title="Supprimer le client"
      description="Êtes-vous sûr de vouloir envoyer ce client à la corbeille ?"
      subtext="Vous pourrez le restaurer depuis la corbeille."
      successTitle="Client déplacé vers la corbeille"
      successSubtitle="Le client a été envoyé à la corbeille."
      @close="isClientDeleteOpen = false; isDeleteClientSuccess = false"
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
import { ref, computed, watch } from 'vue';
import customerCard from '../../cards/customerCard.vue';
import emptyCards from '../../cards/emptyCards.vue';
import LogoLoader from '../../tools/LogoLoader.vue';
import Pagination from '../../tools/Pagination.vue';
import viewClientModale from '../../modale/viewClientModale.vue';
import clientDossiersModale from '../../modale/clientDossiersModale.vue';
import editClientModale from '../../modale/editClientModale.vue';
import deleteModale from '../../modale/deleteModale.vue';
import SuccesModale from '../../modale/succesModale.vue';
import { useClientStore } from '../../../stores/clientStore';

const props = withDefaults(
  defineProps<{
    searchQuery?: string;
  }>(),
  {
    searchQuery: '',
  }
);

const clientStore = useClientStore();

const pageSize = 12;
const currentPage = ref(1);

watch(() => props.searchQuery, () => {
  currentPage.value = 1;
});

const filteredClients = computed(() => {
  const q = props.searchQuery.trim().toLowerCase();
  if (!q) return clientStore.clients;
  return clientStore.clients.filter((c) =>
    [c.nom_complet, c.reference_client, c.email, c.telephone_1, c.ville].some((v) =>
      (v || '').toLowerCase().includes(q)
    )
  );
});

const paginatedClients = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return filteredClients.value.slice(start, start + pageSize);
});

// Modales state
const isClientViewOpen = ref(false);
const isClientFoldersOpen = ref(false);
const isClientEditOpen = ref(false);
const isClientDeleteOpen = ref(false);
const isDeletingClient = ref(false);
const isDeleteClientSuccess = ref(false);
const selectedClient = ref<any>(null);
const clientToDelete = ref<any>(null);

const isSuccess = ref(false);
const successTitle = ref('');
const successSubtitle = ref('');

function viewClient(client: any) {
  selectedClient.value = client;
  isClientViewOpen.value = true;
}

function openClientFolders(client: any) {
  selectedClient.value = client;
  isClientFoldersOpen.value = true;
}

function editClient(client: any) {
  selectedClient.value = client;
  isClientEditOpen.value = true;
}

function onClientUpdated() {
  isClientEditOpen.value = false;
  successTitle.value = 'Client mis à jour';
  successSubtitle.value = 'Les informations du client ont été modifiées avec succès.';
  isSuccess.value = true;
}

function openClientDelete(client: any) {
  clientToDelete.value = client;
  isDeleteClientSuccess.value = false;
  isClientDeleteOpen.value = true;
}

async function confirmDeleteClient() {
  if (!clientToDelete.value) return;
  isDeletingClient.value = true;
  const ok = await clientStore.deleteClient(clientToDelete.value.id);
  isDeletingClient.value = false;
  if (ok) {
    isDeleteClientSuccess.value = true;
  }
}
</script>

<style scoped>
.archive-tab-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.content-container {
  padding: 0.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.loader-area,
.empty-area {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clients-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
  width: 100%;
  padding-bottom: 1rem;
}
</style>

