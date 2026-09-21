<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="300">
        <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
            <div class="modal-card" role="dialog" aria-modal="true">

                <div class="modal-header">
                    <h3 class="modal-title">Inviter un collaborateur</h3>
                    <button class="close-btn" @click="$emit('close')" aria-label="Fermer la modale">
                        &times;
                    </button>
                </div>

                <!-- Textes & Input -->
                <div class="modal-body">
                    <BaseInput
                        type="email"
                        placeholder="Adresse e-mail"
                        v-model="email"
                        :errorMessage="errorMessage"
                    />
                </div>

                <div class="error-content" v-if="backendError">
                    <p>{{backendError}}</p>
                </div>

                <!-- Bouton d'action -->
                <div class="modal-footer">
                    <mainButton
                        @click="handleInvite"
                        label="Envoyer l'invitation"
                        :disabled="isLoading"
                        :isLoading="isLoading"
                    />
                </div>

            </div>
        </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { watch, onUnmounted, ref, onMounted } from 'vue';
import BaseInput from '../BaseInput/BaseInput.vue';
import mainButton from '../buttons/mainButton.vue';

const props = defineProps({
    isOpen: {
      type: Boolean,
      default: false
    },
    errorMessage: {
      type: String,
      default: ''
    },
    backendError: {
      type: String,
      default: ''
    },
    isLoading: {
      type: Boolean,
      default: false
    }
});

const emit = defineEmits(['close', 'invite']);

const closeModal = () => {
  emit('close');
};

const email = ref<string>('');
const errorMessage = ref<string>('');


async function handleInvite() {
    if (email.value === "") {
        errorMessage.value = 'Veuillez saisir une adresse e-mail valide.';
        return;
    }
    errorMessage.value = "";
    emit('invite', email.value);
}

onMounted(() => {
  errorMessage.value = '';
})

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
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.42);
}

/* --- Structure de la carte --- */
.modal-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
    width: 100%;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    z-index: 1001;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #9ca3af;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #4b5563;
}

/* --- Typographie & Input --- */
.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-description {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
}

.email-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #374151;
  outline: none;
  transition: border-color 0.2s;
}

.email-input:focus {
  border-color: #3b82f6;
}

/* --- Bouton d'action --- */
.modal-footer {
  width: 100%;
}

.btn-invite {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  background-color: #3b82f6; /* Bleu primaire */
  color: #ffffff;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.btn-invite:hover {
  background-color: #2563eb;
}

.btn-invite:active {
  transform: scale(0.98);
}

.error-content {
  color: #ef4444;
  font-size: 0.875rem;
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
