<template>
  <div
    class="card"
    ref="cardRef"
    :class="{ 'card--active': isOpen }"
    @click="handleCardClick"
  >
    <!-- En-tête -->
    <div class="card__header">
      <div class="card__header-left">
        <span class="card__badge" :class="statusClass">
          {{ displayBadge }}
        </span>
        <span v-if="displayRef" class="card__ref">
          {{ displayRef }}
        </span>
      </div>

      <button
        type="button"
        class="card__menu-trigger"
        aria-label="Actions du dossier"
        @click.stop="toggleMenu"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="size-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z"
          />
        </svg>
      </button>
    </div>

    <!-- Corps -->
    <div class="card__body">
      <template v-if="dossier">
        <h4 class="card__title" :title="displayTitle">{{ displayTitle }}</h4>
        <p class="card__client">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="client-icon"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"
            />
          </svg>
          <span class="client-name">{{ displayClient }}</span>
        </p>
      </template>
      <p v-else class="card__text">
        {{ content }}
      </p>
    </div>

    <!-- Métadonnées additionnelles pour le dossier -->
    <div v-if="dossier && (displayType || formattedDate)" class="card__meta">
      <span v-if="displayType" class="card__meta-type">{{ displayType }}</span>
      <span v-if="formattedDate" class="card__meta-date">{{ formattedDate }}</span>
    </div>

    <!-- Pied de page -->
    <div class="card__footer">
      <div class="icons">
        <span class="footer__content">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25M9 16.5v.75m3-3v3M15 12v5.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
        </span>
        <span class="footer__content">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25M9 16.5v.75m3-3v3M15 12v5.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
        </span>
      </div>

      <div class="info">
        <p>{{ displayFilesCount }} fichier(s)</p>

        <div class="progress-ring" :title="effectiveProgress + '% complété'">
          <svg width="36" height="36" viewBox="0 0 36 36">
            <circle
              class="progress-ring__track"
              stroke-width="3"
              fill="transparent"
              :r="radius"
              cx="18"
              cy="18"
            />
            <circle
              class="progress-ring__circle"
              stroke-width="3"
              fill="transparent"
              :r="radius"
              cx="18"
              cy="18"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="progressOffset"
            />
          </svg>
          <span class="progress-ring__text">{{ effectiveProgress }}%</span>
        </div>
      </div>
    </div>

    <!-- Overlay pour fermer le menu -->
    <Teleport to="body">
      <transition name="fade">
        <div
          v-if="isOpen"
          class="overlay"
          @click.stop="isOpen = false"
        ></div>
      </transition>
    </Teleport>

    <!-- Dropbox (Menu déroulant d'actions) -->
    <transition :name="menuPositionX === 'right' ? 'slide-right' : 'slide-left'">
      <div
        v-if="isOpen"
        class="dropbox"
        :class="['dropbox--' + menuPositionX]"
        @click.stop
      >
        <ul>
          <li @click="onAction('goTo')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
            <span>Ouvrir</span>
          </li>
          <li @click="onAction('open')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75" />
            </svg>
            <span>Détails</span>
          </li>
          <li @click="onAction('edit')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
            </svg>
            <span>Modifier</span>
          </li>
          <li @click="onAction('share')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0 0a2.25 2.25 0 1 0 3.935 2.186 2.25 2.25 0 0 0-3.935-2.186Zm0-12.814a2.25 2.25 0 1 0 3.933-2.185 2.25 2.25 0 0 0-3.933 2.185Z" />
            </svg>
            <span>Partager</span>
          </li>
          <li @click="onAction('link')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" />
            </svg>
            <span>Créer un lien</span>
          </li>
          <li @click="onAction('download')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            <span>Télécharger</span>
          </li>
          <li @click="onAction('archive')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z" />
            </svg>
            <span>Archiver</span>
          </li>
          <li class="danger" @click="onAction('delete')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
            <span>Supprimer</span>
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Dossier } from '../../stores/dossierStore';

const props = withDefaults(
  defineProps<{
    dossier?: Dossier | null;
    title?: string;
    content?: string;
    progress?: number;
    filesCount?: number;
  }>(),
  {
    dossier: null,
    title: 'Dossier',
    content: 'Lorem ipsum, dolor sit amet consectetur adipisicing elit. Harum cum eligendi.',
    progress: undefined,
    filesCount: undefined,
  }
);

const emit = defineEmits([
  'goTo',
  'open',
  'details',
  'edit',
  'rename',
  'share',
  'link',
  'download',
  'archive',
  'delete',
]);

const isOpen = ref<boolean>(false);
const cardRef = ref<HTMLElement | null>(null);

const menuPositionX = ref<'left' | 'right' | 'inner-right'>('right');

const statutLabels: Record<string, string> = {
  NOUVEAU: 'Nouveau',
  EN_COURS: 'En cours',
  EN_ATTENTE: 'En attente',
  BLOQUE: 'Bloqué',
  TERMINE: 'Terminé',
  CLOTURE: 'Clôturé',
  ANNULE: 'Annulé',
};

const typeLabels: Record<string, string> = {
  CONSTITUTION: 'Constitution',
  MODIFICATION: 'Modification',
  DISSOLUTION: 'Dissolution',
  CONTENTIEUX: 'Contentieux',
  CONSEIL: 'Conseil',
  CONTRAT: 'Contrat',
  AUDIT: 'Audit',
  PROPRIETE_INTELLECTUELLE: 'Propriété intellectuelle',
  FUSION_ACQUISITION: 'Fusion/Acquisition',
  RECOUVREMENT: 'Recouvrement',
  AUTRE: 'Autre',
};

const displayBadge = computed(() => {
  if (props.dossier?.statut) {
    return statutLabels[props.dossier.statut] || props.dossier.statut;
  }
  return props.title;
});

const statusClass = computed(() => {
  return props.dossier?.statut?.toLowerCase() || '';
});

const displayRef = computed(() => {
  return props.dossier?.reference_affair || '';
});

const displayTitle = computed(() => {
  return props.dossier?.title || props.content;
});

const displayClient = computed(() => {
  if (!props.dossier) return '';
  return props.dossier.client?.nom_complet || 'Aucun client';
});

const displayType = computed(() => {
  if (!props.dossier?.type_affair) return '';
  return typeLabels[props.dossier.type_affair] || props.dossier.type_affair;
});

const formattedDate = computed(() => {
  if (!props.dossier?.creation_date) return '';
  return new Date(props.dossier.creation_date).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
});

const displayFilesCount = computed(() => {
  if (props.filesCount !== undefined) return props.filesCount;
  if (props.dossier) return props.dossier.documents_count ?? 0;
  return 2;
});

const effectiveProgress = computed(() => {
  if (props.progress !== undefined) {
    return Math.max(0, Math.min(100, props.progress));
  }
  if (props.dossier) {
    switch (props.dossier.statut) {
      case 'TERMINE':
      case 'CLOTURE':
        return 100;
      case 'EN_COURS':
        return 60;
      case 'EN_ATTENTE':
        return 35;
      case 'NOUVEAU':
        return 15;
      case 'BLOQUE':
      case 'ANNULE':
        return 0;
      default:
        return 40;
    }
  }
  return 35;
});

// Anneau de progression
const radius = 15;
const circumference = 2 * Math.PI * radius;
const progressOffset = computed(() => {
  return circumference - (effectiveProgress.value / 100) * circumference;
});

function toggleMenu() {
  isOpen.value = !isOpen.value;

  if (isOpen.value && cardRef.value) {
    const rect = cardRef.value.getBoundingClientRect();
    const spaceOnRight = window.innerWidth - rect.right;

    if (spaceOnRight < 210 && rect.left < 210) {
      menuPositionX.value = 'inner-right';
    } else if (spaceOnRight < 210) {
      menuPositionX.value = 'left';
    } else {
      menuPositionX.value = 'right';
    }
  }
}

function handleCardClick() {
  if (isOpen.value) return;
  emit('goTo', props.dossier ?? null);
}

type CardAction =
  | 'goTo'
  | 'open'
  | 'details'
  | 'edit'
  | 'rename'
  | 'share'
  | 'link'
  | 'download'
  | 'archive'
  | 'delete';

function onAction(action: CardAction) {
  isOpen.value = false;
  const payload = props.dossier ?? null;
  if (action === 'edit') {
    emit('edit', payload);
    emit('rename', payload);
  } else {
    emit(action, payload);
  }
}
</script>

<style scoped>
.card {
  width: 100%;
  padding: 1.5rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #ffffff;
  border-radius: 16px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  position: relative;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.09);
}

.card--active {
  z-index: 50;
  position: relative;
}

/* --- Header --- */
.card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}

.card__header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  min-width: 0;
}

.card__badge {
  padding: 0.35rem 0.85rem;
  background: var(--primary-color, #2563eb);
  color: #ffffff;
  border: none;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.3px;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}

.card__badge.nouveau {
  background: #dbeafe;
  color: #1e40af;
}

.card__badge.en_cours {
  background: #dcfce7;
  color: #166534;
}

.card__badge.en_attente {
  background: #fef3c7;
  color: #92400e;
}

.card__badge.bloque {
  background: #fee2e2;
  color: #991b1b;
}

.card__badge.termine {
  background: #e0e7ff;
  color: #3730a3;
}

.card__badge.cloture {
  background: #f3f4f6;
  color: #4b5563;
}

.card__badge.annule {
  background: #fee2e2;
  color: #991b1b;
}

.card__ref {
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 500;
  white-space: nowrap;
}

.card__menu-trigger {
  background: none;
  border: none;
  color: #9ca3af;
  padding: 0.25rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.card__menu-trigger:hover {
  background: #f3f4f6;
  color: #111827;
}

/* --- Body --- */
.card__body {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-height: 52px;
}

.card__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #111827;
  line-height: 1.35;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card__client {
  margin: 0;
  font-size: 0.85rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
}

.client-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.client-icon {
  width: 0.95rem;
  height: 0.95rem;
  color: #9ca3af;
  flex-shrink: 0;
}

.card__text {
  margin: 0;
  color: #4b5563;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* --- Meta --- */
.card__meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: #9ca3af;
  padding-top: 0.35rem;
  border-top: 1px dashed #f3f4f6;
}

.card__meta-type {
  font-weight: 500;
  color: #6b7280;
}

.card__meta-date {
  color: #9ca3af;
}

/* --- Footer --- */
.card__footer {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 0.25rem;
}

.icons {
  display: flex;
  align-items: center;
}

.card__footer .footer__content {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.4rem;
  background: var(--primary-color, #2563eb);
  width: 36px;
  height: 36px;
  border-radius: 999px;
  flex-shrink: 0;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  position: relative;
  transition: transform 0.2s ease;
}

.card__footer .footer__content + .footer__content {
  margin-left: -14px;
}

.card__footer .footer__content:hover {
  transform: scale(1.1);
  z-index: 10;
}

.card__footer .footer__content svg {
  width: 18px;
  height: 18px;
  color: #ffffff;
  stroke: #ffffff;
}

.card__footer p {
  color: #7d8796;
  font-size: 0.8rem;
  font-weight: 500;
  margin: 0;
}

/* --- Anneau de progression --- */
.info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-ring {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.progress-ring svg {
  transform: rotate(-90deg);
}

.progress-ring__track {
  stroke: #e5e7eb;
}

.progress-ring__circle {
  stroke: var(--primary-color, #2563eb);
  stroke-linecap: round;
  transition: stroke-dashoffset 0.5s ease-in-out;
}

.progress-ring__text {
  position: absolute;
  font-size: 0.6rem;
  font-weight: 700;
  color: #4b5563;
}

/* --- Dropbox --- */
.dropbox {
  position: absolute;
  top: 5px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  border: 1px solid #f3f4f6;
  min-width: 180px;
  max-height: calc(100vh - 80px);
  overflow-y: auto;
  z-index: 55;
  padding: 0.4rem;
}

.dropbox--right {
  left: calc(100% + 10px);
  right: auto;
  top: 5px;
  transform-origin: top left;
}

.dropbox--left {
  right: calc(100% + 10px);
  left: auto;
  top: 5px;
  transform-origin: top right;
}

.dropbox--inner-right {
  right: 12px;
  left: auto;
  top: 3.25rem;
  transform-origin: top right;
}

.dropbox ul {
  list-style: none;
  margin: 0;
  padding: 0.2rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.dropbox li {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.55rem 0.75rem;
  font-size: 0.85rem;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
  border-radius: 0.5rem;
}

.dropbox li:hover {
  background-color: #f3f4f6;
  color: var(--primary-color, #2563eb);
}

.dropbox li.danger {
  color: #dc2626;
}

.dropbox li.danger:hover {
  background-color: #fef2f2;
  color: #b91c1c;
}

/* --- Animations --- */
.slide-right-enter-active,
.slide-right-leave-active,
.slide-left-enter-active,
.slide-left-leave-active {
  transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-right-enter-from,
.slide-right-leave-to {
  opacity: 0;
  transform: translateX(-15px) scale(0.95);
}

.slide-left-enter-from,
.slide-left-leave-to {
  opacity: 0;
  transform: translateX(15px) scale(0.95);
}

/* --- Overlay --- */
:global(.overlay) {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(17, 24, 39, 0.25);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 40;
  cursor: default;
}

:global(.fade-enter-active),
:global(.fade-leave-active) {
  transition: opacity 0.3s ease;
}

:global(.fade-enter-from),
:global(.fade-leave-to) {
  opacity: 0;
}
</style>
