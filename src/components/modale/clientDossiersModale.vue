<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="300">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card" role="dialog" aria-modal="true">
          <div class="modal-header">
            <div class="title-container">
              <button v-if="mode === 'add'" class="back-btn" @click="mode = 'list'" aria-label="Retour">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
                </svg>
              </button>
              <div>
                <h3 class="modal-title">{{ mode === 'list' ? 'Dossiers du client' : 'Ajouter un dossier' }}</h3>
                <p class="modal-subtitle" v-if="client && mode === 'list'">{{ client.nom_complet }}</p>
              </div>
            </div>
            <button class="close-btn" @click="$emit('close')" aria-label="Fermer la modale">&times;</button>
          </div>

          <!-- Liste des dossiers du client -->
          <div v-if="mode === 'list'" class="modal-body">
            <div v-if="dossierStore.isLoading && dossiers.length === 0" class="state-text">Chargement des dossiers...</div>

            <div v-else-if="dossiers.length === 0" class="empty-state">
              <div class="empty-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.3" stroke="currentColor" class="size-8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
                </svg>
              </div>
              <p class="empty-title">Aucun dossier lié à ce client</p>
              <p class="empty-text">Créez un dossier et rattachez-le à un client.</p>
            </div>

            <ul v-else class="dossier-list">
              <li v-for="d in dossiers" :key="d.id" class="dossier-item">
                <div class="dossier-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
                  </svg>
                </div>
                <div class="dossier-info">
                  <span class="dossier-name">{{ d.title }}</span>
                  <span class="dossier-meta">{{ d.reference_affair }} · {{ statutLabels[d.statut] || d.statut }}</span>
                </div>
                <div class="item-actions">
                  <button type="button" class="action-btn" title="Modifier le dossier" @click.stop="openEdit(d)">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                    </svg>
                  </button>
                  <button type="button" class="action-btn danger" title="Supprimer le dossier" @click.stop="openDelete(d)">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                    </svg>
                  </button>
                </div>
              </li>
            </ul>
          </div>

          <!-- Formulaire d'ajout -->
          <form v-else class="modal-body" @submit.prevent="submit">
            <div class="field">
              <label class="field-label">Client</label>

              <div v-if="selectedClient" class="selected-client">
                <div class="dossier-info">
                  <span class="dossier-name">{{ selectedClient.nom_complet }}</span>
                  <span class="dossier-meta">{{ selectedClient.reference_client }}</span>
                </div>
                <button type="button" class="change-btn" @click="selectedClient = null; clientSearch = ''">Changer</button>
              </div>

              <template v-else>
                <input v-model="clientSearch" type="text" class="text-input" placeholder="Rechercher un client (nom, référence, email...)" autocomplete="off" />
                <ul v-if="matchingClients.length" class="dossier-list client-results">
                  <li v-for="c in matchingClients" :key="c.id" class="dossier-item selectable" @click="selectedClient = c">
                    <div class="dossier-info">
                      <span class="dossier-name">{{ c.nom_complet }}</span>
                      <span class="dossier-meta">{{ c.reference_client }}<template v-if="c.email"> · {{ c.email }}</template></span>
                    </div>
                  </li>
                </ul>
                <p v-else class="state-text small">Aucun client trouvé.</p>
              </template>
              <p v-if="dossierStore.fieldErrors.client_id" class="error-text">{{ dossierStore.fieldErrors.client_id }}</p>
            </div>

            <div class="field">
              <label class="field-label" for="dossier-title">Nom du dossier</label>
              <input id="dossier-title" v-model="title" type="text" class="text-input" placeholder="Ex : Constitution de la société SARL" maxlength="200" />
              <p v-if="dossierStore.fieldErrors.title" class="error-text">{{ dossierStore.fieldErrors.title }}</p>
            </div>

            <p v-if="dossierStore.errorMessage" class="error-text">{{ dossierStore.errorMessage }}</p>
          </form>

          <div class="modal-footer">
            <button class="btn" type="button" @click="mode === 'add' ? (mode = 'list') : $emit('close')">
              {{ mode === 'add' ? 'Annuler' : 'Fermer' }}
            </button>
            <button v-if="mode === 'list'" class="btn btn-primary" type="button" @click="openAdd">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Ajouter un dossier
            </button>
            <button v-else class="btn btn-primary" type="button" :disabled="!canSubmit" @click="submit">
              {{ dossierStore.isLoading ? 'Création...' : 'Créer le dossier' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modale de modification -->
    <editDossierModale
      :isOpen="isEditOpen"
      :dossier="editingDossier"
      @close="isEditOpen = false"
      @updated="isEditOpen = false"
    />

    <!-- Modale de suppression -->
    <deleteModale
      :isOpen="isDeleteOpen"
      :isLoading="isDeleting"
      :isSuccess="isDeleteSuccess"
      :itemName="dossierToDelete?.title || 'ce dossier'"
      :isFolder="true"
      title="Supprimer le dossier"
      description="Êtes-vous sûr de vouloir supprimer définitivement ce dossier ?"
      subtext="Attention, cette action est irréversible."
      @close="isDeleteOpen = false; isDeleteSuccess = false"
      @delete="confirmDelete"
    />
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import { useClientDossierStore, type Dossier } from '../../stores/dossierStore';
import { useClientStore, type ClientListItem } from '../../stores/clientStore';
import editDossierModale from './editDossierModale.vue';
import deleteModale from './deleteModale.vue';

const props = defineProps<{
  isOpen: boolean;
  client: ClientListItem | null;
}>();

defineEmits(['close']);

const dossierStore = useClientDossierStore();
const clientStore = useClientStore();

const mode = ref<'list' | 'add'>('list');
const title = ref('');
const clientSearch = ref('');
const selectedClient = ref<ClientListItem | null>(null);

// Gestion modification / suppression
const isEditOpen = ref(false);
const editingDossier = ref<Dossier | null>(null);
const isDeleteOpen = ref(false);
const dossierToDelete = ref<Dossier | null>(null);
const isDeleting = ref(false);
const isDeleteSuccess = ref(false);

const statutLabels: Record<string, string> = {
  NOUVEAU: 'Nouveau',
  EN_COURS: 'En cours',
  EN_ATTENTE: 'En attente',
  BLOQUE: 'Bloqué',
  TERMINE: 'Terminé',
  CLOTURE: 'Clôturé',
  ANNULE: 'Annulé',
};

const dossiers = computed(() =>
  props.client ? dossierStore.dossiersByClient[props.client.id] ?? [] : []
);

const matchingClients = computed(() => {
  const q = clientSearch.value.trim().toLowerCase();
  return clientStore.clients
    .filter(c => !q || [c.nom_complet, c.reference_client, c.email, c.telephone_1]
      .some(v => (v || '').toLowerCase().includes(q)))
    .slice(0, 6);
});

const canSubmit = computed(() =>
  !!selectedClient.value && title.value.trim().length > 0 && !dossierStore.isLoading
);

function openAdd() {
  title.value = '';
  clientSearch.value = '';
  selectedClient.value = props.client;
  dossierStore.errorMessage = '';
  dossierStore.fieldErrors = {};
  if (clientStore.clients.length === 0) clientStore.fetchClients();
  mode.value = 'add';
}

function openEdit(d: Dossier) {
  editingDossier.value = d;
  isEditOpen.value = true;
}

function openDelete(d: Dossier) {
  dossierToDelete.value = d;
  isDeleteSuccess.value = false;
  isDeleteOpen.value = true;
}

async function confirmDelete() {
  if (!dossierToDelete.value) return;
  isDeleting.value = true;
  const ok = await dossierStore.deleteDossier(dossierToDelete.value.id);
  isDeleting.value = false;
  if (ok) {
    isDeleteSuccess.value = true;
    setTimeout(() => {
      isDeleteOpen.value = false;
      isDeleteSuccess.value = false;
    }, 1200);
  }
}

async function submit() {
  if (!canSubmit.value || !selectedClient.value) return;
  const targetId = selectedClient.value.id;
  const ok = await dossierStore.addDossier({
    title: title.value.trim(),
    client_id: targetId,
  });
  if (ok) {
    // Si le dossier est rattaché à un autre client, on rafraîchit la liste du client courant
    mode.value = 'list';
  }
}

watch(() => props.isOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : '';
  if (open && props.client) {
    mode.value = 'list';
    dossierStore.fetchClientDossiers(props.client.id);
  }
});

onUnmounted(() => { document.body.style.overflow = ''; });
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.42);
}

.modal-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.modal-header { display: flex; justify-content: space-between; align-items: flex-start; }
.title-container { display: flex; align-items: center; gap: 0.6rem; }
.modal-title { margin: 0; font-size: 1.2rem; font-weight: 600; color: #111827; }
.modal-subtitle { margin: 0.15rem 0 0; font-size: 0.85rem; color: #6b7280; }
.close-btn { background: none; border: none; font-size: 1.5rem; color: #9ca3af; cursor: pointer; line-height: 1; }
.close-btn:hover { color: #4b5563; }

.back-btn {
  background: #f3f4f6; border: none; border-radius: 8px; width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center; cursor: pointer; color: #4b5563;
  transition: background-color 0.2s;
}
.back-btn:hover { background: #e5e7eb; }

.modal-body { display: flex; flex-direction: column; gap: 1rem; overflow-y: auto; min-height: 180px; }

.empty-state {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; padding: 1.5rem 1rem; gap: 0.35rem;
}
.empty-icon {
  width: 64px; height: 64px; border-radius: 50%; background: #f3f4f6; color: #9ca3af;
  display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;
}
.empty-title { margin: 0; font-size: 1rem; font-weight: 600; color: #374151; }
.empty-text { margin: 0; font-size: 0.85rem; color: #9ca3af; }

.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field-label { font-size: 0.8rem; font-weight: 600; color: #6b7280; }
.text-input {
  width: 100%; box-sizing: border-box; padding: 0.7rem 0.9rem; border: 1px solid #e5e7eb;
  border-radius: 10px; font-size: 0.9rem; outline: none; background: #f9fafb; color: #111827;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.text-input:focus { border-color: var(--primary-color, #2563eb); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12); background: #fff; }

.selected-client {
  display: flex; align-items: center; justify-content: space-between; gap: 0.75rem;
  padding: 0.7rem 0.9rem; border: 1px solid var(--primary-color, #2563eb); background: #f8faff; border-radius: 10px;
}
.change-btn { background: none; border: none; color: var(--primary-color, #2563eb); font-weight: 600; font-size: 0.8rem; cursor: pointer; }

.client-results { max-height: 200px; overflow-y: auto; }
.state-text { text-align: center; color: #9ca3af; font-size: 0.9rem; padding: 2rem 0; margin: 0; }
.state-text.small { padding: 0.5rem 0; font-size: 0.82rem; }
.error-text { margin: 0; font-size: 0.8rem; color: #dc2626; }

.dossier-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.dossier-item {
  display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem;
  border: 1px solid #f3f4f6; border-radius: 12px; background: #fff;
  transition: border-color 0.2s, background-color 0.2s;
}
.dossier-item.selectable { cursor: pointer; }
.dossier-item.selectable:hover { border-color: var(--primary-color, #2563eb); background: #f8faff; }
.dossier-icon {
  width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
  background: #eff6ff; color: var(--primary-color, #2563eb);
  display: flex; align-items: center; justify-content: center;
}
.dossier-info { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.dossier-name { font-size: 0.92rem; font-weight: 500; color: #111827; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.dossier-meta { font-size: 0.78rem; color: #9ca3af; }

.item-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.action-btn {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.4rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.action-btn:hover {
  background: #f3f4f6;
  color: #111827;
}
.action-btn.danger:hover {
  background: #fef2f2;
  color: #dc2626;
}

.modal-footer { display: flex; gap: 0.75rem; }
.btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 0.4rem;
  padding: 0.65rem 1rem; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
  cursor: pointer; border: none; background: #f3f4f6; color: #4b5563; transition: all 0.2s ease;
}
.btn:hover { background: #e5e7eb; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--primary-color, #2563eb); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--primary-color-dark, #1d4ed8); }

.size-4 { width: 1rem; height: 1rem; }
.size-5 { width: 1.25rem; height: 1.25rem; }
.size-8 { width: 2rem; height: 2rem; }
</style>
