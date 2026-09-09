<template>
    <li class="file-item" :class="`file-item--${view}`" @click="emit('open', filePath)">
        <div class="file-info flex items-center gap-4 truncate">
            <div v-if="isImage" class="image-box">
                <img :src="imageSource" :alt="fileName" class="file-preview" @error="imageLoadFailed = true" />
            </div>
            <div v-else class="icon-box" :class="fileColorClass">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6 file-icon">
                    <path d="M5.625 1.5c-1.036 0-1.875.84-1.875 1.875v17.25c0 1.035.84 1.875 1.875 1.875h12.75c1.035 0 1.875-.84 1.875-1.875V12.75A3.75 3.75 0 0 0 16.5 9h-1.875a1.875 1.875 0 0 1-1.875-1.875V5.25A3.75 3.75 0 0 0 9 1.5H5.625Z" />
                    <path d="M12.971 1.816A5.23 5.23 0 0 1 14.25 5.25v1.875c0 .207.168.375.375.375H16.5a5.23 5.23 0 0 1 3.434 1.279 9.768 9.768 0 0 0-6.963-6.963Z" />
                </svg>
            </div>

            <div class="file-text truncate">
                <h4 class="file-name truncate">{{ fileName }}</h4>
                <span class="file-path truncate">{{ fileExtension.toUpperCase() }} • Modifié récemment</span>
            </div>
        </div>

        <div class="actions-group flex items-center gap-1">
            <button class="action-btn" @click.stop="emit('rename', filePath)" title="Renommer">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" /></svg>
            </button>
            <button class="action-btn" @click.stop="emit('share', filePath)" title="Partager">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0 0a2.25 2.25 0 1 0 3.935 2.186 2.25 2.25 0 0 0-3.935-2.186Zm0-12.814a2.25 2.25 0 1 0 3.933-2.185 2.25 2.25 0 0 0-3.933 2.185Z" /></svg>
            </button>
            <button class="action-btn text-red-500 hover:bg-red-50" @click.stop="emit('delete', filePath)" title="Supprimer">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
            </button>
        </div>
    </li>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { convertFileSrc } from '@tauri-apps/api/core';

const props = defineProps<{
    filePath: string;
    view?: 'list' | 'grid';
}>();
const emit = defineEmits<{
    open: [filePath: string];
    rename: [filePath: string];
    share: [filePath: string];
    delete: [filePath: string];
}>();

const imageLoadFailed = ref(false);
const imageExtensions = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp', 'avif'];
const fileName = computed(() => props.filePath.split(/[/\\]/).pop() || 'Fichier inconnu');
const fileExtension = computed(() => {
    const parts = fileName.value.split('.');
    return parts.length > 1 ? parts.pop() || '' : 'Fichier';
});
const isImage = computed(() => imageExtensions.includes(fileExtension.value.toLowerCase()) && !imageLoadFailed.value);
const imageSource = computed(() => convertFileSrc(props.filePath));
const fileColorClass = computed(() => {
    const extension = fileExtension.value.toLowerCase();
    if (extension === 'pdf') return 'is-pdf';
    if (['doc', 'docx', 'txt'].includes(extension)) return 'is-word';
    if (['xls', 'xlsx', 'csv'].includes(extension)) return 'is-excel';
    return 'is-default';
});
</script>

<style scoped>
.file-item { 
    padding: 0.5rem; 
    border-radius: 8px; 
    border: 1px solid transparent; 
    transition: all 0.2s ease; 
    cursor: pointer; 
    background-color: #ffffff; 
    display: flex; 
    align-items: center; 
    justify-content: space-between; 
}
.file-item--grid { min-width: 0; min-height: 180px; flex-direction: column; align-items: stretch; gap: 0.75rem; }
.file-item--grid .file-info { flex-direction: column; align-items: stretch; gap: 0.65rem; }
.file-item--grid .image-box, .file-item--grid .icon-box { 
    width: 100%; 
    height: 110px; 
    flex-basis: 110px; 
}
.file-item--grid .file-preview { object-fit: contain; }
.file-item--grid .actions-group { align-self: flex-end; }
.file-item:hover { background-color: #f8fafc; }
.file-info { flex: 1; min-width: 0; }
.icon-box, .image-box { display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 8px; flex: 0 0 40px; overflow: hidden; }
.image-box { background-color: #f3f4f6; }
.file-preview { width: 100%; height: 100%; object-fit: cover; }
.is-pdf { background-color: #fee2e2; color: #ef4444; }
.is-word { background-color: #e0e7ff; color: #4f46e5; }
.is-excel { background-color: #dcfce7; color: #16a34a; }
.is-default { background-color: #f3f4f6; color: #6b7280; }
.file-text { display: flex; flex-direction: column; min-width: 0; }
.file-name { margin: 0; font-size: 0.95rem; font-weight: 600; color: #1f2937; }
.file-path { font-size: 0.75rem; color: #9ca3af; font-weight: 500; }
.actions-group { opacity: 0; transition: opacity 0.2s ease; }
.file-item:hover .actions-group { opacity: 1; }
.action-btn { background: transparent; border: none; color: #64748b; cursor: pointer; padding: 0.5rem; border-radius: 6px; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; }
.action-btn:hover { background-color: #e2e8f0; color: #0f172a; }
</style>