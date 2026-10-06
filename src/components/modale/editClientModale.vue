<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="300">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card" role="dialog" aria-modal="true">
          <div class="modal-header">
            <h3 class="modal-title">Modifier client</h3>
            <button class="close-btn" @click="$emit('close')" aria-label="Fermer la modale">&times;</button>
          </div>

          <div class="type-switch">
            <button
              type="button"
              :class="{ active: form.type_client === 'PERSONNE_PHYSIQUE' }"
              @click="form.type_client = 'PERSONNE_PHYSIQUE'"
            >Personne physique</button>
            <button
              type="button"
              :class="{ active: form.type_client === 'PERSONNE_MORALE' }"
              @click="form.type_client = 'PERSONNE_MORALE'"
            >Personne morale</button>
          </div>

          <form class="modal-body" @submit.prevent="submit">
            <div class="grid">
              <template v-if="form.type_client === 'PERSONNE_PHYSIQUE'">
                <BaseInput label="Nom" required placeholder="Nom" v-model="form.nom" :errorMessage="err('nom')" />
                <BaseInput label="Prénoms" required placeholder="Prénoms" v-model="form.prenoms" :errorMessage="err('prenoms')" />
                <BaseInput label="Date de naissance" type="date" placeholder="" v-model="form.date_naissance" :errorMessage="err('date_naissance')" />
                <BaseInput label="Lieu de naissance" placeholder="Lieu de naissance" v-model="form.lieu_naissance" :errorMessage="err('lieu_naissance')" />
              </template>

              <template v-else>
                <BaseInput label="Raison sociale" required placeholder="Raison sociale" v-model="form.raison_sociale" :errorMessage="err('raison_sociale')" />
                <BaseInput label="Forme juridique" placeholder="SARL, SA..." v-model="form.forme_juridique" :errorMessage="err('forme_juridique')" />
                <BaseInput label="Numéro RCCM" placeholder="Numéro RCCM" v-model="form.numero_rccm" :errorMessage="err('numero_rccm')" />
                <BaseInput label="Compte contribuable" placeholder="Numéro CC" v-model="form.numero_cc" :errorMessage="err('numero_cc')" />
                <BaseInput label="Représentant légal" placeholder="Nom du représentant" v-model="form.representant_legal_nom" :errorMessage="err('representant_legal_nom')" />
                <BaseInput label="Fonction du représentant" placeholder="Gérant, DG..." v-model="form.representant_legal_fonction" :errorMessage="err('representant_legal_fonction')" />
              </template>

              <BaseInput label="Téléphone" required type="tel" placeholder="+225XXXXXXXXXX" v-model="form.telephone_1" :errorMessage="err('telephone_1')" />
              <BaseInput label="Téléphone 2" type="tel" placeholder="Optionnel" v-model="form.telephone_2" :errorMessage="err('telephone_2')" />
              <BaseInput label="Email" type="email" placeholder="email@exemple.com" v-model="form.email" :errorMessage="err('email')" />
              <BaseInput label="Ville" placeholder="Ville" v-model="form.ville" :errorMessage="err('ville')" />
              <BaseInput label="Commune" placeholder="Commune" v-model="form.commune" :errorMessage="err('commune')" />
              <BaseInput label="Pays" placeholder="Côte d'Ivoire" v-model="form.pays" :errorMessage="err('pays')" />
              <BaseInput label="Adresse" placeholder="Adresse" v-model="form.adresse" :errorMessage="err('adresse')" />
            </div>

            <p v-if="clientStore.errorMessage" class="error-content">{{ clientStore.errorMessage }}</p>

            <div class="modal-footer">
              <mainButton label="Mettre à jour le client" :disabled="clientStore.isLoading" :isLoading="clientStore.isLoading" />
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { reactive, watch, onUnmounted } from 'vue';
import BaseInput from '../BaseInput/BaseInput.vue';
import mainButton from '../buttons/mainButton.vue';
import { useClientStore, type ClientPayload } from '../../stores/clientStore';

const props = defineProps<{ isOpen: boolean; client: any }>();
const emit = defineEmits(['close', 'updated']);

const clientStore = useClientStore();

const emptyForm = (): ClientPayload => ({
  type_client: 'PERSONNE_PHYSIQUE',
  nom: '', prenoms: '', date_naissance: '', lieu_naissance: '',
  raison_sociale: '', forme_juridique: '', numero_rccm: '', numero_cc: '',
  representant_legal_nom: '', representant_legal_fonction: '',
  telephone_1: '', telephone_2: '', email: '', adresse: '', ville: '', commune: '', pays: '',
});

const form = reactive<ClientPayload>(emptyForm());

function err(field: string) {
  return clientStore.fieldErrors[field] || '';
}

// Les champs qui ne concernent pas le type choisi ne sont pas envoyés
function buildPayload(): ClientPayload {
  const payload = { ...form };
  if (form.type_client === 'PERSONNE_PHYSIQUE') {
    delete payload.raison_sociale; delete payload.forme_juridique;
    delete payload.numero_rccm; delete payload.numero_cc;
    delete payload.representant_legal_nom; delete payload.representant_legal_fonction;
  } else {
    delete payload.nom; delete payload.prenoms;
    delete payload.date_naissance; delete payload.lieu_naissance;
  }
  return payload;
}

async function submit() {
  if (!props.client || !props.client.id) return;
  const ok = await clientStore.updateClient(props.client.id, buildPayload());
  if (ok) emit('updated');
}

watch(() => props.isOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) {
    if (props.client) {
      // Map existing client data to the form
      Object.assign(form, emptyForm());
      for (const key in form) {
        if (props.client[key] !== undefined && props.client[key] !== null) {
          (form as any)[key] = props.client[key];
        }
      }
    } else {
      Object.assign(form, emptyForm());
    }
    clientStore.fieldErrors = {};
    clientStore.errorMessage = '';
  }
});

onUnmounted(() => { document.body.style.overflow = ''; });
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.42);
}

.modal-card {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 720px;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.modal-header { display: flex; justify-content: space-between; align-items: center; }
.modal-title { margin: 0; font-size: 1.25rem; font-weight: 600; color: #111827; }
.close-btn { background: none; border: none; font-size: 1.5rem; color: #9ca3af; cursor: pointer; line-height: 1; }
.close-btn:hover { color: #4b5563; }

.type-switch {
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem;
  background: #f3f4f6;
  border-radius: 999px;
}
.type-switch button {
  flex: 1;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 999px;
  background: transparent;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}
.type-switch button.active {
  background: #fff;
  color: var(--primary-color);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.modal-body { display: flex; flex-direction: column; gap: 1rem; }
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
.grid :deep(.input-group) { max-width: 100%; gap: 0.35rem; }
.modal-footer { display: flex; justify-content: flex-end; }
.modal-footer :deep(.main-button) { max-width: 260px; }
.error-content { color: #ef4444; font-size: 0.875rem; margin: 0; }

@media (max-width: 640px) {
  .grid { grid-template-columns: 1fr; }
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
