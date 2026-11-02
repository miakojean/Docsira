<template>
  <div class="card">
    <div v-if="image || $slots.illustration" class="card__illustration">
      <slot name="illustration">
        <img :src="image" :alt="title" class="card__image" />
      </slot>
    </div>

    <div class="card__header">
      <button class="card__badge" type="button">
        {{ title }}
      </button>
    </div>
    
    <div class="card__body">
      <p class="card__text">
        {{ content }}
      </p>
    </div>

    <div class="card__action">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="card__arrow">
        <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    content?: string;
    image?: string;
  }>(),
  {
    title: 'Dossiers',
    content: '',
    image: '',
  }
);
</script>

<style scoped>
/* 🎨 Variables (si tu ne les as pas déjà en global) */
:root {
  --primary-color: #2563eb; /* Un beau bleu moderne */
}

.card {
    /* Largeur et respiration */
    width: 100%;
    max-width: 280px; 
    padding: 1.25rem;
    padding-bottom: 2.25rem;
    
    /* Structure */
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    
    /* Design Premium */
    background: #ffffff;
    border-radius: 18px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    
    /* Transition douce globale */
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    
    /* ⚡️ CRUCIAL : Nécessaire pour positionner l'action à l'intérieur */
    position: relative; 
    
    /* Curseur pointer si toute la carte est un lien */
    cursor: pointer;
}

/* --- Effet Hover global sur la carte --- */
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 16px 30px rgba(0, 0, 0, 0.08);
    border-color: #cbd5e1;
}

/* --- Illustration SVG --- */
.card__illustration {
    width: 100%;
    height: 125px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
    background: #f8fafc;
    border-radius: 12px;
    overflow: hidden;
    transition: background-color 0.25s ease;
}

.card:hover .card__illustration {
    background: #f1f5f9;
}

.card__image {
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
    object-fit: contain;
    transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.card:hover .card__image {
    transform: scale(1.06);
}

/* --- Stylisation des éléments existants --- */
.card__header {
    display: flex;
    align-items: center;
}

.card__badge {
    padding: 0.35rem 1rem;
    background: var(--primary-color);
    color: #ffffff;
    border: none;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.3px;
    cursor: pointer;
}

.card__body {
    flex: 1;
}

.card__text {
    margin: 0;
    color: #4b5563; /* Gris doux */
    font-size: 0.9rem;
    line-height: 1.45;
}

/* --- ⚡️ Stylisation de la NOUVELLE Action --- */

.card__action {
    /* Positionnement en bas à droite */
    position: absolute;
    bottom: 1.5rem;
    right: 1.5rem;
    
    /* Structure de l'élément rond */
    display: flex;
    justify-content: center;
    align-items: center;
    width: 38px;
    height: 38px;
    background-color: var(--primary-color);
    border-radius: 50%; /* ⚡️ C'est rond ! */
    
    /* Design de la flèche */
    color: #ffffff;
    
    /* --- État par défaut (Caché) --- */
    opacity: 0;
    
    /* Légère rotation et échelle pour l'effet d'entrée */
    transform: translate(10px, 10px) scale(0.6); 
    
    /* Transition douce sur les propriétés */
    transition: 
        opacity 0.3s ease, 
        transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), /* Effet ressort (rebound) */
        background-color 0.2s ease;
}

/* --- Effet Hover pour révéler l'action --- */
.card:hover .card__action {
    opacity: 1;
    /* Revient à sa position et échelle normale */
    transform: translate(0, 0) scale(1);
}

/* Stylisation du SVG de la flèche */
.card__arrow {
    width: 18px;
    height: 18px;
}


/* --- ⚡️ L'animation du Background (Ripple/Pulsation) --- */

/* On crée un pseudo-élément ::after pour l'effet de ripple */
.card__action::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: var(--primary-color);
    border-radius: 50%;
    
    /* L'animation est désactivée par défaut */
    opacity: 0;
}

/* On lance l'animation sur ::after uniquement quand la carte est survolée */
.card:hover .card__action::after {
    animation: pulse-ripple 1.2s infinite;
}

/* Définition de l'animation */
@keyframes pulse-ripple {
    0% {
        transform: scale(1);
        opacity: 0.6;
    }
    /* L'élément grandit et devient transparent */
    100% {
        transform: scale(1.6);
        opacity: 0;
    }
}
</style>