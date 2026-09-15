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

                <!-- Icône de succès (Macaron ondulé) -->
                <div class="icon-container">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="success-badge">
                    <!-- Fond vert ondulé -->
                    <path d="M12 2L14.8 4.2L18.2 3.8L19.4 7.1L22.4 8.7L21 12L22.4 15.3L19.4 16.9L18.2 20.2L14.8 19.8L12 22L9.2 19.8L5.8 20.2L4.6 16.9L1.6 15.3L3 12L1.6 8.7L4.6 7.1L5.8 3.8L9.2 4.2L12 2Z" fill="#dcfce7"/>
                    <!-- Checkmark noir -->
                    <path d="M8 12.5L10.5 15L16 9" stroke="#111827" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>

                <!-- Textes -->
                <div class="modal-body">
                    <h3 class="modal-title">Inscription réussie</h3>
                    <p class="modal-description">
                    Votre compte Docsira a été créé avec succès.<br>
                    Vous pouvez maintenant vous connecter.
                    </p>
                </div>

                <!-- Bouton d'action -->
                <div class="modal-footer">
                  <mainButton @click="$emit('handleEvent')"/>
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
    modaleTitle: string
  }>(),
  {
    isOpen: true,
    modaleTitle: 'Félicitations'
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

/* --- Icône --- */
.icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.success-badge {
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

.btn-done {
  width: 100%;
  padding: 0.8rem 1rem;
  border-radius: 12px; /* Bords arrondis pour le bouton */
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  border: none;
  background-color: #1f2937; /* Gris très sombre / Noir */
  color: #ffffff;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.btn-done:hover {
  background-color: #111827;
}

.btn-done:active {
  transform: scale(0.98);
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
