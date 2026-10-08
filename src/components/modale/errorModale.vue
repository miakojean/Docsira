<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="300">
        <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
            <div class="modal-card" role="dialog" aria-modal="true">

                <div class="modal-header w-full">
                    <h3 class="">{{ modaleTitle }}</h3>
                    <button class="close-btn" @click="$emit('close')" aria-label="Fermer la modale">
                        &times;
                    </button>
                </div>

                <!-- Icône d'erreur -->
                <div class="icon-container">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="error-badge">
                      <!-- Fond rouge ondulé/rond -->
                      <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z" fill="#fee2e2"/>
                      <!-- Croix rouge foncé -->
                      <path d="M15 9L9 15M9 9L15 15" stroke="#991b1b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>

                <!-- Textes -->
                <div class="modal-body">
                    <h3 class="modal-title">{{ title }}</h3>
                    <p class="modal-description">
                      {{ subtitle }}
                    </p>
                </div>

                <!-- Bouton d'action -->
                <div class="modal-footer">
                  <mainButton @click="$emit('handleEvent')" :label="actionText"/>
                </div>

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
    modaleTitle?: string,
    title?: string,
    subtitle?: string,
    actionText?: string
  }>(),
  {
    isOpen: false,
    modaleTitle: 'Erreur',
    title:'Accès refusé',
    subtitle: 'Une erreur est survenue.',
    actionText: 'Compris'
  }
);

const emit = defineEmits(['close','handleEvent']);

const closeModal = () => {
  emit('close');
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
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.42); /* Fond semi-transparent */
}

/* --- Structure de la carte --- */
.modal-card {
    background: #ffffff;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
    width: 100%;
    max-width: 340px;
    min-height: 40vh;
    height: auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 1.5rem;
    z-index: 101;
    text-align: center
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

/* --- Icône --- */
.icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.error-badge {
  width: 90px;
  height: 90px;
}

/* --- Typographie --- */
.modal-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.modal-title {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: #111827;
}

.modal-description {
  margin: 0;
  font-size: 0.9rem;
  color: #6b7280;
  line-height: 1.5;
}

/* --- Bouton d'action --- */
.modal-footer {
  width: 100%;
  margin-top: 0.5rem;
}
</style>

<style>
/* Transitions de la modale */
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
