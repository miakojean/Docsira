<template>
    <div class="files-list-container w-full">

        <!-- ÉTAT VIDE : Aucun fichier trouvé -->
        <div v-if="files.length === 0" class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-10 text-gray-300">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
            <p>Ce dossier est vide ou aucun fichier n'a été détecté.</p>
        </div>

        <!-- LISTE DES FICHIERS -->
        <ul v-else class="file-list" :class="`file-list--${view}`">
            <fileCards
                v-for="(filePath, index) in files"
            :key="filePath || index"
                :file-path="filePath"
            :view="view"
                @open="emit('open', $event)"
                @rename="emit('rename', $event)"
                @share="emit('share', $event)"
                @delete="emit('delete', $event)"
            />
        </ul>

        <footerSection :view="view" @update:view="view = $event" />
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import fileCards from '../../cards/fileCards.vue';
import footerSection from '../../layout/footerSection.vue';

defineProps<{
    files: string[]
}>();

// Les événements émis correspondent à ceux attendus par vos modales
const emit = defineEmits(['open', 'rename', 'share', 'delete']);
const view = ref<'list' | 'grid'>('list');
</script>

<style scoped>
.files-list-container {
    width: 100%;
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    scrollbar-width: 2px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.5rem;
}

/* --- État vide --- */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 1rem;
    background-color: #f9fafb;
    border: 2px dashed #e5e7eb;
    border-radius: 12px;
    color: #6b7280;
    gap: 0.75rem;
    font-size: 0.95rem;
}

/* --- Liste et Éléments --- */
.file-list {
    list-style: none;
    margin: 0;
    padding: 0;
}

.file-list--list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.file-list--grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
}

.file-item {
    padding: 0.75rem 1rem;
    border-radius: 20px;
    border: 1px solid transparent;
    transition: all 0.2s ease;
    cursor: pointer;
    background-color: #ffffff;
}

.file-item:hover {
    background-color: #f8fafc;
    /*border-color: #e2e8f0;*/
}

/* --- Informations du fichier --- */
.file-info {
    flex: 1;
    min-width: 0;
}

/* Couleurs dynamiques des icônes */
.icon-box {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 8px;
}

.is-pdf { background-color: #fee2e2; color: #ef4444; } /* Rouge */
.is-word { background-color: #e0e7ff; color: #4f46e5; } /* Indigo */
.is-excel { background-color: #dcfce7; color: #16a34a; } /* Vert */
.is-image { background-color: #f3e8ff; color: #9333ea; } /* Violet */
.is-default { background-color: #f3f4f6; color: #6b7280; } /* Gris */

.file-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.file-name {
    margin: 0;
    font-size: 0.95rem;
    font-weight: 600;
    color: #1f2937;
}

.file-path {
    font-size: 0.75rem;
    color: #9ca3af;
    font-weight: 500;
}

/* --- Boutons d'actions --- */
.actions-group {
    opacity: 0; /* Caché par défaut pour alléger l'UI */
    transition: opacity 0.2s ease;
}

.file-item:hover .actions-group {
    opacity: 1; /* Apparaît au survol de la ligne */
}

.action-btn {
    background: transparent;
    border: none;
    color: #64748b;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 6px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.action-btn:hover {
    background-color: #e2e8f0;
    color: #0f172a;
}

/* Utilitaire pour couper le texte trop long */
.truncate {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
</style>
