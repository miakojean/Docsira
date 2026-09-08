<template>
    <div class="my-list-container">
        <!-- État vide : s'affiche si aucun dossier n'est dans la liste -->
        <div v-if="folders.length === 0" class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8 text-gray-400">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 0 0-1.883 2.542l.857 6a2.25 2.25 0 0 0 2.227 1.932H19.05a2.25 2.25 0 0 0 2.227-1.932l.857-6a2.25 2.25 0 0 0-1.883-2.542m-16.5 0V6A2.25 2.25 0 0 1 6 3.75h3.879a1.5 1.5 0 0 1 1.06.44l2.122 2.12a1.5 1.5 0 0 0 1.06.44H18A2.25 2.25 0 0 1 20.25 9v.776" />
            </svg>
            <p>Aucun dossier ouvert pour le moment.</p>
        </div>

        <!-- Liste des dossiers -->
        <ul v-else class="folder-list flex flex-col gap-3">
            <li 
                v-for="(folderPath, index) in folders" 
                :key="index" 
                class="folder-item flex items-center justify-between"
                @click="$emit('open', folderPath)"
            >
                <div class="folder-info flex items-center gap-4 truncate">
                    <!-- Icône Dossier -->
                    <div class="icon-box">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6 folder-icon">
                          <path d="M19.5 21a3 3 0 0 0 3-3v-9a3 3 0 0 0-3-3h-7a1 1 0 0 1-.7-.29L9.4 3.3A2 2 0 0 0 8 2.75H4.5a3 3 0 0 0-3 3v12.25a3 3 0 0 0 3 3h15z" />
                        </svg>
                    </div>
                    
                    <div class="folder-text truncate">
                        <!-- Extrait juste le nom du dossier -->
                        <h4 class="folder-name truncate">{{ getFolderName(folderPath) }}</h4>
                        <!-- Affiche le chemin complet en tout petit -->
                        <span class="folder-path truncate">{{ folderPath }}</span>
                    </div>
                </div>

                <!-- Action pour retirer le dossier de la liste -->
                <button 
                    class="remove-btn" 
                    @click.stop="$emit('remove', index)"
                    title="Retirer de la liste"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </li>
        </ul>
    </div>
</template>

<script setup lang="ts">
// Utilisation de la syntaxe moderne <script setup>
defineProps<{
    folders: string[]
}>();

const emit = defineEmits(['remove', 'open']);

// Fonction utilitaire pour extraire le nom du dossier à partir du chemin complet
const getFolderName = (fullPath: string): string => {
    if (!fullPath) return 'Dossier inconnu';
    // Gère les slash (Mac/Linux) et antislash (Windows)
    const parts = fullPath.split(/[/\\]/); 
    return parts.pop() || fullPath;
};
</script>

<style scoped>
.my-list-container {
    width: 100%;
    max-width: 600px;
}

/* --- État vide --- */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 1rem;
    background-color: #f9fafb;
    /* border: 2px dashed #e5e7eb;*/
    border-radius: 12px;
    color: #6b7280;
    gap: 0.5rem;
    font-size: 0.95rem;
}

/* --- Liste et Éléments --- */
.folder-list {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.folder-item {
    padding: 0.75rem 1rem;
    border-radius: 8px;
    border: 1px solid transparent;
    transition: all 0.2s ease;
    cursor: pointer;
    background-color: #ffffff;
}

.folder-item:hover {
    background-color: #f3f4f6;
    border-color: #e5e7eb;
}

/* --- Informations du dossier --- */
.folder-info {
    flex: 1;
    min-width: 0; /* Important pour que le truncate fonctionne */
}

.icon-box {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background-color: #eff6ff; /* Bleu très clair */
    border-radius: 8px;
}

.folder-icon {
    color: var(--primary-color); /* Bleu primaire */
}

.folder-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.folder-name {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
}

.folder-path {
    font-size: 0.75rem;
    color: #9ca3af;
}

/* --- Bouton Retirer --- */
.remove-btn {
    background: transparent;
    border: none;
    color: #9ca3af;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 6px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.remove-btn:hover {
    background-color: #fee2e2;
    color: #ef4444;
}

/* Utilitaire pour couper le texte trop long avec "..." */
.truncate {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
</style>