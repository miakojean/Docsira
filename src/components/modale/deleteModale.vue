<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="300">
      <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card" role="dialog" aria-modal="true">

          <template v-if="isLoading && !isSuccess">
            <div class="modal-header w-full" style="justify-content: center;">
                <h3 class="">Traitement en cours</h3>
            </div>
            <div class="modal-body text-center" style="align-items: center; justify-content: center; min-height: 150px; display: flex; flex-direction: column;">
                <div class="spinner"></div>
                <p style="margin-top: 1rem; color: #6b7280; font-size: 0.95rem;">Veuillez patienter...</p>
            </div>
          </template>

          <template v-else-if="!isSuccess">
            <div class="modal-header">
              <div class="title-container">
                <span class="header-icon-box is-danger">
                  <!-- Icône Corbeille -->
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="icon">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM8 9h8v10H8V9zm7.5-5l-1-1h-5l-1 1H5v2h14V4h-3.5z"/>
                  </svg>
                </span>
                <h3 class="modal-title">
                  {{ title || `Supprimer le ${isFolder ? 'dossier' : 'fichier'}` }}
                </h3>
              </div>
              <button class="close-btn" @click="closeModal" aria-label="Fermer la modale">
                &times;
              </button>
            </div>

            <div class="modal-body">
              <p class="delete-description">
                <template v-if="description">{{ description }}</template>
                <template v-else>Êtes-vous sûr de vouloir supprimer définitivement <strong>{{ itemName }}</strong> ?</template>
              </p>
              <p class="delete-subtext">
                <template v-if="subtext">{{ subtext }}</template>
                <template v-else>Attention, cette action est <strong>irréversible</strong>. Cet élément sera supprimé pour vous et pour tous les collaborateurs qui y ont accès.</template>
              </p>
            </div>

            <div class="modal-footer">
              <button class="btn" @click="closeModal" :disabled="isLoading">Annuler</button>
              <button class="btn btn-danger" @click="confirmDelete" :disabled="isLoading">
                {{ isLoading ? 'En cours...' : 'Oui, supprimer' }}
              </button>
            </div>
          </template>

          <template v-else>
            <div class="modal-header w-full">
                <h3 class="">Succès</h3>
                <button class="close-btn" @click="closeModal" aria-label="Fermer la modale">
                    &times;
                </button>
            </div>

            <!-- Icône de succès (Macaron ondulé) -->
            <div class="icon-container">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="success-badge">
                <path d="M12 2L14.8 4.2L18.2 3.8L19.4 7.1L22.4 8.7L21 12L22.4 15.3L19.4 16.9L18.2 20.2L14.8 19.8L12 22L9.2 19.8L5.8 20.2L4.6 16.9L1.6 15.3L3 12L1.6 8.7L4.6 7.1L5.8 3.8L9.2 4.2L12 2Z" fill="#dcfce7"/>
                <path d="M8 12.5L10.5 15L16 9" stroke="#005792" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>

            <!-- Textes -->
            <div class="modal-body text-center" style="align-items: center; text-align: center;">
                <h3 class="modal-title" style="margin-bottom: 0.5rem;">{{ successTitle || 'Opération réussie' }}</h3>
                <p class="modal-description" style="color: #6b7280; font-size: 0.95rem; margin: 0;">
                  {{ successSubtitle || 'L\'élément a été traité avec succès.' }}
                </p>
            </div>

            <!-- Bouton d'action -->
            <div class="modal-footer" style="justify-content: center; margin-top: 1rem;">
              <mainButton @click="closeModal" label="Continuer" style="width: 100%;"/>
            </div>
          </template>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { watch, onUnmounted } from 'vue';
import mainButton from '../buttons/mainButton.vue';

const props = withDefaults(
  defineProps<{
    isOpen: boolean;
    itemName?: string;
    isFolder?: boolean;
    title?: string;
    description?: string;
    subtext?: string;
    isSuccess?: boolean;
    isLoading?: boolean;
    successTitle?: string;
    successSubtitle?: string;
  }>(),
  {
    isOpen: false,
    itemName: 'Élément sélectionné',
    isFolder: true,
    isSuccess: false,
    isLoading: false,
  }
);

const emit = defineEmits(['close', 'delete']);

const closeModal = () => {
  emit('close');
};

const confirmDelete = () => {
  emit('delete');
  // If the parent manages async state (isLoading), we don't close immediately.
  // We'll let the parent close it. Wait, let's just emit 'delete'.
  // If `isLoading` or `isSuccess` props are not used by the parent, they might expect it to close.
  // Since we are changing the paradigm to 'async modal', we will rely on the parent to close it if it's successful,
  // or we can just not call `closeModal()` here and update the parents.
  // Actually, to be safe: we don't close it automatically anymore. The parent must close it or change its state to isSuccess.
};

// Gestion du blocage du scroll en arrière-plan
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});

onUnmounted(() => {
  document.body.style.overflow = '';
});
</script>

<style scoped>
/* --- Overlay --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(17, 24, 39, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

/* --- Structure de base --- */
.modal-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  width: 85%;
  position: relative;
  z-index: 101;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* --- En-tête --- */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon-box {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Thème Alerte / Danger */
.header-icon-box.is-danger {
  background-color: #fee2e2; /* Rouge très clair */
  color: #dc2626; /* Rouge vif */
}

.header-icon-box .icon {
  width: 22px;
  height: 22px;
}

.modal-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #1f2937;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.75rem;
  cursor: pointer;
  color: #9ca3af;
  line-height: 1;
  padding: 0;
  transition: color 0.2s ease;
}

.close-btn:hover { color: #ef4444; }

/* --- Corps de la modale --- */
.modal-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.delete-description {
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
  line-height: 1.4;
}

.delete-subtext {
  margin: 0;
  font-size: 0.85rem;
  color: #ef4444; /* Texte rouge pour insister sur l'aspect irréversible */
  line-height: 1.4;
}

.icon-container {
  width: 30%;
  margin: auto;
}

/* --- Pied de page --- */
.modal-footer {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn {
  flex: 1;
  padding: 0.65rem 1rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #4b5563;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

/* Bouton spécifique pour la suppression */
.btn-danger {
  background-color: #dc2626; /* Rouge vif */
  color: white;
}

.btn-danger:hover {
  background-color: #b91c1c; /* Rouge plus foncé au survol */
}

/* --- Responsive Ordinateur --- */
@media (min-width: 1024px) {
  .modal-card {
    width: 32%;
    max-width: 450px;
  }
}

/* --- Loader --- */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

<style>
/* ⚡️ Transitions ciblées uniquement sur la carte pour que l'overlay apparaisse instantanément */
.modal-fade-enter-active .modal-card,
.modal-fade-leave-active .modal-card {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.modal-fade-enter-from .modal-card,
.modal-fade-leave-to .modal-card {
  opacity: 0;
  transform: scale(0.95);
}
</style>