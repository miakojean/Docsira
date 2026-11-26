<template>
    <section class="on-boarding">
        <div class="bg" aria-hidden="true">
            <span class="blob blob-1"></span>
            <span class="blob blob-2"></span>
        </div>

        <OnBoardingProgress
            class="progress"
            :current="step"
            :total="totalSteps"
            @select="$emit('go-to', $event)"
        />

        <div class="content">
            <div class="pic-frame animate-step" style="--step: 0">
                <img
                    src="../../../assets/assets/svg/undraw_people_ka7y.svg"
                    alt="Illustration de la gestion des clients"
                />
            </div>

            <div class="text-frame">
                <h3 class="animate-step" style="--step: 1">Gérer vos clients</h3>
                <p class="lead animate-step" style="--step: 2">
                    Ajoutez, modifiez et archivez vos clients.
                </p>

                <ul class="feature-list">
                    <li
                        v-for="(feature, i) in features"
                        :key="feature.title"
                        class="feature-item animate-step"
                        :style="{ '--step': i + 3 }"
                    >
                        <span class="feature-icon" aria-hidden="true">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path v-for="d in feature.paths" :key="d" :d="d" />
                            </svg>
                        </span>
                        <div>
                            <h4>{{ feature.title }}</h4>
                            <p>{{ feature.text }}</p>
                        </div>
                    </li>
                </ul>
            </div>
        </div>

        <div class="footer">
            <button
                class="btn-continue animate-step"
                style="--step: 7"
                @click="$emit('continue')"
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
import OnBoardingProgress from './OnBoardingProgress.vue';

export default {
  name: 'OnBoarding',
  components: { OnBoardingProgress },
  props: {
    step: { type: Number, default: 1 },
    totalSteps: { type: Number, default: 4 }
  },
  emits: ['continue', 'go-to'],
  data() {
    return {
      features: [
        {
          title: 'Ajouter un client',
          text: 'Enregistrez un nouveau client en quelques secondes.',
          paths: ['M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2', 'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8', 'M19 8v6', 'M22 11h-6']
        },
        {
          title: 'Modifier ses informations',
          text: 'Mettez à jour un nom, un contact ou une adresse.',
          paths: ['M12 20h9', 'M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z']
        },
        {
          title: 'Retrouver un client',
          text: 'Recherchez par nom ou par numéro de téléphone.',
          paths: ['M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16', 'm21 21-4.3-4.3']
        },
        {
          title: 'Archiver un client',
          text: 'Masquez les clients inactifs sans perdre leur historique.',
          paths: ['M21 8v13H3V8', 'M1 3h22v5H1Z', 'M10 12h4']
        }
      ]
    }
  }
}
</script>

<style scoped>
.on-boarding {
  --stagger-delay: 120ms; /* Écart de temps entre chaque élément */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
  height: 100%;
  width: 100%;
  position: relative;
  isolation: isolate;
  background: var(--adn-white-color);
  padding: 2rem;
  box-sizing: border-box;
  overflow: hidden;
}

/* Tout le contenu passe au-dessus du fond */
.on-boarding > *:not(.bg) {
  position: relative;
  z-index: 1;
}

/* ---------- Fond animé ---------- */
.bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
  background: linear-gradient(160deg, #ffffff 0%, var(--adn-white-color) 100%);
}

.blob {
  position: absolute;
  width: 38vmax;
  height: 38vmax;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  will-change: transform;
}

/* Bleu : coin haut gauche */
.blob-1 {
  top: -16vmax;
  left: -16vmax;
  background: var(--primary-color);
  animation: driftBlue 18s ease-in-out infinite alternate;
}

/* Vert : coin bas droit */
.blob-2 {
  bottom: -16vmax;
  right: -16vmax;
  background: var(--secondary-color);
  opacity: 0.35;
  animation: driftGreen 22s ease-in-out infinite alternate;
}

/* Léger mouvement, les taches restent dans leur coin */
@keyframes driftBlue {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(4vmax, 3vmax) scale(1.12); }
}

@keyframes driftGreen {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(-4vmax, -3vmax) scale(1.12); }
}

.progress {
  flex-shrink: 0;
}

/* Image à gauche, liste à droite */
.content {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr);
  align-items: center;
  gap: 3rem;
  min-height: 0;
}

.pic-frame {
  display: flex;
  justify-content: center;
  align-items: center;
}

.pic-frame img {
  width: 100%;
  max-width: 420px;
  height: auto;
}

.text-frame {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.text-frame h3 {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.02em;
}

.text-frame .lead {
  font-size: 1.15rem;
  font-weight: 500;
  color: var(--primary-black-color);
  margin: 0 0 1.5rem 0;
}

/* Liste séparée par de fines lignes plutôt que des cartes */
.feature-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.9rem 0;
  border-top: 1px solid #e3e5ea;
}

.feature-item:last-child {
  border-bottom: 1px solid #e3e5ea;
}

.feature-icon {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(12, 48, 108, 0.08);
  color: var(--primary-color);
}

.feature-item h4 {
  margin: 0 0 0.15rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary-black-color);
}

.feature-item p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
  color: #5b6270;
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
  transition: background-color 0.2s ease;
}

.btn-continue svg {
  transition: transform 0.2s ease;
}

.btn-continue:hover {
  background-color: #16428b;
  animation-play-state: paused; /* stoppe le flottement au survol */
}

.btn-continue:hover svg {
  transform: translateX(3px);
}

.btn-continue:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 3px;
}

.btn-continue.animate-step {
  animation:
    fadeSlideUp 0.65s cubic-bezier(0.22, 1, 0.36, 1) calc(var(--step, 5) * var(--stagger-delay)) forwards,
    floatIdle 2.5s ease-in-out calc(var(--step, 5) * var(--stagger-delay) + 0.65s) infinite;
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

/* Mobile : on empile l'image au-dessus de la liste */
@media (max-width: 768px) {
  .on-boarding { padding: 1.25rem; overflow-y: auto; }
  .content { grid-template-columns: 1fr; gap: 1.5rem; }
  .pic-frame img { max-width: 220px; }
  .text-frame h3 { font-size: 1.75rem; }
}

@media (prefers-reduced-motion: reduce) {
  .blob { animation: none; }
  .animate-step,
  .btn-continue.animate-step {
    animation: none;
    opacity: 1;
  }
}
</style>