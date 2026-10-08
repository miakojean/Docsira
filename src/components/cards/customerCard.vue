<template>
  <div class="customer-card" ref="cardRef" :class="{ 'card--active': isOpen }">
    <div class="card-header">
      <span class="role">{{ client.type_client === 'PERSONNE_MORALE' ? 'Personne morale' : 'Personne physique' }}</span>
      <div class="header-right">
        <span class="time-container">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="clock-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          {{ formatDate(client.date_creation) }}
        </span>
        <button class="menu-trigger" @click.stop="toggleMenu">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
          </svg>
        </button>
      </div>
    </div>
    
    <div class="card-body">
      <div class="avatar-container">
        <!-- Vous pouvez remplacer par une image si client.avatar existe -->
        <div class="avatar-fallback">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6" v-if  ="client.type_client === 'PERSONNE_PHYSIQUE'" >
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
          </svg>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6" v-else >
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 21v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21m0 0h4.5V3.545M12.75 21h7.5V10.75M2.25 21h1.5m18 0h-18M2.25 9l4.5-1.636M18.75 3l-1.5.545m0 6.205 3 1m1.5.5-1.5-.5M6.75 7.364V3h-3v18m3-13.636 10.5-3.819" />
          </svg>
        </div>
      </div>
      <div class="info">
        <h3 class="name">{{ client.nom_complet }}</h3>
        <p class="email">{{ client.email }}</p>
        <p class="email">{{ client.reference_client }}</p>
      </div>
    </div>
    
    <div class="card-actions">
      <button class="primary-btn">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 0 0-1.883 2.542l.857 6a2.25 2.25 0 0 0 2.227 1.932H19.05a2.25 2.25 0 0 0 2.227-1.932l.857-6a2.25 2.25 0 0 0-1.883-2.542m-16.5 0V6A2.25 2.25 0 0 1 6 3.75h3.879a1.5 1.5 0 0 1 1.06.44l2.122 2.12a1.5 1.5 0 0 0 1.06.44H18A2.25 2.25 0 0 1 20.25 9v.776" />
        </svg>
        Voir dossier
      </button>
      <button class="secondary-btn" @click.stop="$emit('view', client)">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
        </svg>
        
      </button>
    </div>

    <Teleport to="body">
      <transition name="fade">
        <div v-if="isOpen" class="overlay" @click="isOpen = false"></div>
      </transition>
    </Teleport>

    <transition :name="menuPositionX === 'right' ? 'slide-right' : 'slide-left'">
      <div v-if="isOpen" class="dropbox" :class="['dropbox--' + menuPositionX, 'dropbox--' + menuPositionY]">
        <ul>
          <li @click.stop="() => { isOpen = false; $emit('view', client) }">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
             Voir
          </li>
          <li @click.stop="() => { isOpen = false; $emit('edit', client) }">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" /></svg>
             Modifier
          </li>
          <li @click.stop="() => { isOpen = false; $emit('share', client) }">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0 0a2.25 2.25 0 1 0 3.935 2.186 2.25 2.25 0 0 0-3.935-2.186Zm0-12.814a2.25 2.25 0 1 0 3.933-2.185 2.25 2.25 0 0 0-3.933 2.185Z" /></svg>
             Partager
          </li>
          <li @click.stop="() => { isOpen = false; $emit('archive', client) }">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z" /></svg>
             Archiver
          </li>
          <li class="danger" @click.stop="() => { isOpen = false; $emit('delete', client) }">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" /></svg>
             Supprimer
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue';

const props = defineProps({
  client: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['view', 'edit', 'share', 'archive', 'delete']);

const isOpen = ref(false);
const cardRef = ref<HTMLElement | null>(null);
const menuPositionX = ref<'left' | 'right'>('right');
const menuPositionY = ref<'top' | 'bottom'>('top');

function toggleMenu() {
  isOpen.value = !isOpen.value;
  if (isOpen.value && cardRef.value) {
      const rect = cardRef.value.getBoundingClientRect();

      const spaceOnRight = window.innerWidth - rect.right;
      const spaceOnBottom = window.innerHeight - rect.top;

      if (spaceOnRight < 200) {
          menuPositionX.value = 'left';
      } else {
          menuPositionX.value = 'right';
      }

      if (spaceOnBottom < 320) {
          menuPositionY.value = 'bottom';
      } else {
          menuPositionY.value = 'top';
      }
  }
}

function formatDate(value: string) {
  if (!value) return '—';
  const d = new Date(value);
  // Just show time like 7:23 PM to match the image or date ?
  // Actually, standard clients have date_creation. Let's show date to make sense for a client.
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
}

</script>

<style scoped>
.customer-card {
  background-color: #fcfbfb;
  border-radius: 20px;
  padding: 1.5rem;
  color: #ffffff;
  font-family: 'Inter', system-ui, sans-serif;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: relative;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  min-width: 350px;
}

.card--active {
  z-index: 50;
}

.customer-card:hover,
.customer-card.card--active {
  transform: translateY(-4px);
  box-shadow: 0 15px 35px rgba(0,0,0,0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #7a7777;
  font-weight: 400;
}

.card-header .role{
  background: var(--primary-color);
  padding: 0.4rem 0.6rem;
  color: #fff;
  border-radius: 4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.time-container {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.clock-icon {
  width: 16px;
  height: 16px;
}

.menu-trigger {
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.menu-trigger:hover {
  color: var(--primary-color);
}

.size-5 {
  width: 1.25rem;
  height: 1.25rem;
}

.card-body {
  width: 100%;
  display: flex;
  align-items: left;
  justify-content: left;
  gap: 1rem;
}

.avatar-container {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #a855f7, #ec4899);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-fallback {
  color: white;
  font-weight: 600;
  font-size: 1.2rem;
}

.info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
  letter-spacing: -0.01em;
  width: 100%;
  text-align: left;
}

.email {
  margin: 0;
  color: #a8a8a8;
  font-size: 0.8rem;
  font-weight: 400;
}

/* Status colors mapped slightly to fit dark theme better if needed */
.dot.actif { background-color: #a3e635; }
.dot.inactif { background-color: #ef4444; }
.dot.prospect { background-color: #60a5fa; }
.dot.archive { background-color: #fbbf24; }

.card-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.25rem;
}

.primary-btn, .secondary-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.7rem 1rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.primary-btn {
  background-color: var(--primary-color);
  color: #fcfbfb;
}

.primary-btn:hover {
  background-color: var(--primary-color-dark);
  color: #fcfbfb;
}

.secondary-btn {
  background-color: #e5e5e5;
  color: #404040;
  max-width: 50px;
}

.secondary-btn:hover {
  background-color: #f3f3f3;
  color: #171717;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* --- Dropbox --- */
.dropbox {
    position: absolute;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    border: 1px solid #f3f4f6;
    min-width: 170px;
    z-index: 55;
    overflow: hidden;
    padding: 0.5rem;
}

.dropbox--top {
    top: 0;
    bottom: auto;
}
.dropbox--bottom {
    bottom: 0;
    top: auto;
}

.dropbox--right {
    left: calc(100% + 15px);
    right: auto;
}
.dropbox--left {
    right: calc(100% + 15px);
    left: auto;
}

.dropbox--right.dropbox--top { transform-origin: top left; }
.dropbox--right.dropbox--bottom { transform-origin: bottom left; }
.dropbox--left.dropbox--top { transform-origin: top right; }
.dropbox--left.dropbox--bottom { transform-origin: bottom right; }

.dropbox ul {
    list-style: none;
    margin: 0;
    padding: 0.5rem 0;
}

.dropbox li {
    padding: 0.7rem;
    font-size: 0.875rem;
    color: #374151;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s ease, color 0.2s ease;
    border-radius: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
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
