<template>
  <form class="form-ui otp-form" @submit.prevent="submitOtp">
    <h3>Vérification de sécurité</h3>
    <p class="subtitle">
      Nous vous avons envoyé un code à 6 caractères. Veuillez l'entrer ci-dessous.
    </p>

    <!-- Conteneur des 6 cases OTP -->
    <div class="otp-container" @paste="handlePaste">
        <input
            v-for="(_, index) in otp"
            :key="index"
            ref="otpInputs"
            type="text"
            inputmode="text"
            maxlength="1"
            v-model="otp[index]"
            @input="handleInput(index, $event)"
            @keydown="handleKeydown(index, $event)"
            class="otp-input"
        />
    </div>

    <!-- Composant d'erreur (réutilisé de ton projet) -->
    <errorMessage :label="errorMessageState" v-if="errorMessageState" />

    <!-- Bouton principal (réutilisé de ton projet) -->
    <mainButton type="submit" label="Vérifier le code" :isLoading="isLoading" />

    <div class="divider-form"></div>

    <div class="resend-section">
        <p>Vous n'avez pas reçu le code ?</p>
        <button type="button" class="resend-btn" @click="resendOtp">
            Renvoyer le code
        </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import mainButton from '../buttons/mainButton.vue';
import errorMessage from '../tools/errorMessage.vue';

// On définit les événements pour communiquer avec le parent (la page de login/auth)
const emit = defineEmits(['verify', 'resend']);

const props = defineProps<{
  isLoading?: boolean;
}>();

// Tableau réactif pour stocker les 6 chiffres
const otp = ref<string[]>(['', '', '', '', '', '']);
const errorMessageState = ref<string>("");

// Référence vers les éléments DOM des inputs pour gérer le focus
const otpInputs = ref<HTMLInputElement[]>([]);

// 1. Gère la saisie d'un caractère
const handleInput = (index: number, event: Event) => {
  const input = event.target as HTMLInputElement;

  // Accepte les chiffres et les lettres
  otp.value[index] = input.value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();

  // Passe au champ suivant si un chiffre est entré
  if (otp.value[index] !== '' && index < 5) {
    nextTick(() => {
      otpInputs.value[index + 1]?.focus();
    });
  }
};

// 2. Gère la touche Retour (Backspace) pour reculer
const handleKeydown = (index: number, event: KeyboardEvent) => {
  if (event.key === 'Backspace' && otp.value[index] === '' && index > 0) {
    // Si la case est vide et qu'on efface, on retourne à la case précédente
    nextTick(() => {
      otpInputs.value[index - 1]?.focus();
    });
  }
};

// 3. Gère le Copier-Coller global
const handlePaste = (event: ClipboardEvent) => {
  event.preventDefault();
  const pasteData = event.clipboardData?.getData('text');

  if (pasteData) {
    // Garde uniquement les lettres et chiffres et coupe à 6 caractères max
    const cleanData = pasteData.replace(/[^a-zA-Z0-9]/g, '').toUpperCase().slice(0, 6);

    // Répartit les chiffres dans le tableau
    for (let i = 0; i < cleanData.length; i++) {
      otp.value[i] = cleanData[i];
    }

    // Focus sur la case qui suit le dernier chiffre collé
    const nextIndex = Math.min(cleanData.length, 5);
    nextTick(() => {
      otpInputs.value[nextIndex]?.focus();
    });
  }
};

// 4. Soumission du formulaire
const submitOtp = () => {
  const code = otp.value.join(''); // Assemble les 6 chiffres

  if (code.length === 6) {
    errorMessageState.value = "";
    emit('verify', code); // Envoie le code au parent pour l'appel API
  } else {
    errorMessageState.value = "Veuillez entrer les 6 chiffres du code.";
  }
};

// 5. Demande de renvoi
const resendOtp = () => {
  // Ici on pourrait vider les cases : otp.value = ['', '', '', '', '', '']
  emit('resend');
};
</script>

<style scoped>
/* --- Styles globaux du formulaire --- */
form h3 {
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  text-align: center;
}

.subtitle {
  color: #6b7280;
  font-size: 0.95rem;
  text-align: center;
  margin-bottom: 2rem;
  line-height: 1.4;
}

/* --- Conteneur OTP --- */
.otp-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  width: 100%;
}

.otp-input {
  width: 3rem;
  height: 3.5rem;
  text-align: center;
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  background-color: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 12px; /* Coins arrondis façon iOS */
  transition: all 0.2s ease;
  outline: none;
}

/* Effet au focus et au survol */
.otp-input:focus {
  border-color: var(--primary-color);
  background-color: #ffffff;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.otp-input:hover:not(:focus) {
  border-color: #9ca3af;
}

.divider-form {
  width: 100%;
  height: 1px;
  background-color: #f3f4f6;
  margin: 1.5rem 0;
}

/* --- Section de renvoi --- */
.resend-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.resend-section p {
  color: #9ca3af;
  font-size: 0.9rem;
  margin: 0;
}

.resend-btn {
  background: none;
  border: none;
  color: #111827;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  text-decoration: underline;
  text-decoration-color: transparent;
  transition: text-decoration-color 0.2s ease;
}

.resend-btn:hover {
  text-decoration-color: #111827;
}
</style>
