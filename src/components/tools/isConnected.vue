<template>
  <Transition name="slide-fade">
    <div v-if="isVisible" class="notification-popup">
      
      <div class="notif-icon-container" :class="{ 'is-online': isOnline }">
        <svg v-if="!isOnline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="m3 3 8.735 8.735m0 0a.374.374 0 1 1 .53.53m-.53-.53.53.53m0 0L21 21M14.652 9.348a3.75 3.75 0 0 1 0 5.304m2.121-7.425a6.75 6.75 0 0 1 0 9.546m2.121-11.667c3.808 3.807 3.808 9.98 0 13.788m-9.546-4.242a3.733 3.733 0 0 1-1.06-2.122m-1.061 4.243a6.75 6.75 0 0 1-1.625-6.929m-.496 9.05c-3.068-3.067-3.664-7.67-1.79-11.334M12 12h.008v.008H12V12Z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.288 15.038a5.25 5.25 0 0 1 7.424 0M5.106 11.856c3.807-3.808 9.98-3.808 13.788 0M1.924 8.674c5.565-5.565 14.587-5.565 20.152 0M12.53 18.22l-.53.53-.53-.53a.75.75 0 0 1 1.06 0Z" />
        </svg>
      </div>

      <div class="notif-content">
        <p class="notif-text" :class="{ 'is-online': isOnline }">
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
          default: 'Vous n\'êtes pas connecté à internet.'
        },
        isOnline: {
          type: Boolean,
          default: false
        },
        duration: {
          type: Number,
          default: 10000
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
  bottom: 24px;
  left: 24px;
  width: 320px;
  max-width: calc(100vw - 48px);
  background-color: #f8f2f2; /* Vert foncé de ton image */
  border-radius: 8px;
  padding: 8px;
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
  color: #f30707;
  margin: 0;
  line-height: 1.4;
}

.notif-text.is-online {
  color: #10B981;
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
  background-color: #f30707;
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
  color: #f30707;
}

.notif-icon-container.is-online svg {
  color: #10B981;
}
</style>