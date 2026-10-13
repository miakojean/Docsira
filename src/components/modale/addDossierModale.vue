<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="300">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <form class="modal-card" role="dialog" aria-modal="true" @submit.prevent="submit">
          <div class="modal-header">
            <h3 class="modal-title">Nouveau dossier</h3>
            <button type="button" class="close-btn" @click="$emit('close')" aria-label="Fermer la modale">&times;</button>
          </div>

          <div class="field">
            <label class="field-label">Client</label>
            <div v-if="selectedClient" class="selected-client">
              <div class="info">
                <span class="name">{{ selectedClient.nom_complet }}</span>
                <span class="meta">{{ selectedClient.reference_client }}</span>
              </div>
              <button type="button" class="change-btn" @click="selectedClient = null; search = ''">Changer</button>
            </div>
            <template v-else>
              <input v-model="search" type="text" class="text-input" placeholder="Rechercher un client (nom, référence, email...)" autocomplete="off" />
              <ul v-if="matchingClients.length" class="results">
                <li v-for="c in matchingClients" :key="c.id" @click="selectedClient = c">
                  <span class="name">{{ c.nom_complet }}</span>
                  <span class="meta">{{ c.reference_client }}<template v-if="c.email"> · {{ c.email }}</template></span>
                </li>
              </ul>
              <p v-else class="hint">Aucun client trouvé.</p>
            </template>
            <p v-if="dossierStore.fieldErrors.client_id" class="error-text">{{ dossierStore.fieldErrors.client_id }}</p>
          </div>

          <div class="field">
            <label class="field-label" for="new-dossier-title">Nom du dossier</label>
            <input id="new-dossier-title" v-model="title" type="text" class="text-input" placeholder="Ex : Constitution de la société SARL" maxlength="200" />
            <p v-if="dossierStore.fieldErrors.title" class="error-text">{{ dossierStore.fieldErrors.title }}</p>
          </div>

          <p v-if="dossierStore.errorMessage" class="error-text">{{ dossierStore.errorMessage }}</p>

          <div class="modal-footer">
            <button type="button" class="btn" @click="$emit('close')">Annuler</button>
            <button type="submit" class="btn btn-primary" :disabled="!canSubmit">
              {{ dossierStore.isLoading ? 'Création...' : 'Créer le dossier' }}
            </button>
          </div>
        </form>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import { useClientDossierStore } from '../../stores/dossierStore';
import { useClientStore, type ClientListItem } from '../../stores/clientStore';

const props = defineProps<{ isOpen: boolean }>();
const emit = defineEmits(['close', 'created']);

const dossierStore = useClientDossierStore();
const clientStore = useClientStore();

const title = ref('');
const search = ref('');
const selectedClient = ref<ClientListItem | null>(null);

const matchingClients = computed(() => {
  const q = search.value.trim().toLowerCase();
  return clientStore.clients
    .filter(c => !q || [c.nom_complet, c.reference_client, c.email, c.telephone_1]
      .some(v => (v || '').toLowerCase().includes(q)))
    .slice(0, 6);
});

const canSubmit = computed(() =>
  !!selectedClient.value && title.value.trim().length > 0 && !dossierStore.isLoading
);

async function submit() {
  if (!canSubmit.value || !selectedClient.value) return;
  const ok = await dossierStore.addDossier({
    title: title.value.trim(),
    client_id: selectedClient.value.id,
  });
  if (ok) emit('created');
}

watch(() => props.isOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) {
    title.value = '';
    search.value = '';
    selectedClient.value = null;
    dossierStore.errorMessage = '';
    dossierStore.fieldErrors = {};
    if (clientStore.clients.length === 0) clientStore.fetchClients();
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
  background: #fff; border-radius: 16px; padding: 1.5rem; width: 100%; max-width: 480px; max-height: 90vh;
  display: flex; flex-direction: column; gap: 1.25rem; overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
}
.modal-header { display: flex; justify-content: space-between; align-items: center; }
.modal-title { margin: 0; font-size: 1.2rem; font-weight: 600; color: #111827; }
.close-btn { background: none; border: none; font-size: 1.5rem; color: #9ca3af; cursor: pointer; line-height: 1; }
.close-btn:hover { color: #4b5563; }

.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field-label { font-size: 0.8rem; font-weight: 600; color: #6b7280; }
.text-input {
  width: 100%; box-sizing: border-box; padding: 0.7rem 0.9rem; border: 1px solid #e5e7eb; border-radius: 10px;
  font-size: 0.9rem; outline: none; background: #f9fafb; color: #111827; transition: border-color 0.2s, box-shadow 0.2s;
}
.text-input:focus { border-color: var(--primary-color, #2563eb); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12); background: #fff; }

.selected-client {
  display: flex; align-items: center; justify-content: space-between; gap: 0.75rem;
  padding: 0.7rem 0.9rem; border: 1px solid var(--primary-color, #2563eb); background: #f8faff; border-radius: 10px;
}
.info { display: flex; flex-direction: column; min-width: 0; }
.name { font-size: 0.92rem; font-weight: 500; color: #111827; }
.meta { font-size: 0.78rem; color: #9ca3af; }
.change-btn { background: none; border: none; color: var(--primary-color, #2563eb); font-weight: 600; font-size: 0.8rem; cursor: pointer; }

.results { list-style: none; margin: 0; padding: 0; max-height: 200px; overflow-y: auto; display: flex; flex-direction: column; gap: 0.4rem; }
.results li {
  display: flex; flex-direction: column; padding: 0.65rem 0.8rem; border: 1px solid #f3f4f6; border-radius: 10px;
  cursor: pointer; transition: border-color 0.2s, background-color 0.2s;
}
.results li:hover { border-color: var(--primary-color, #2563eb); background: #f8faff; }
.hint { margin: 0; text-align: center; color: #9ca3af; font-size: 0.82rem; padding: 0.5rem 0; }
.error-text { margin: 0; font-size: 0.8rem; color: #dc2626; }

.modal-footer { display: flex; gap: 0.75rem; }
.btn {
  flex: 1; padding: 0.65rem 1rem; border-radius: 10px; font-weight: 600; font-size: 0.9rem; cursor: pointer;
  border: none; background: #f3f4f6; color: #4b5563; transition: all 0.2s ease;
}
.btn:hover { background: #e5e7eb; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--primary-color, #2563eb); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--primary-color-dark, #1d4ed8); }
</style>
