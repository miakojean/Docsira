<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="preview" class="preview-backdrop" @click.self="$emit('close')">
        <div class="preview-modal">
          <div class="preview-header">
            <div class="preview-title-box truncate">
              <h3 class="preview-title truncate">{{ preview.title }}</h3>
            </div>
            <div class="preview-actions">
              <button
                type="button"
                class="preview-action-btn"
                title="Télécharger"
                @click="$emit('download', preview.doc)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                </svg>
                <span>Télécharger</span>
              </button>
              <button
                type="button"
                class="preview-close-btn"
                aria-label="Fermer"
                @click="$emit('close')"
              >
                ×
              </button>
            </div>
          </div>

          <div class="preview-body">
            <img v-if="preview.kind === 'image'" :src="preview.url" :alt="preview.title" class="preview-img" />
            <iframe v-else-if="preview.kind === 'pdf'" :src="preview.url" class="preview-frame"></iframe>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import type { DossierDocument } from '../../stores/documentStore';

export interface PreviewData {
  url: string;
  title: string;
  kind: 'image' | 'pdf';
  doc: DossierDocument;
}

defineProps<{
  preview: PreviewData | null;
}>();

defineEmits<{
  (e: 'close'): void;
  (e: 'download', doc: DossierDocument): void;
}>();
</script>

<style scoped>
.preview-backdrop {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.preview-modal {
  width: 100%;
  max-width: 900px;
  height: 85vh;
  background: #ffffff;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.preview-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.preview-title-box {
  min-width: 0;
}

.preview-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #111827;
}

.preview-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preview-action-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  background: #eff6ff;
  color: var(--primary-color, #2563eb);
  border: 1px solid #bfdbfe;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.preview-action-btn:hover {
  background: #dbeafe;
}

.preview-close-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f3f4f6;
  color: #6b7280;
  font-size: 1.4rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.preview-close-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.preview-body {
  flex: 1;
  min-height: 0;
  background: #0f172a;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: none;
  background: #ffffff;
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.size-4 {
  width: 1rem;
  height: 1rem;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
