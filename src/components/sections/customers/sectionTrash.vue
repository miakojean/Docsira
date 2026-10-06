<template>
  <div class="main-section gap-2">
    <headerNav title="Corbeille" :showToolsButton="false" v-model="searchQuery">
    </headerNav>

    <div v-if="clientStore.trashClients.length > 0" class="content-container">
      <div v-if="filteredClients.length > 0" class="table-card">
        <table class="clients-table">
          <thead>
            <tr>
              <th>Référence</th>
              <th>Client</th>
              <th>Type</th>
              <th>Contact</th>
              <th>Localisation</th>
              <th>Statut</th>
              <th>Créé le</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="client in filteredClients" :key="client.id">
              <td class="ref">{{ client.reference_client }}</td>
              <td class="name">{{ client.nom_complet }}</td>
              <td>{{ client.type_client === 'PERSONNE_MORALE' ? 'Personne morale' : 'Personne physique' }}</td>
              <td>
                <div>{{ client.telephone_1 }}</div>
                <div class="muted">{{ client.email }}</div>
              </td>
              <td>{{ [client.ville, client.pays].filter(Boolean).join(', ') || '—' }}</td>
              <td><span class="badge" :class="client.statut.toLowerCase()">{{ statutLabels[client.statut] }}</span></td>
              <td class="muted">{{ formatDate(client.date_creation) }}</td>
              <td class="actions-cell">
                <button class="action-btn" @click.stop="toggleMenu(client, $event)">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
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
        title="Corbeille"
        mainText="La corbeille est vide."
        subtitle="Aucun client n'a été supprimé."
        :showAddButton="false"
      />
    </div>

    <addClientModale :isOpen="isOpen" @close="isOpen = false" @created="onCreated" />
    <viewClientModale :isOpen="isViewOpen" :client="selectedClient" @close="isViewOpen = false" />
    <editClientModale :isOpen="isEditOpen" :client="selectedClient" @close="isEditOpen = false" @updated="onUpdated" />
    <restoreModale
      :isOpen="isRestoreOpen"
      :isLoading="isRestoring"
      :isSuccess="isRestoreSuccess"
      :itemName="clientToRestore?.nom_complet || 'ce client'"
      title="Restaurer le client"
      description="Êtes-vous sûr de vouloir restaurer ce client ?"
      subtext="Il réapparaîtra dans votre liste des clients actifs."
      successTitle="Client restauré"
      successSubtitle="Le client a été restauré avec succès."
      @close="isRestoreOpen = false; isRestoreSuccess = false"
      @restore="confirmRestoreClient"
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

    <!-- Teleport de l'action menu pour éviter d'être coupé par la table -->
    <Teleport to="body">
      <div v-if="activeMenu" class="dropdown-menu" :style="menuStyle" @click.stop>
        <ul>
          <li @click.stop="viewClient(activeClient)">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
             Voir
          </li>
          <li class="danger" @click.stop="restoreClientAction(activeClient)">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" /></svg>
             Restaurer
          </li>
        </ul>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
import addClientModale from '../../modale/addClientModale.vue';
import viewClientModale from '../../modale/viewClientModale.vue';
import editClientModale from '../../modale/editClientModale.vue';
import restoreModale from '../../modale/restoreModale.vue';
import SuccesModale from '../../modale/succesModale.vue';
import { useClientStore } from '../../../stores/clientStore';

const clientStore = useClientStore();
const isOpen = ref(false);
const isViewOpen = ref(false);
const isEditOpen = ref(false);
const isRestoreOpen = ref(false);
const isRestoring = ref(false);
const isRestoreSuccess = ref(false);
const isSuccess = ref(false);
const successTitle = ref('');
const successSubtitle = ref('');
const searchQuery = ref('');
const activeMenu = ref<string | null>(null);
const activeClient = ref<any>(null);
const selectedClient = ref<any>(null);
const clientToRestore = ref<any>(null);
const menuStyle = ref({ top: '0px', left: '0px' });

const statutLabels: Record<string, string> = {
  ACTIF: 'Actif',
  INACTIF: 'Inactif',
  PROSPECT: 'Prospect',
  ARCHIVE: 'Archivé',
};

const filteredClients = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return clientStore.trashClients;
  return clientStore.trashClients.filter(c =>
    [c.nom_complet, c.reference_client, c.email, c.telephone_1, c.ville]
      .some(v => (v || '').toLowerCase().includes(q))
  );
});

function formatDate(value: string) {
  if (!value) return '—';
  return new Date(value).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
}

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

function toggleMenu(client: any, event: MouseEvent) {
  if (activeMenu.value === client.id) {
    activeMenu.value = null;
    activeClient.value = null;
  } else {
    activeMenu.value = client.id;
    activeClient.value = client;
    
    // Calculate the position of the button
    const button = event.currentTarget as HTMLElement;
    const rect = button.getBoundingClientRect();
    
    // Position the menu to the left of the button, centered vertically with the button
    menuStyle.value = {
      top: `${rect.top + window.scrollY + rect.height / 2}px`,
      left: `${rect.left + window.scrollX - 170 - 8}px`, // 170px width + 8px gap
    };
  }
}

function closeMenu() {
  activeMenu.value = null;
  activeClient.value = null;
}

function viewClient(client: any) {
  selectedClient.value = client;
  isViewOpen.value = true;
  closeMenu();
}

function restoreClientAction(client: any) {
  closeMenu();
  clientToRestore.value = client;
  isRestoreOpen.value = true;
}

async function confirmRestoreClient() {
  if (clientToRestore.value) {
    isRestoring.value = true;
    const ok = await clientStore.restoreClient(clientToRestore.value.id);
    await new Promise(resolve => setTimeout(resolve, 1000));
    isRestoring.value = false;
    if (ok) {
      isRestoreSuccess.value = true;
    }
  }
}

function handleClickOutside(event: MouseEvent) {
  // Close the menu if the click is outside the dropdown
  const target = event.target as HTMLElement;
  if (!target.closest('.dropdown-menu') && !target.closest('.action-btn')) {
    closeMenu();
  }
}

onMounted(() => {
  clientStore.fetchTrashClients();
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.main-section { display: flex; flex-direction: column; height: 100%; }
.content-container { padding: 2rem; flex: 1; display: flex; flex-direction: column; }

.table-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  overflow-x: auto;
}

.clients-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; color: #374151; }
.clients-table th {
  text-align: left;
  padding: 0.9rem 1rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #9ca3af;
  border-bottom: 1px solid #f3f4f6;
  white-space: nowrap;
}
.clients-table td { padding: 0.9rem 1rem; border-bottom: 1px solid #f9fafb; vertical-align: middle; }
.clients-table tbody tr { transition: background 0.15s ease; }
.clients-table tbody tr:hover { background: #f9fafb; }
.center { text-align: center !important; }
.ref { font-family: monospace; color: #6b7280; }
.name { font-weight: 600; color: #111827; }
.muted { color: #9ca3af; font-size: 0.8rem; }

.badge { padding: 0.2rem 0.65rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.badge.actif { background: #dcfce7; color: #166534; }
.badge.inactif { background: #f3f4f6; color: #4b5563; }
.badge.prospect { background: #dbeafe; color: #1e40af; }
.badge.archive { background: #fef3c7; color: #92400e; }

/* --- Actions Menu --- */
.text-right { text-align: right !important; }
.actions-cell {
  position: relative;
  text-align: right;
  vertical-align: middle;
}

.action-btn {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.dropdown-menu {
  position: absolute; /* becomes relative to body thanks to Teleport */
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  border: 1px solid #f3f4f6;
  min-width: 170px;
  z-index: 9999;
  padding: 0.5rem;
  text-align: left;
  transform: translateY(-50%);
}

.dropdown-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.dropdown-menu li {
  padding: 0.7rem;
  font-size: 0.875rem;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dropdown-menu li:hover {
  background-color: #f3f4f6;
  color: #2563eb;
}

.dropdown-menu li.danger {
  color: #325aaf;
}

.size-4 { width: 1rem; height: 1rem; }
.size-5 { width: 1.25rem; height: 1.25rem; }
</style>