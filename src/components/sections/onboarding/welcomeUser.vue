<template>
  <section class="on-boarding">
    <div class="text-frame">
      <h1 class="animate-step" style="--step: 0">Bienvenue dans Docsira</h1>
      <p class="animate-step" style="--step: 1">Votre logiciel de gestion de cabinet,</p>

      <div class="card-features w-full flex justify-center items-center gap-4">
        <featuresCard
          class="animate-step feature-item"
          style="--step: 2"
          title="Espace collaboratif"
          content="Partagez et collaborez sur vos documents en temps réel, avec des permissions personnalisables."
          icon="user"
        />
        <featuresCard
          class="animate-step feature-item"
          style="--step: 3"
          title="Espace personnel"
          content="Organisez vos documents et dossiers personnels de manière sécurisée et accessible."
          icon="calendar"
        />
        <featuresCard
          class="animate-step feature-item"
          style="--step: 4"
          title="Gestion des archives"
          content="Conservez et archivez vos documents importants avec un accès facile et rapide."
          icon="file-text"
        />
      </div>
    </div>

    <div class="footer">
      <button
        class="btn-continue animate-step"
        style="--step: 5"
        @click="router.push('/onboarding/customer')"
      >
        Continuer
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14" />
          <path d="m12 5 7 7-7 7" />
        </svg>
      </button>
    </div>
  </section>
</template>

<script>
import mainButton from '../../buttons/mainButton.vue';
import featuresCard from '../../cards/featuresCards.vue';
import { useRouter } from 'vue-router';

export default {
  name: 'OnBoarding',
  components: {
    mainButton,
    featuresCard
  },
  emits: ['continue'],
  setup(){
    
    const router = useRouter();

    return{
        router
    }
  }
}
</script>

<style scoped>
.on-boarding {
  --stagger-delay: 160ms; /* Écart de temps entre chaque élément */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  width: 100%;
  background: radial-gradient(circle at 50% 40%, #ffffff 0%, #f5f5f5 100%);
  padding: 2rem;
  box-sizing: border-box;
  overflow: hidden;
}

.text-frame {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
}

.text-frame h1 {
  font-size: 3.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.02em;
}

.text-frame p {
  font-size: 1.5rem;
  font-weight: 500;
  color: var(--primary-black-color);
  margin: 0 0 2.5rem 0;
}

.card-features {
  margin-top: 1rem;
}

.feature-item {
  transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.25s ease;
}

.feature-item:hover {
  transform: translateY(-4px);
}

.footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0.5rem 1.25rem;
}

.btn-continue {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: var(--primary-color);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.15s ease;
}

.btn-continue:hover {
  background-color: #16428b;
}

.btn-continue:hover svg {
  transform: translateX(3px);
}

.btn-continue svg {
  transition: transform 0.2s ease;
}

.btn-continue:active {
  transform: scale(0.98);
}

.btn-continue.animate-step {
  animation:
    fadeSlideUp 0.65s cubic-bezier(0.22, 1, 0.36, 1) calc(var(--step, 5) * var(--stagger-delay)) forwards,
    floatIdle 2.5s ease-in-out calc(var(--step, 5) * var(--stagger-delay) + 0.65s) infinite;
}

/* Stoppe le flottement proprement dès que la souris survole le bouton */
.btn-continue:hover {
  background-color: #16428b;
  animation-play-state: paused;
}

@keyframes floatIdle {
  0%, 100% {
    transform: translateY(0);
    box-shadow: 0 4px 12px rgba(12, 48, 108, 0.15);
  }
  50% {
    transform: translateY(-6px);
    box-shadow: 0 10px 20px rgba(12, 48, 108, 0.25);
  }
}

/* Animation séquentielle à l'activation */
.animate-step {
  opacity: 0;
  animation: fadeSlideUp 0.65s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  animation-delay: calc(var(--step, 0) * var(--stagger-delay));
}

@keyframes fadeSlideUp {
  0% {
    opacity: 0;
    transform: translateY(24px) scale(0.98);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>