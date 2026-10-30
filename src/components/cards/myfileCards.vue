<template>
  <div
    class="my-file-cards"
    draggable="true"
    @dragstart="onDragStart"
    @click="$emit('open', document)"
  >
    <div class="my-file-header" @click.stop>
      <button
        type="button"
        class="kebab-btn"
        title="Options"
        @click="isMenuOpen = !isMenuOpen"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
        </svg>
      </button>

      <!-- Dropdown des actions du document -->
      <div v-if="isMenuOpen" class="file-dropdown-menu">
        <button type="button" class="dropdown-row" @click="emitAction('open')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
          </svg>
          <span>Visualiser</span>
        </button>

        <button type="button" class="dropdown-row" @click="emitAction('details')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
          </svg>
          <span>Détails</span>
        </button>

        <button type="button" class="dropdown-row" @click="emitAction('download')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          <span>Télécharger</span>
        </button>

        <button type="button" class="dropdown-row" @click="emitAction('move')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
          </svg>
          <span>Déplacer vers...</span>
        </button>

        <button type="button" class="dropdown-row" @click="emitAction('rename')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
          </svg>
          <span>Renommer</span>
        </button>

        <button type="button" class="dropdown-row is-danger" @click="emitAction('delete')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
          </svg>
          <span>Supprimer</span>
        </button>
      </div>
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
        <span :title="document.title || document.file_name">{{ document.title || document.file_name }}</span>
      </div>
    </div>

    <div class="divider"></div>

    <div class="my-file-footer flex items-center justify-around">
      <div class="size-wrapper flex flex-col justify-items-start">
        <span>Taille</span>
        <span>{{ formatSize(document.size) }}</span>
      </div>
      <div class="initials-wrapper">
        <button type="button" class="btn-wrapper" :title="document.title">
          {{ (document.extension || 'DOC').toUpperCase().slice(0, 3) }}
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue';

type FileKind = 'pdf' | 'word' | 'excel' | 'image' | 'other';

export default {
  props: {
    document: {
      type: Object,
      default: () => ({}),
    },
  },
  emits: ['open', 'preview', 'detail', 'details', 'rename', 'share', 'download', 'delete', 'move'],
  setup(props: any, { emit }: any) {
    const isMenuOpen = ref(false);

    const KIND_BY_EXT: Record<string, FileKind> = {
      pdf: 'pdf',
      doc: 'word', docx: 'word', rtf: 'word', odt: 'word',
      xls: 'excel', xlsx: 'excel', csv: 'excel', ods: 'excel',
      png: 'image', jpg: 'image', jpeg: 'image',
      webp: 'image', gif: 'image', svg: 'image', bmp: 'image',
    };

    const fileKind = computed<FileKind>(() => {
      const raw = props.document?.extension;
      if (typeof raw !== 'string') return 'other';
      const ext = raw.trim().replace(/^\./, '').toLowerCase();
      return KIND_BY_EXT[ext] ?? 'other';
    });

    function formatSize(bytes?: number) {
      if (!bytes || bytes <= 0) return '0 Ko';
      const kb = bytes / 1024;
      if (kb < 1024) return `${kb.toFixed(1)} Ko`;
      return `${(kb / 1024).toFixed(1)} Mo`;
    }

    function emitAction(eventName: string) {
      isMenuOpen.value = false;
      emit(eventName, props.document);
    }

    function onDragStart(e: DragEvent) {
      if (e.dataTransfer && props.document?.id) {
        e.dataTransfer.setData('text/plain', String(props.document.id));
        e.dataTransfer.effectAllowed = 'move';
      }
    }

    function onWindowClick() {
      if (isMenuOpen.value) isMenuOpen.value = false;
    }

    onMounted(() => {
      window.addEventListener('click', onWindowClick);
    });

    onUnmounted(() => {
      window.removeEventListener('click', onWindowClick);
    });

    return {
      isMenuOpen,
      fileKind,
      formatSize,
      emitAction,
      onDragStart,
    };
  },
};
</script>

<style scoped>
.my-file-cards,
.my-file-cards * {
  box-sizing: border-box;
}

.my-file-cards {
  width: 100%;
  max-width: 260px;
  height: 290px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.my-file-cards:hover {
  background: #ffffff;
  border-color: #2563eb;
  transform: translateY(-4px);
  box-shadow: 0 10px 20px -3px rgba(37, 99, 235, 0.12);
}

.my-file-header {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  position: relative;
}

.kebab-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.kebab-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.file-dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.25rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  padding: 0.35rem;
  min-width: 160px;
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.dropdown-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.65rem;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #374151;
  font-size: 0.85rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.dropdown-row:hover {
  background: #f3f4f6;
  color: #111827;
}

.dropdown-row.is-danger {
  color: #dc2626;
}

.dropdown-row.is-danger:hover {
  background: #fef2f2;
}

.my-file-body {
  padding: 0 0.5rem;
  width: 100%;
}

.file-name {
  width: 100%;
  min-width: 0;
  padding: 0 0.5rem;
  text-align: center;
}

.file-name span {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1f2937;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow-wrap: anywhere;
  word-break: break-word;
  line-height: 1.3;
}

.icon-wrapper {
  height: 90px;
  width: 80px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #f8fafc;
}

.icon-wrapper svg {
  width: 36px;
  height: 36px;
}

.icon-pdf { color: #e53935; }
.icon-word { color: #1e88e5; }
.icon-excel { color: #43a047; }
.icon-image { color: #8e24aa; }
.icon-other { color: #757575; }

.divider {
  width: 100%;
  height: 1px;
  background-color: #f1f5f9;
}

.my-file-footer {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.25rem 0.5rem;
}

.size-wrapper span {
  font-size: 0.75rem;
  font-weight: 500;
  color: #94a3b8;
}

.btn-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eff6ff;
  color: #2563eb;
  font-size: 0.75rem;
  font-weight: 700;
  border-radius: 6px;
  border: none;
  height: 26px;
  padding: 0 0.45rem;
}
</style>