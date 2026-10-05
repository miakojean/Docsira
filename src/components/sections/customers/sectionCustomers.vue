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
              <th>Ville</th>
              <th>Statut</th>
              <th class="center">Dossiers</th>
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
              <td>{{ client.ville || '—' }}</td>
              <td><span class="badge" :class="client.statut.toLowerCase()">{{ statutLabels[client.statut] }}</span></td>
              <td class="center">{{ client.nombre_dossiers }}</td>
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

    <SuccesModale
      modaleTitle="Client ajouté"
      :isOpen="isSuccess"
      title="Client créé avec succès"
      subtitle="Le nouveau client a été ajouté à votre liste."
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
import addClientModale from '../../modale/addClientModale.vue';
import SuccesModale from '../../modale/succesModale.vue';
import { useClientStore } from '../../../stores/clientStore';

const clientStore = useClientStore();
const isOpen = ref(false);
const isSuccess = ref(false);
const searchQuery = ref('');

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

function onCreated() {
  isOpen.value = false;
  isSuccess.value = true;
}

onMounted(() => clientStore.fetchClients());
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
</style>
