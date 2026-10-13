<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="300">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card" role="dialog" aria-modal="true">
          <div class="modal-header">
            <div class="title-container">
              <button v-if="mode === 'pick'" class="back-btn" @click="mode = 'list'" aria-label="Retour">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
                </svg>
              </button>
              <div>
                <h3 class="modal-title">{{ mode === 'list' ? 'Dossiers du client' : 'Lier un dossier' }}</h3>
                <p class="modal-subtitle" v-if="client">{{ client.nom_complet }}</p>
              </div>
            </div>
            <button class="close-btn" @click="$emit('close')" aria-label="Fermer la modale">&times;</button>
          </div>

          <!-- Liste des dossiers liés -->
          <div v-if="mode === 'list'" class="modal-body">
            <div v-if="linkedDossiers.length === 0" class="empty-state">
              <div class="empty-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.3" stroke="currentColor" class="size-8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
                </svg>
              </div>
              <p class="empty-title">Aucun dossier lié à ce client</p>
              <p class="empty-text">Liez un dossier de votre espace de travail à ce client.</p>
            </div>

            <ul v-else class="dossier-list">
              <li v-for="d in linkedDossiers" :key="d.id" class="dossier-item">
                <div class="dossier-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
                  </svg>
                </div>
                <div class="dossier-info">
                  <span class="dossier-name">{{ d.name }}</span>
                  <span class="dossier-meta">{{ d.reference }} · {{ d.fileCount }} {{ d.fileCount > 1 ? 'fichiers' : 'fichier' }}</span>
                </div>
                <button class="unlink-btn" @click="unlink(d.id)" title="Délier ce dossier" aria-label="Délier ce dossier">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                  </svg>
                </button>
              </li>
            </ul>
          </div>

          <!-- Sélection d'un dossier du workspace -->
          <div v-else class="modal-body">
            <input v-model="search" type="text" class="search-input" placeholder="Rechercher un dossier du workspace..." />

            <div v-if="dossierStore.isLoading" class="state-text">Chargement des dossiers...</div>
            <div v-else-if="availableDossiers.length === 0" class="state-text">
              {{ search ? 'Aucun dossier ne correspond à votre recherche.' : 'Tous les dossiers du workspace sont déjà liés.' }}
            </div>
            <ul v-else class="dossier-list">
              <li v-for="d in availableDossiers" :key="d.id" class="dossier-item selectable" @click="link(d.id)">
                <div class="dossier-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
                  </svg>
                </div>
                <div class="dossier-info">
                  <span class="dossier-name">{{ d.name }}</span>
                  <span class="dossier-meta">{{ d.reference }} · {{ d.fileCount }} {{ d.fileCount > 1 ? 'fichiers' : 'fichier' }}</span>
                </div>
                <span class="link-label">Lier</span>
              </li>
            </ul>
          </div>

          <div class="modal-footer">
            <button class="btn" @click="mode === 'pick' ? (mode = 'list') : $emit('close')">
              {{ mode === 'pick' ? 'Annuler' : 'Fermer' }}
            </button>
            <button v-if="mode === 'list'" class="btn btn-primary" @click="openPicker">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Lier un dossier
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import { useClientDossierStore } from '../../stores/dossierStore';

const props = defineProps<{
  isOpen: boolean;
  client: any;
}>();

defineEmits(['close']);

const dossierStore = useClientDossierStore();
const mode = ref<'list' | 'pick'>('list');
const search = ref('');

const linkedDossiers = computed(() =>
  props.client ? dossierStore.getLinkedDossiers(props.client.id) : []
);

const availableDossiers = computed(() => {
  if (!props.client) return [];
  const linkedIds = new Set(linkedDossiers.value.map(d => d.id));
  const q = search.value.trim().toLowerCase();
  return dossierStore.workspaceDossiers.filter(d =>
    !linkedIds.has(d.id) &&
    (!q || d.name.toLowerCase().includes(q) || d.reference.toLowerCase().includes(q))
  );
});

function openPicker() {
  search.value = '';
  mode.value = 'pick';
  dossierStore.fetchWorkspaceDossiers();
}

function link(dossierId: string) {
  dossierStore.linkDossier(props.client.id, dossierId);
  mode.value = 'list';
}

function unlink(dossierId: string) {
  dossierStore.unlinkDossier(props.client.id, dossierId);
}

watch(() => props.isOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) {
    mode.value = 'list';
    search.value = '';
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

.search-input {
  width: 100%; box-sizing: border-box; padding: 0.7rem 0.9rem; border: 1px solid #e5e7eb;
  border-radius: 10px; font-size: 0.9rem; outline: none; background: #f9fafb;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-input:focus { border-color: var(--primary-color, #2563eb); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12); background: #fff; }

.state-text { text-align: center; color: #9ca3af; font-size: 0.9rem; padding: 2rem 0; }

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
.link-label { font-size: 0.8rem; font-weight: 600; color: var(--primary-color, #2563eb); }

.unlink-btn {
  background: none; border: none; color: #9ca3af; cursor: pointer; padding: 0.35rem; border-radius: 8px;
  display: flex; transition: all 0.2s;
}
.unlink-btn:hover { background: #fef2f2; color: #dc2626; }

.modal-footer { display: flex; gap: 0.75rem; }
.btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 0.4rem;
  padding: 0.65rem 1rem; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
  cursor: pointer; border: none; background: #f3f4f6; color: #4b5563; transition: all 0.2s ease;
}
.btn:hover { background: #e5e7eb; }
.btn-primary { background: var(--primary-color, #2563eb); color: #fff; }
.btn-primary:hover { background: var(--primary-color-dark, #1d4ed8); }

.size-4 { width: 1rem; height: 1rem; }
.size-5 { width: 1.25rem; height: 1.25rem; }
.size-8 { width: 2rem; height: 2rem; }
</style>
