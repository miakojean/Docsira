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
        <ul v-else class="file-list flex flex-col gap-3">
            <li 
                v-for="(filePath, index) in files" 
                :key="index" 
                class="file-item flex items-center justify-between"
                @click="$emit('open', filePath)"
            >
                <!-- Informations du fichier -->
                <div class="file-info flex items-center gap-4 truncate">
                    
                    <!-- Icône Fichier dynamique selon l'extension -->
                    <div class="icon-box" :class="getFileColorClass(filePath)">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6 file-icon">
                          <path d="M5.625 1.5c-1.036 0-1.875.84-1.875 1.875v17.25c0 1.035.84 1.875 1.875 1.875h12.75c1.035 0 1.875-.84 1.875-1.875V12.75A3.75 3.75 0 0 0 16.5 9h-1.875a1.875 1.875 0 0 1-1.875-1.875V5.25A3.75 3.75 0 0 0 9 1.5H5.625Z" />
                          <path d="M12.971 1.816A5.23 5.23 0 0 1 14.25 5.25v1.875c0 .207.168.375.375.375H16.5a5.23 5.23 0 0 1 3.434 1.279 9.768 9.768 0 0 0-6.963-6.963Z" />
                        </svg>
                    </div>
                    
                    <div class="file-text truncate">
                        <h4 class="file-name truncate">{{ getFileName(filePath) }}</h4>
                        <span class="file-path truncate">{{ getFileExtension(filePath).toUpperCase() }} • Modifié récemment</span>
                    </div>
                </div>

                <!-- Actions du fichier (Connectées à vos modales) -->
                <div class="actions-group flex items-center gap-1">
                    <button class="action-btn" @click.stop="$emit('rename', filePath)" title="Renommer">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" /></svg>
                    </button>
                    <button class="action-btn" @click.stop="$emit('share', filePath)" title="Partager">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0 0a2.25 2.25 0 1 0 3.935 2.186 2.25 2.25 0 0 0-3.935-2.186Zm0-12.814a2.25 2.25 0 1 0 3.933-2.185 2.25 2.25 0 0 0-3.933 2.185Z" /></svg>
                    </button>
                    <button class="action-btn text-red-500 hover:bg-red-50" @click.stop="$emit('delete', filePath)" title="Supprimer">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
                    </button>
                </div>
            </li>
        </ul>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    files: string[]
}>();

// Les événements émis correspondent à ceux attendus par vos modales
const emit = defineEmits(['open', 'rename', 'share', 'delete']);

// Extraire le nom du fichier
const getFileName = (fullPath: string): string => {
    if (!fullPath) return 'Fichier inconnu';
    const parts = fullPath.split(/[/\\]/); 
    return parts.pop() || fullPath;
};

// Extraire l'extension (ex: 'pdf', 'docx')
const getFileExtension = (fullPath: string): string => {
    const fileName = getFileName(fullPath);
    const parts = fileName.split('.');
    return parts.length > 1 ? parts.pop() || '' : 'Fichier';
};

// UX : Attribuer une couleur d'icône selon le type de fichier
const getFileColorClass = (fullPath: string): string => {
    const ext = getFileExtension(fullPath).toLowerCase();
    if (['pdf'].includes(ext)) return 'is-pdf';
    if (['doc', 'docx', 'txt'].includes(ext)) return 'is-word';
    if (['xls', 'xlsx', 'csv'].includes(ext)) return 'is-excel';
    if (['png', 'jpg', 'jpeg', 'svg'].includes(ext)) return 'is-image';
    return 'is-default';
};
</script>

<style scoped>
.files-list-container {
    width: 100%;
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
    background-color: #ffffff;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.file-item {
    padding: 0.75rem 1rem;
    border-radius: 8px;
    border: 1px solid transparent;
    transition: all 0.2s ease;
    cursor: pointer;
    background-color: #ffffff;
}

.file-item:hover {
    background-color: #f8fafc;
    border-color: #e2e8f0;
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
    padding: 0.4rem;
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