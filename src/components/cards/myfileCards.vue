<template>
  <div class="my-file-cards">
    <div class="my-file-header">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
        </svg>

    </div>

    <div class="my-file-body flex flex-col items-center justify-center gap-4">

        <div class="icon-wrapper flex items-center justify-center">
            <!-- 1. PDF -->
            <svg v-if="fileKind === 'pdf'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-pdf">
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                <path d="M5 12v-7a2 2 0 0 1 2 -2h7l5 5v4" />
                <path d="M5 18h1.5a1.5 1.5 0 0 0 0 -3h-1.5v6" />
                <path d="M17 18h2" />
                <path d="M20 15h-3v6" />
                <path d="M11 15v6h1a2 2 0 0 0 2 -2v-2a2 2 0 0 0 -2 -2h-1" />
            </svg>

            <!-- 2. WORD (doc, docx, etc.) -->
            <svg v-else-if="fileKind === 'word'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-word">
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
                <path d="M9 12l1.5 6l1.5 -4l1.5 4l1.5 -6" />
            </svg>

            <!-- 3. EXCEL / CSV -->
            <svg v-else-if="fileKind === 'excel'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-excel">
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
                <path d="M10 12l4 6" />
                <path d="M10 18l4 -6" />
            </svg>

            <!-- 4. IMAGE (png, jpg, webp, etc.) -->
            <svg v-else-if="fileKind === 'image'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-image">
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M15 8h.01" />
                <path d="M3 6a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v12a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3v-12z" />
                <path d="M3 16l5 -5c.928 -.893 2.072 -.893 3 0l5 5" />
                <path d="M14 14l1 -1c.617 -.593 1.328 -.793 2.009 -.6" />
            </svg>

            <!-- 5. AUTRE / DEFAUT -->
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-other">
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
            </svg>
        </div>

        <div class="file-name">
            <span>{{ document.file_name }}</span>
        </div>

    </div>

    <div class="divider"></div>

    <div class="my-file-footer flex items-center justify-around">
        <div class="size-wrapper flex flex-col justify-items-start">
            <span>Taille</span>
            <span>{{document.size}} Ko</span>
        </div>
        <div class="initials-wrapper">
            <button class="btn-wrapper">A</button>
        </div>
    </div>
  </div>
</template>

<script lang="ts">
import {computed} from 'vue'
type FileKind = 'pdf' | 'word' | 'excel' | 'image' | 'other'


export default {

    props:{
        document:{
            type: Object,
            default:{}
        }
    },
    emits:['open', 'preview', 'detail', 'rename', 'share', 'download', 'delete'],
    setup(props:any,{emit}){
        
        // Computed my file extension from the props
        const KIND_BY_EXT: Record<string, FileKind> = {
            pdf: 'pdf',

            doc: 'word', docx: 'word', rtf: 'word', odt: 'word',

            xls: 'excel', xlsx: 'excel', csv: 'excel', ods: 'excel',

            png: 'image', jpg: 'image', jpeg: 'image',
            webp: 'image', gif: 'image', svg: 'image', bmp: 'image',
        }

        const fileKind = computed<FileKind>(() => {
            const raw = props.document?.extension
                if (typeof raw !== 'string') return 'other'

            const ext = raw.trim().replace(/^\./, '').toLowerCase()
            return KIND_BY_EXT[ext] ?? 'other'
        })

        return {
            KIND_BY_EXT,
            fileKind,
        }
    }
}
</script>

<style scoped>

.my-file-cards,
.my-file-cards * {
  box-sizing: border-box;
}

.my-file-cards{
    width: 260px;
    height: 290px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #f9f8f8;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    transition: ease-in-out 0.3s;
    cursor: pointer;
    overflow: hidden;
}

.my-file-cards:hover{
    background: #f5f3f3;
    border: 1px solid #005380;
}

.my-file-header{
    width: 100%;
    display: flex;
    justify-content: flex-end;
}

.my-file-body{
    padding: 0 0.5rem;
}

.file-name {
  width: 100%;             /* take the card width, don't hug the text */
  min-width: 0;
  padding: 0 0.75rem;      /* border-box → padding stays inside */
  text-align: center;
}

.my-file-body span{
    font-size: 0.9rem;
    font-weight: 500;
}

.file-name span {
  display: -webkit-box;
  -webkit-line-clamp: 2;   /* max 2 lines, then ellipsis */
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow-wrap: anywhere; /* THE fix: break unbreakable strings */
  word-break: break-word;  /* older-engine fallback */
  line-height: 1.3;
}

.icon-wrapper{
    height: 90px;
    width: 80px;
    border: 1px solid #ddd;
}

.icon-wrapper svg{
    color: red;
}

.size-wrapper span{
    font-size: 0.8rem;
    font-weight: 400;
    color: #999999;
}
.my-file-footer{
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem;
}

.btn-wrapper{
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-color-ligth);
    color: #f9f8f8;
    height: 30px;
    width: 30px;
}

/* About icon color */
.icon-wrapper svg {
  width: 32px;  /* Augmenter la taille pour une meilleure visibilité */
  height: 32px;
}

/* Couleurs spécifiques par type de fichier */
.icon-pdf {
  color: #e53935; /* Rouge */
}

.icon-word {
  color: #1e88e5; /* Bleu */
}

.icon-excel {
  color: #43a047; /* Vert */
}

.icon-image {
  color: #8e24aa; /* Violet */
}

.icon-other {
  color: #757575; /* Gris */
}
</style>