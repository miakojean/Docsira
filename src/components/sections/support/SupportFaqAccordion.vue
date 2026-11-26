<template>
  <div class="faq-box">
    <h4 class="faq-heading">Questions fréquentes</h4>
    <div class="faq-list">
      <div
        v-for="(item, idx) in FAQ_ITEMS"
        :key="idx"
        class="faq-item"
        :class="{ 'is-open': openIndex === idx }"
      >
        <button
          type="button"
          class="faq-trigger"
          :aria-expanded="openIndex === idx"
          @click="toggle(idx)"
        >
          <span>{{ item.question }}</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
            class="faq-chevron"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
          </svg>
        </button>

        <p v-if="openIndex === idx" class="faq-answer">
          {{ item.answer }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface FaqItem {
  question: string;
  answer: string;
}

const FAQ_ITEMS: FaqItem[] = [
  {
    question: 'Comment fonctionne la progression SIRA dans un dossier ?',
    answer:
      "La progression passe de 10 % à 100 % automatiquement selon les catégories des pièces ajoutées (Identification : 45 %, Constitution : 60 %, Procédures : 75 %, Livrables : 90 %, Clôture : 100 %). Chaque action alimente le journal de traçabilité dans l'onglet SIRA.",
  },
  {
    question: 'Comment ajouter une nouvelle version d’un document ?',
    answer:
      'Ouvrez un document en aperçu puis cliquez sur « Nouvelle version », ou ouvrez le menu Actions > Versions sur la carte du fichier. Vous pouvez aussi restaurer une version antérieure à tout moment.',
  },
  {
    question: 'Comment citer un document précis dans les commentaires ?',
    answer:
      'Ouvrez le panneau Commentaires à droite d’un dossier et tapez @ (ou cliquez sur @ Document). Sélectionnez le document voulu : un badge cliquable sera inséré dans votre message pour que vos collaborateurs puissent l’ouvrir directement.',
  },
  {
    question: 'Quelle différence entre Administrateur, Collaborateur et Lecteur ?',
    answer:
      'L’Administrateur gère l’équipe et les suppressions définitives ; le Collaborateur (rôle par défaut) crée et modifie dossiers et documents ; le Lecteur consulte les dossiers/archives et peut laisser des commentaires sans modifier les fichiers.',
  },
  {
    question: 'Quelle différence entre Mon espace et le Workspace ?',
    answer:
      'Mon espace affiche vos dossiers locaux sur votre ordinateur (utilisables hors-ligne). Le Workspace contient les dossiers d’affaires partagés en ligne avec votre cabinet. Vous pouvez envoyer un fichier de Mon espace vers le Workspace à tout moment.',
  },
];

const openIndex = ref<number | null>(0);

function toggle(idx: number) {
  openIndex.value = openIndex.value === idx ? null : idx;
}
</script>

<style scoped>
.faq-box {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 1.35rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.faq-heading {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--blues-color, #002945);
  text-align: left;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.faq-item {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.15s ease;
}

.faq-item.is-open {
  border-color: #bfdbfe;
  background: #f8fbff;
}

.faq-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.8rem 1rem;
  border: none;
  border-radius: 0;
  background: transparent;
  color: #0f172a;
  font-size: 0.88rem;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
}

.faq-chevron {
  width: 16px;
  height: 16px;
  color: #64748b;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.faq-item.is-open .faq-chevron {
  transform: rotate(180deg);
  color: var(--primary-color, #005792);
}

.faq-answer {
  margin: 0;
  padding: 0 1rem 0.9rem;
  font-size: 0.84rem;
  line-height: 1.55;
  color: #475569;
}
</style>

