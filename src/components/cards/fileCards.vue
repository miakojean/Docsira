<template>
    <li class="file-item" :class="`file-item--${view}`" @click="emit('open', filePath)">
        <div class="file-info flex items-center gap-4 truncate">
            <div v-if="isImage" class="image-box">
                <img :src="imageSource" :alt="fileName" class="file-preview" @error="imageLoadFailed = true" />
            </div>
            <div v-else-if="hasPreview && view === 'grid'" class="preview-box">
                <iframe :src="previewSource" class="file-preview pointer-events-none" frameborder="0" scrolling="no" tabindex="-1"></iframe>
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
const previewExtensions = ['pdf', 'txt', 'html', 'md', 'csv', 'json'];

const fileName = computed(() => props.filePath.split(/[/\\]/).pop() || 'Fichier inconnu');
const fileExtension = computed(() => {
    const parts = fileName.value.split('.');
    return parts.length > 1 ? parts.pop() || '' : 'Fichier';
});

const isImage = computed(() => imageExtensions.includes(fileExtension.value.toLowerCase()) && !imageLoadFailed.value);
const isPdf = computed(() => fileExtension.value.toLowerCase() === 'pdf');
const hasPreview = computed(() => previewExtensions.includes(fileExtension.value.toLowerCase()) && !imageLoadFailed.value);

const imageSource = computed(() => convertFileSrc(props.filePath));
const previewSource = computed(() => {
    if (isPdf.value) return `${imageSource.value}#toolbar=0&navpanes=0&scrollbar=0&view=FitH`;
    return imageSource.value;
});

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
.file-item--list:hover { background-color: #f8fafc; }

.file-info { flex: 1; min-width: 0; }
.icon-box, .image-box, .preview-box { display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 8px; flex: 0 0 40px; overflow: hidden; }
.image-box { background-color: #f3f4f6; }
.preview-box { background-color: #ffffff; }
.file-preview { width: 100%; height: 100%; object-fit: cover ; overflow: hidden; }
.is-pdf { background-color: #fee2e2; color: #ef4444; }
.is-word { background-color: #e0e7ff; color: #4f46e5; }
.is-excel { background-color: #dcfce7; color: #16a34a; }
.is-default { background-color: #f3f4f6; color: #6b7280; }
.file-text { display: flex; flex-direction: column; min-width: 0; }
.file-name { margin: 0; font-size: 0.95rem; font-weight: 600; color: #1f2937; }
.file-path { font-size: 0.75rem; color: #9ca3af; font-weight: 500; }
.actions-group { opacity: 0; transition: opacity 0.2s ease; }
.file-item--list:hover .actions-group { opacity: 1; }
.action-btn { background: transparent; border: none; color: #64748b; cursor: pointer; padding: 0.5rem; border-radius: 6px; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; }
.action-btn:hover { background-color: #e2e8f0; color: #0f172a; }

/* Grid View specific styles (Animations and Glassmorphism) */
.file-item--grid { 
    position: relative;
    padding: 0;
    min-width: 0; 
    height: 280px; 
    flex-direction: column; 
    align-items: stretch; 
    gap: 0; 
    border-radius: 20px;
    background-color: #000000; /* fallback behind icon/image */
    overflow: hidden;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.file-item--grid:hover {
    background-color: #ffffff;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Reset .file-info properties for absolute positioning of children */
.file-item--grid .file-info { 
    position: static;
    flex-direction: column; 
    align-items: stretch; 
    gap: 0;
    overflow: visible; 
}

.file-item--grid .image-box, 
.file-item--grid .icon-box,
.file-item--grid .preview-box { 
    position: absolute;
    top: 0;
    left: 0;
    width: 100%; 
    height: 100%; 
    flex-basis: auto; 
    border-radius: 0;
    z-index: 1;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.file-item--grid:hover .image-box, 
.file-item--grid:hover .icon-box,
.file-item--grid:hover .preview-box {
    top: 10px;
    left: 10px;
    width: calc(100% - 20px);
    height: 160px;
    border-radius: 16px;
}

/* Hide scrollbars inside the iframe by pushing them out of the container bounds */
.file-item--grid .preview-box iframe.file-preview {
    position: absolute;
    top: 0;
    left: 0;
    width: calc(100% + 30px);
    height: calc(100% + 30px);
    max-width: none;
    border: none;
}

/* Dark gradient overlay for normal state */
.file-item--grid::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0) 100%);
    z-index: 2;
    transition: opacity 0.4s ease;
    border-radius: 20px;
    pointer-events: none;
}
.file-item--grid:hover::after {
    opacity: 0;
}

/* Positioning text at the bottom */
.file-item--grid .file-text {
    position: absolute;
    bottom: 24px;
    left: 20px;
    right: 20px;
    z-index: 3;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Move text up to make space for action buttons on hover */
.file-item--grid:hover .file-text {
    bottom: 60px;
}

/* Text style changes on hover */
.file-item--grid .file-name {
    color: #ffffff;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 4px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    transition: color 0.4s ease, text-shadow 0.4s ease;
}

.file-item--grid:hover .file-name {
    color: #111827;
    text-shadow: none;
}

.file-item--grid .file-path {
    color: #e5e7eb;
    font-size: 0.8rem;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    transition: color 0.4s ease, text-shadow 0.4s ease;
}

.file-item--grid:hover .file-path {
    color: #6b7280;
    text-shadow: none;
}

/* Action buttons transition */
.file-item--grid .actions-group {
    position: absolute;
    bottom: 20px;
    left: 20px;
    right: 20px;
    z-index: 3;
    opacity: 0;
    transform: translateY(15px);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    background: transparent;
    pointer-events: none; /* Disable pointer events when hidden */
    gap: 12px !important; 
    justify-content: center !important;
}

.file-item--grid:hover .actions-group {
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto; /* Enable when visible */
}

/* Style action buttons */
.file-item--grid .action-btn {
    background-color: #f1f5f9;
    color: #334155;
    flex: 1;
    padding: 0.6rem;
    border-radius: 12px;
    font-weight: 600;
    display: flex;
    justify-content: center;
    align-items: center;
}

.file-item--grid .action-btn:hover {
    background-color: #000000;
    color: #ffffff;
}
.file-item--grid .action-btn.text-red-500 {
    color: #ef4444;
}
.file-item--grid .action-btn.text-red-500:hover {
    background-color: #ef4444;
    color: #ffffff;
}

/* Icon sizing for grid */
.file-item--grid .icon-box .file-icon {
    width: 80px;
    height: 80px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    opacity: 0.9;
}
.file-item--grid:hover .icon-box .file-icon {
    width: 56px;
    height: 56px;
    opacity: 1;
}
</style>