<template>
  <section class="support-section">
    <header class="support-header">
      <div class="header-copy">
        <h2 class="support-title">Support client &amp; Visites guidées</h2>
        <p class="support-subtitle">
          Lancez la visite interactive des fonctionnalités avancées ou reprenez la prise en main de DocSira à votre rythme.
        </p>
      </div>
      <div class="header-logo">
        <AnimatedBrandLogo :size="56" />
      </div>
    </header>

    <div class="tracks-grid">
      <TutorialTrackCard
        title="Fonctionnalités avancées"
        meta="8 étapes interactives · ~3 min"
        description="Pratiquez directement dans un dossier et vos réglages : suivi SIRA, import de pièce, versioning v1/v2, mentions @Document, paramètres et gestion des collaborateurs."
        :highlights="[
          'Ouverture d’un dossier du Workspace et suivi SIRA (10 % → 100 %)',
          'Import de pièce et historique de versioning (v1, v2, restauration)',
          'Commentaires d’équipe et mentions @Document',
          'Paramètres (profil & sécurité), collaborateurs, rôles et liens .zip'
        ]"
        :completed="tutorialStore.advancedCompleted"
        variant="primary"
        ctaLabel="Lancer le tutoriel avancé"
        @start="tutorialStore.startAdvancedTour()"
      />

      <TutorialTrackCard
        title="Les bases de DocSira"
        meta="6 étapes interactives · ~2 min"
        description="Revoir la prise en main guidée pas à pas : répertoire Clients, création d’un client et d’un dossier Workspace, puis découverte de Mon espace local."
        :highlights="[
          'Accès au répertoire Clients et création d’une fiche',
          'Navigation dans le Workspace collaboratif',
          'Création d’un dossier rattaché à un client',
          'Prise en main de Mon espace local hors-ligne'
        ]"
        :completed="tutorialStore.basicCompleted"
        variant="secondary"
        ctaLabel="Relancer la visite de base"
        @start="tutorialStore.startBasicTour(true)"
      />
    </div>

    <SupportFaqAccordion />
  </section>
</template>

<script setup lang="ts">
import { useTutorialStore } from '../../../stores/tutorialStore';
import AnimatedBrandLogo from '../../tutorial/AnimatedBrandLogo.vue';
import SupportFaqAccordion from './SupportFaqAccordion.vue';
import TutorialTrackCard from './TutorialTrackCard.vue';

const tutorialStore = useTutorialStore();
</script>

<style scoped>
.support-section {
  width: 100%;
  max-width: 1080px;
  margin: 0 auto;
  padding: 1.5rem 1.75rem 2.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.35rem;
}

.support-header {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.25rem;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
}

.header-copy {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.support-title {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--blues-color, #002945);
  text-align: left;
}

.support-subtitle {
  margin: 0;
  font-size: 0.86rem;
  line-height: 1.5;
  color: #64748b;
  max-width: 620px;
  text-align: left;
}

.header-logo {
  flex-shrink: 0;
}

.tracks-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.15rem;
}

@media (max-width: 820px) {
  .tracks-grid {
    grid-template-columns: 1fr;
  }

  .support-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
