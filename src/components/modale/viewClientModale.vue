<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="300">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card" role="dialog" aria-modal="true">
          <div class="modal-header">
            <h3 class="modal-title">Détails du client</h3>
            <button class="close-btn" @click="$emit('close')" aria-label="Fermer la modale">&times;</button>
          </div>

          <div class="modal-body" v-if="client">
            <div class="info-section">
              <h4 class="section-title">Informations générales</h4>
              <div class="grid">
                <div class="info-item">
                  <span class="info-label">Référence</span>
                  <span class="info-value">{{ client.reference_client || '—' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Type de client</span>
                  <span class="info-value">{{ client.type_client === 'PERSONNE_MORALE' ? 'Personne morale' : 'Personne physique' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Statut</span>
                  <span class="info-value badge" :class="client.statut.toLowerCase()">{{ statutLabels[client.statut] || client.statut }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Créé le</span>
                  <span class="info-value">{{ formatDate(client.date_creation) }}</span>
                </div>
              </div>
            </div>

            <div class="info-section">
              <h4 class="section-title">Identité</h4>
              <div class="grid">
                <template v-if="client.type_client === 'PERSONNE_PHYSIQUE'">
                  <div class="info-item">
                    <span class="info-label">Nom</span>
                    <span class="info-value">{{ client.nom || '—' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Prénoms</span>
                    <span class="info-value">{{ client.prenoms || '—' }}</span>
                  </div>
                  <div class="info-item" v-if="client.date_naissance">
                    <span class="info-label">Date de naissance</span>
                    <span class="info-value">{{ formatDate(client.date_naissance) }}</span>
                  </div>
                  <div class="info-item" v-if="client.lieu_naissance">
                    <span class="info-label">Lieu de naissance</span>
                    <span class="info-value">{{ client.lieu_naissance }}</span>
                  </div>
                </template>
                <template v-else>
                  <div class="info-item">
                    <span class="info-label">Raison sociale</span>
                    <span class="info-value">{{ client.raison_sociale || '—' }}</span>
                  </div>
                  <div class="info-item" v-if="client.forme_juridique">
                    <span class="info-label">Forme juridique</span>
                    <span class="info-value">{{ client.forme_juridique }}</span>
                  </div>
                  <div class="info-item" v-if="client.numero_rccm">
                    <span class="info-label">Numéro RCCM</span>
                    <span class="info-value">{{ client.numero_rccm }}</span>
                  </div>
                  <div class="info-item" v-if="client.numero_cc">
                    <span class="info-label">Compte contribuable</span>
                    <span class="info-value">{{ client.numero_cc }}</span>
                  </div>
                  <div class="info-item" v-if="client.representant_legal_nom">
                    <span class="info-label">Représentant légal</span>
                    <span class="info-value">{{ client.representant_legal_nom }} ({{ client.representant_legal_fonction || 'N/A' }})</span>
                  </div>
                </template>
              </div>
            </div>

            <div class="info-section">
              <h4 class="section-title">Contact & Localisation</h4>
              <div class="grid">
                <div class="info-item">
                  <span class="info-label">Email</span>
                  <span class="info-value">{{ client.email || '—' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Téléphone 1</span>
                  <span class="info-value">{{ client.telephone_1 || '—' }}</span>
                </div>
                <div class="info-item" v-if="client.telephone_2">
                  <span class="info-label">Téléphone 2</span>
                  <span class="info-value">{{ client.telephone_2 }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Pays</span>
                  <span class="info-value">{{ client.pays || '—' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Ville</span>
                  <span class="info-value">{{ client.ville || '—' }}</span>
                </div>
                <div class="info-item" v-if="client.commune">
                  <span class="info-label">Commune</span>
                  <span class="info-value">{{ client.commune }}</span>
                </div>
                <div class="info-item" style="grid-column: 1 / -1;">
                  <span class="info-label">Adresse</span>
                  <span class="info-value">{{ client.adresse || '—' }}</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { watch, onUnmounted } from 'vue';

const props = defineProps<{ 
  isOpen: boolean;
  client: any;
}>();

const emit = defineEmits(['close']);

const statutLabels: Record<string, string> = {
  ACTIF: 'Actif',
  INACTIF: 'Inactif',
  PROSPECT: 'Prospect',
  ARCHIVE: 'Archivé',
};

function formatDate(value: string) {
  if (!value) return '—';
  return new Date(value).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
}

watch(() => props.isOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : '';
});

onUnmounted(() => { document.body.style.overflow = ''; });
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000; /* Higher than dropdown */
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
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.modal-header { display: flex; justify-content: space-between; align-items: center; }
.modal-title { margin: 0; font-size: 1.25rem; font-weight: 600; color: #111827; }
.close-btn { background: none; border: none; font-size: 1.5rem; color: #9ca3af; cursor: pointer; line-height: 1; }
.close-btn:hover { color: #4b5563; }

.modal-body { display: flex; flex-direction: column; gap: 1.5rem; }

.info-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 0.25rem;
}

.grid { 
  display: grid; 
  grid-template-columns: repeat(2, 1fr); 
  gap: 1rem; 
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.info-label {
  font-size: 0.75rem;
  color: #9ca3af;
}

.info-value {
  font-size: 0.95rem;
  color: #111827;
  font-weight: 500;
  word-break: break-word;
}

.badge { display: inline-flex; width: fit-content; padding: 0.2rem 0.65rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.badge.actif { background: #dcfce7; color: #166534; }
.badge.inactif { background: #f3f4f6; color: #4b5563; }
.badge.prospect { background: #dbeafe; color: #1e40af; }
.badge.archive { background: #fef3c7; color: #92400e; }

@media (max-width: 640px) {
  .grid { grid-template-columns: 1fr; }
}
</style>
