<template>
  <div class="main-section gap-2">
    <headerNav title="Mes clients" :showToolsButton="true" @handleEvent="isOpen = true" v-model="searchQuery" />

    <div v-if="clientStore.clients.length > 0" class="content-container">
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
        title="Mes clients"
        mainText="Vous n'avez aucun client."
        subtitle="Ajoutez votre premier client."
        btnLabel="Ajouter un client"
        @add="isOpen = true"
      />
    </div>

    <addClientModale :isOpen="isOpen" @close="isOpen = false" @created="onCreated" />
    <viewClientModale :isOpen="isViewOpen" :client="selectedClient" @close="isViewOpen = false" />

    <SuccesModale
      modaleTitle="Client ajouté"
      :isOpen="isSuccess"
      title="Client créé avec succès"
      subtitle="Le nouveau client a été ajouté à votre liste."
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
          <li @click.stop="editClient(activeClient)">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" /></svg>
             Modifier
          </li>
          <li @click.stop="shareClient(activeClient)">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0 0a2.25 2.25 0 1 0 3.935 2.186 2.25 2.25 0 0 0-3.935-2.186Zm0-12.814a2.25 2.25 0 1 0 3.933-2.185 2.25 2.25 0 0 0-3.933 2.185Z" /></svg>
             Partager
          </li>
          <li @click.stop="archiveClient(activeClient)">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z" /></svg>
             Archiver
          </li>
          <li class="danger" @click.stop="deleteClient(activeClient)">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" /></svg>
             Supprimer
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
import SuccesModale from '../../modale/succesModale.vue';
import { useClientStore } from '../../../stores/clientStore';

const clientStore = useClientStore();
const isOpen = ref(false);
const isViewOpen = ref(false);
const isSuccess = ref(false);
const searchQuery = ref('');
const activeMenu = ref<string | null>(null);
const activeClient = ref<any>(null);
const selectedClient = ref<any>(null);
const menuStyle = ref({ top: '0px', left: '0px' });

const statutLabels: Record<string, string> = {
  ACTIF: 'Actif',
  INACTIF: 'Inactif',
  PROSPECT: 'Prospect',
  ARCHIVE: 'Archivé',
};

const filteredClients = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return clientStore.clients;
  return clientStore.clients.filter(c =>
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

function editClient(client: any) {
  selectedClient.value = client;
  closeMenu();
  console.log("Modifier client", client.id);
  // TODO: Ouvrir la modale d'édition
}

function shareClient(client: any) {
  closeMenu();
  console.log("Partager client", client.id);
}

function archiveClient(client: any) {
  closeMenu();
  console.log("Archiver client", client.id);
}

async function deleteClient(client: any) {
  closeMenu();
  if (confirm(`Êtes-vous sûr de vouloir supprimer le client ${client.nom_complet} ?`)) {
    // await clientStore.deleteClient(client.id); // À implémenter dans le store
    console.log("Supprimer client", client.id);
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
  clientStore.fetchClients();
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
  color: #dc2626;
}
.dropdown-menu li.danger:hover {
  background-color: #fef2f2;
  color: #b91c1c;
}

.size-4 { width: 1rem; height: 1rem; }
.size-5 { width: 1.25rem; height: 1.25rem; }
</style>