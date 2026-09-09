<template>
  <Transition name="slide-fade">
    <div v-if="isVisible" class="notification-popup">
      
      <div class="notif-icon-container">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 0 0-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 0 0-16.536-1.84M7.5 14.25 5.106 5.272M6 20.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm12.75 0a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z" />
        </svg>
      </div>

      <div class="notif-content">
        <p class="notif-text">
          {{ actionText }} 
        </p>
      </div>

      <button class="close-btn" @click="closePopup" aria-label="Fermer">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  </Transition>
</template>

<script lang="ts">
import { ref, watch } from 'vue';

export default {
    name: 'NotificationPopup',
    props:{
        visible: {
          type: Boolean,
          default: false
        },
        userName: {
          type: String,
          default: 'Olamina'
        },
        actionText: {
          type: String,
          default: 'Un article ajouté au panier'
        },
        duration: {
          type: Number,
          default: 2000
        }
    },

    emits: ['close'],
    setup(props, {emit}){
      const isVisible = ref(props.visible);
      let closeTimer: ReturnType<typeof setTimeout> | null = null;

      const closePopup = () => {
        if (closeTimer) {
          clearTimeout(closeTimer);
          closeTimer = null;
        }

        isVisible.value = false;
        emit('close');
      };

      watch(
        () => props.visible,
        (value) => {
          isVisible.value = value;

          if (!value) {
            if (closeTimer) {
              clearTimeout(closeTimer);
              closeTimer = null;
            }
            return;
          }

          if (closeTimer) {
            clearTimeout(closeTimer);
          }

          if (props.duration > 0) {
            closeTimer = setTimeout(() => {
              closePopup();
            }, props.duration);
          }
        },
        { immediate: true }
      );

      return {
        isVisible,
        closePopup
      }
    }
}

// On définit les propriétés pour pouvoir afficher des messages dynamiques



</script>

<style scoped>
/* Conteneur principal de la popup */
.notification-popup {
  position: fixed;
  top: 24px;
  right: 24px;
  width: 380px;
  max-width: calc(100vw - 48px);
  background-color: #f4f8f7; /* Vert foncé de ton image */
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  font-family: sans-serif;
}

/* Conteneur de l'icône */
.notif-icon-container {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: none;
  border: 1px solid #111827;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-left: 8px; /* Espace pour le point bleu */
}

/* Textes */
.notif-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.notif-text {
  font-size: 14px;
  color: #111827;
  margin: 0;
  line-height: 1.4;
}

.notif-text strong {
  font-weight: 600;
  color: #FFFFFF;
}

.notif-time {
  font-size: 12px;
  color: #9CA3AF;
}

/* Bouton fermer (la petite croix) */
.close-btn {
  background: none;
  border: none;
  color: #9CA3AF;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #FFFFFF;
  background-color: #111827;
}

/* Animations d'apparition et disparition */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.4s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(50px);
  opacity: 0;
}

/* Animation de l'icône (effet cloche avec rebond) */
@keyframes ring-bounce {
  0% { transform: scale(0.8) rotate(0); }
  20% { transform: scale(1.1) rotate(-15deg); }
  40% { transform: scale(1.1) rotate(15deg); }
  60% { transform: scale(1) rotate(-10deg); }
  80% { transform: scale(1) rotate(5deg); }
  100% { transform: scale(1) rotate(0); }
}

.notif-icon-container svg {
  /* Le point de pivot en haut donne un mouvement naturel de balancier */
  transform-origin: top center; 
  /* Le délai de 0.1s permet à la popup d'entrer avant que l'icône ne s'anime */
  animation: ring-bounce 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) 0.1s both;
}
</style>