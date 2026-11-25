<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="300">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <form class="modal-card" role="dialog" aria-modal="true" @submit.prevent="submit">
          <div class="modal-header">
            <h3 class="modal-title">Nouveau dossier</h3>
            <button type="button" class="close-btn" @click="$emit('close')" aria-label="Fermer la modale">&times;</button>
          </div>

          <div class="border-wrapper">
            <!-- Informations du client -->
            <div class="field w-full flex flex-col gap-2">
              <label class="field-label">
                Client rattaché
                <span class="required-mark">*</span>
              </label>

              <!-- Si un client est sélectionné -->
              <div v-if="selectedClient" class="selected-client">
                <div class="info">
                  <span class="name">{{ selectedClient.nom_complet }}</span>
                  <span class="meta">
                    {{ selectedClient.reference_client }}
                    <template v-if="selectedClient.email"> · {{ selectedClient.email }}</template>
                    <template v-if="selectedClient.telephone_1"> · {{ selectedClient.telephone_1 }}</template>
                  </span>
                </div>
                <button type="button" class="change-btn" @click="selectedClient = null; search = ''">
                  Changer
                </button>
              </div>

              <!-- Sinon recherche ou création de client -->
              <div v-else class="client-selection-box">
                <div class="search-actions-row">
                  <BaseInput
                    v-model="search"
                    placeholder="Trouver un client (nom, email, tél...)"
                    autocomplete="off"
                  />
                  <addItemButton
                    btnLabel="+ Nouveau client"
                    @add="isAddClientOpen = true"
                  />
                </div>

                <!-- Résultats de la recherche -->
                <ul v-if="matchingClients.length" class="results">
                  <li v-for="c in matchingClients" :key="c.id" @click="selectClient(c)">
                    <span class="name">{{ c.nom_complet }}</span>
                    <span class="meta">
                      {{ c.reference_client }}
                      <template v-if="c.email"> · {{ c.email }}</template>
                      <template v-if="c.telephone_1"> · {{ c.telephone_1 }}</template>
                    </span>
                  </li>
                </ul>
                <p v-else-if="search.trim()" class="hint">Aucun client trouvé pour cette recherche.</p>
                <p v-else class="hint">Commencez à taper pour rechercher un client ou créez-en un nouveau.</p>

                <p v-if="dossierStore.fieldErrors.client_id" class="error-text">
                  {{ dossierStore.fieldErrors.client_id }}
                </p>
              </div>
            </div>

            <!-- Nom du dossier & Type de dossier -->
            <div class="fields-row">
              <BaseInput
                label="Nom du dossier"
                v-model="title"
                required
                placeholder="Ex : Constitution de la société SARL"
                :errorMessage="dossierStore.fieldErrors.title"
              />
              <BaseSelectInput
                label="Type de dossier"
                placeholder="Sélectionner le type de dossier"
                v-model="typeAffair"
                required
                :groups="DOSSIER_TYPE_GROUPS"
                :errorMessage="dossierStore.fieldErrors.type_affair"
              />
            </div>

            <!-- Message d'erreur global -->
            <p v-if="dossierStore.errorMessage" class="error-text">{{ dossierStore.errorMessage }}</p>

            <div class="modal-footer">
              <button type="button" class="btn" @click="$emit('close')">Annuler</button>
              <button type="submit" class="btn btn-primary" :disabled="!canSubmit">
                {{ dossierStore.isLoading ? 'Création...' : 'Créer le dossier' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </Transition>

    <!-- Modale imbriquée pour création d'un nouveau client -->
    <addClientModale
      :isOpen="isAddClientOpen"
      :zIndex="11000"
      @close="isAddClientOpen = false"
      @created="onClientCreated"
    />
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import { useClientDossierStore } from '../../stores/dossierStore';
import { useClientStore, type ClientListItem } from '../../stores/clientStore';
import { DOSSIER_TYPE_GROUPS } from '../../helpers/dossierTypes';
import addItemButton from '../buttons/addItemButton.vue';
import BaseInput from '../BaseInput/BaseInput.vue';
import BaseSelectInput from '../BaseInput/BaseSelectInput.vue';
import addClientModale from './addClientModale.vue';

const props = withDefaults(
  defineProps<{
    isOpen: boolean;
    defaultClient?: ClientListItem | null;
  }>(),
  {
    defaultClient: null,
  }
);
const emit = defineEmits(['close', 'created']);

const dossierStore = useClientDossierStore();
const clientStore = useClientStore();

const title = ref('');
const typeAffair = ref('CONSTITUTION');
const search = ref('');
const selectedClient = ref<ClientListItem | null>(null);
const isAddClientOpen = ref(false);

const matchingClients = computed(() => {
  const q = search.value.trim().toLowerCase();
  return clientStore.clients
    .filter(c => !q || [c.nom_complet, c.reference_client, c.email, c.telephone_1]
      .some(v => (v || '').toLowerCase().includes(q)))
    .slice(0, 6);
});

const canSubmit = computed(() =>
  !!selectedClient.value && title.value.trim().length > 0 && !!typeAffair.value && !dossierStore.isLoading
);

function selectClient(client: ClientListItem) {
  selectedClient.value = client;
  search.value = '';
}

function onClientCreated() {
  isAddClientOpen.value = false;
  // Sélectionne automatiquement le nouveau client créé (placé en tête de liste par clientStore)
  if (clientStore.clients.length > 0) {
    selectedClient.value = clientStore.clients[0];
    search.value = '';
  }
}

async function submit() {
  if (!canSubmit.value || !selectedClient.value) return;
  const ok = await dossierStore.addDossier({
    title: title.value.trim(),
    client_id: selectedClient.value.id,
    type_affair: typeAffair.value,
  });
  if (ok) emit('created');
}

watch(() => props.isOpen, (open:any) => {
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) {
    title.value = '';
    search.value = '';
    typeAffair.value = 'CONSTITUTION';
    selectedClient.value = props.defaultClient ?? null;
    isAddClientOpen.value = false;
    dossierStore.errorMessage = '';
    dossierStore.fieldErrors = {};
    if (clientStore.clients.length === 0) clientStore.fetchClients();
  }
});

watch(isAddClientOpen, (open:any) => {
  if (!open && props.isOpen) {
    document.body.style.overflow = 'hidden';
  }
});

onUnmounted(() => { document.body.style.overflow = ''; });
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; z-index: 10000; display: flex; align-items: center; justify-content: center;
  padding: 1.5rem; background: rgba(15, 23, 42, 0.42);
}
.modal-card {
  background: #fff; 
  border-radius: 16px; 
  padding: 1.5rem; 
  width: 100%; 
  max-width: 650px; max-height: 90vh;
  display: flex; flex-direction: column; gap: 1.25rem; overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
}

.border-wrapper {
  width: 100%;
  border: 1px solid #e8ecf1;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  border-radius: 0.75rem;
}

.modal-header { display: flex; justify-content: space-between; align-items: center; }
.modal-title { 
  margin: 0; 
  font-size: 1.15rem; 
  font-weight: 600; 
  color: #111827; 
}
.close-btn { background: none; border: none; font-size: 1.5rem; color: #9ca3af; cursor: pointer; line-height: 1; }
.close-btn:hover { color: #4b5563; }

.field { 
  display: flex; 
  flex-direction: column;
}

.field-label { 
  font-size: 0.8rem; 
  font-weight: 600; 
  color: #374151; 
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.required-mark {
  color: #ef4444;
}

.selected-client {
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  gap: 0.75rem;
  padding: 0.7rem 0.9rem; 
  background: #f8faff; 
  border-radius: 10px;
}
.info { display: flex; flex-direction: column; min-width: 0; }
.name { font-size: 0.92rem; font-weight: 500; color: #111827; }
.meta { font-size: 0.78rem; color: #6b7280; }
.change-btn { background: none; border: none; color: var(--primary-color, #2563eb); font-weight: 600; font-size: 0.8rem; cursor: pointer; }
.change-btn:hover { text-decoration: underline; }

.client-selection-box {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.search-actions-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
}

.search-actions-row :deep(.input-group) {
  max-width: 100%;
  flex: 1;
}

.search-actions-row :deep(.outline-btn) {
  white-space: nowrap;
  flex-shrink: 0;
}

.fields-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  width: 100%;
}

.fields-row :deep(.input-group) {
  max-width: 100%;
}

@media (max-width: 640px) {
  .fields-row {
    grid-template-columns: 1fr;
  }
  .search-actions-row {
    flex-direction: column;
    align-items: stretch;
  }
}

.results { 
  list-style: none; 
  margin: 0; 
  padding: 0.25rem; 
  max-height: 160px; 
  overflow-y: auto; 
  display: flex; 
  flex-direction: column; 
  gap: 0.35rem; 
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
}
.results li {
  display: flex; flex-direction: column; padding: 0.5rem 0.75rem; border-radius: 8px;
  cursor: pointer; transition: background-color 0.15s;
  background: #ffffff;
  border: 1px solid #f3f4f6;
}
.results li:hover { 
  background: #d3d6d9; 
}
.hint { margin: 0; text-align: center; color: #9ca3af; font-size: 0.82rem; padding: 0.5rem 0; }
.error-text { margin: 0; font-size: 0.8rem; color: #dc2626; }

.modal-footer { width: 100%; display: flex; gap: 0.75rem; margin-top: 0.5rem; }
.btn {
  flex: 1; padding: 0.65rem 1rem; border-radius: 10px; font-weight: 600; font-size: 0.9rem; cursor: pointer;
  border: none; background: #f3f4f6; color: #4b5563; transition: all 0.2s ease;
}
.btn:hover { background: #e5e7eb; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--primary-color, #2563eb); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--primary-color-dark, #1d4ed8); }
</style>

<style>
.modal-fade-enter-active .modal-card,
.modal-fade-leave-active .modal-card {
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-fade-enter-from .modal-card,
.modal-fade-leave-to .modal-card {
  opacity: 0;
  transform: scale(0.9);
}
</style>
<style>
.modal-fade-enter-active .modal-card,
.modal-fade-leave-active .modal-card {
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-fade-enter-from .modal-card,
.modal-fade-leave-to .modal-card {
  opacity: 0;
  transform: scale(0.9);
}
</style>
