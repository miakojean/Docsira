<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="preview" class="preview-backdrop" @click.self="$emit('close')">
        <div class="preview-modal">
          <div class="preview-header">
            <div class="preview-title-box truncate">
              <h3 class="preview-title truncate">{{ preview.title }}</h3>
              <span v-if="preview.kind === 'pdf' && pdfPageCount > 0" class="preview-badge">
                {{ pdfPageCount }} page{{ pdfPageCount > 1 ? 's' : '' }}
              </span>
              <span v-else-if="preview.kind === 'docx'" class="preview-badge is-word">Word</span>
              <span v-else-if="preview.kind === 'image'" class="preview-badge is-image">Image</span>
            </div>

            <div class="preview-actions">
              <!-- Contrôles de zoom pour PDF -->
              <div v-if="preview.kind === 'pdf' && pdfPageCount > 0" class="zoom-controls">
                <button
                  type="button"
                  class="zoom-btn"
                  title="Zoom arrière"
                  :disabled="pdfScale <= 0.6"
                  @click="changeZoom(-0.2)"
                >
                  −
                </button>
                <span class="zoom-label">{{ Math.round(pdfScale * 100) }}%</span>
                <button
                  type="button"
                  class="zoom-btn"
                  title="Zoom avant"
                  :disabled="pdfScale >= 2.4"
                  @click="changeZoom(0.2)"
                >
                  +
                </button>
              </div>

              <button
                v-if="preview.doc"
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

          <div class="preview-body" :class="{ 'is-document-bg': preview.kind === 'pdf' || preview.kind === 'docx' }">
            <!-- Chargement -->
            <div v-if="preview.kind === 'loading' || isRenderingPdf" class="preview-state">
              <LogoLoader size="md" label="Chargement de l'aperçu..." />
            </div>

            <!-- Image -->
            <img
              v-else-if="preview.kind === 'image' && preview.url"
              :src="preview.url"
              :alt="preview.title"
              class="preview-img"
            />

            <!-- PDF rendu via pdfjs-dist -->
            <div v-show="preview.kind === 'pdf' && !isRenderingPdf && !pdfError" ref="pdfContainerRef" class="pdf-pages-container"></div>

            <!-- Erreur PDF -->
            <div v-if="preview.kind === 'pdf' && pdfError" class="preview-state">
              <p class="state-message">{{ pdfError }}</p>
              <button v-if="preview.doc" type="button" class="preview-action-btn" @click="$emit('download', preview.doc)">
                Télécharger le PDF
              </button>
            </div>

            <!-- Word (.docx) rendu via mammoth -->
            <div v-else-if="preview.kind === 'docx'" class="docx-scroll-container">
              <article class="docx-page" v-html="preview.html || '<p>Document vide.</p>'"></article>
            </div>

            <!-- Format non prévisualisable (ex: ancien .doc) -->
            <div v-else-if="preview.kind === 'unsupported'" class="preview-state">
              <p class="state-message">
                {{ preview.message || "L'aperçu intégré n'est pas disponible pour ce format." }}
              </p>
              <button v-if="preview.doc" type="button" class="preview-action-btn" @click="$emit('download', preview.doc)">
                Télécharger le document
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue';
import * as pdfjsLib from 'pdfjs-dist';
import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
import type { DossierDocument } from '../../stores/documentStore';
import LogoLoader from '../tools/LogoLoader.vue';

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl;

export interface PreviewData {
  title: string;
  kind: 'loading' | 'image' | 'pdf' | 'docx' | 'unsupported';
  doc?: DossierDocument;
  url?: string;
  data?: ArrayBuffer;
  html?: string;
  message?: string;
}

const props = defineProps<{
  preview: PreviewData | null;
}>();

defineEmits<{
  (e: 'close'): void;
  (e: 'download', doc: DossierDocument): void;
}>();

const pdfContainerRef = ref<HTMLDivElement | null>(null);
const isRenderingPdf = ref(false);
const pdfError = ref('');
const pdfPageCount = ref(0);
const pdfScale = ref(1.2);
let renderGeneration = 0;

function changeZoom(delta: number) {
  const next = Math.min(2.4, Math.max(0.6, Number((pdfScale.value + delta).toFixed(1))));
  if (next !== pdfScale.value) {
    pdfScale.value = next;
  }
}

async function renderPdf(buffer: ArrayBuffer) {
  const gen = ++renderGeneration;
  isRenderingPdf.value = true;
  pdfError.value = '';
  pdfPageCount.value = 0;

  await nextTick();
  const container = pdfContainerRef.value;
  if (!container) {
    isRenderingPdf.value = false;
    return;
  }
  container.innerHTML = '';

  try {
    const bytes = new Uint8Array(buffer.slice(0));
    const loadingTask = pdfjsLib.getDocument({ data: bytes });
    const pdfDoc = await loadingTask.promise;

    if (gen !== renderGeneration) {
      await loadingTask.destroy();
      return;
    }

    pdfPageCount.value = pdfDoc.numPages;
    const dpr = window.devicePixelRatio || 1;

    for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
      if (gen !== renderGeneration) {
        await loadingTask.destroy();
        return;
      }

      const page = await pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale: pdfScale.value });

      const pageWrapper = document.createElement('div');
      pageWrapper.className = 'pdf-page-wrapper';

      const canvas = document.createElement('canvas');
      canvas.className = 'pdf-page-canvas';
      canvas.width = Math.floor(viewport.width * dpr);
      canvas.height = Math.floor(viewport.height * dpr);
      canvas.style.width = `${Math.floor(viewport.width)}px`;
      canvas.style.height = `${Math.floor(viewport.height)}px`;

      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        await page.render({ canvasContext: ctx, viewport, canvas }).promise;
      }

      pageWrapper.appendChild(canvas);
      container.appendChild(pageWrapper);
    }

    await loadingTask.destroy();
  } catch (err) {
    console.error('Erreur rendu PDF :', err);
    if (gen === renderGeneration) {
      pdfError.value = "Impossible d'afficher ce fichier PDF. Vous pouvez le télécharger pour l'ouvrir localement.";
    }
  } finally {
    if (gen === renderGeneration) {
      isRenderingPdf.value = false;
    }
  }
}

watch(
  () => [props.preview?.kind, props.preview?.data, pdfScale.value] as const,
  ([kind, data]) => {
    if (kind === 'pdf' && data) {
      void renderPdf(data);
    } else {
      renderGeneration++;
      isRenderingPdf.value = false;
      pdfError.value = '';
      pdfPageCount.value = 0;
      if (pdfContainerRef.value) pdfContainerRef.value.innerHTML = '';
    }
  },
  { immediate: true }
);

watch(
  () => props.preview?.doc?.id,
  () => {
    pdfScale.value = 1.2;
  }
);
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
  max-width: 980px;
  height: 88vh;
  background: #ffffff;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.preview-header {
  padding: 0.9rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-shrink: 0;
}

.preview-title-box {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.preview-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #111827;
}

.preview-badge {
  flex-shrink: 0;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  background: #fee2e2;
  color: #dc2626;
}

.preview-badge.is-word {
  background: #dbeafe;
  color: #1d4ed8;
}

.preview-badge.is-image {
  background: #f3e8ff;
  color: #7e22ce;
}

.preview-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-shrink: 0;
}

.zoom-controls {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.2rem 0.35rem;
}

.zoom-btn {
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 6px;
  background: #ffffff;
  color: #334155;
  font-size: 1rem;
  font-weight: 700;
  line-height: 1;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.zoom-btn:hover:not(:disabled) {
  background: #e2e8f0;
}

.zoom-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.zoom-label {
  min-width: 44px;
  text-align: center;
  font-size: 0.78rem;
  font-weight: 600;
  color: #334155;
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
  padding: 1.25rem;
}

.preview-body.is-document-bg {
  background: #e2e8f0;
  align-items: flex-start;
}

.preview-state {
  margin: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  text-align: center;
  padding: 2rem;
  background: #ffffff;
  border-radius: 14px;
  max-width: 460px;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
}

.state-message {
  margin: 0;
  font-size: 0.92rem;
  color: #334155;
  line-height: 1.5;
}

.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.pdf-pages-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.pdf-pages-container :deep(.pdf-page-wrapper) {
  background: #ffffff;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.14);
  border-radius: 4px;
  overflow: hidden;
  line-height: 0;
}

.docx-scroll-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.docx-page {
  width: 100%;
  max-width: 794px;
  min-height: 600px;
  background: #ffffff;
  color: #1e293b;
  padding: 2.5rem 3rem;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.12);
  font-size: 0.95rem;
  line-height: 1.65;
  overflow-wrap: break-word;
}

.docx-page :deep(h1),
.docx-page :deep(h2),
.docx-page :deep(h3),
.docx-page :deep(h4) {
  color: #0f172a;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.docx-page :deep(p) {
  margin: 0 0 0.75rem;
}

.docx-page :deep(ul),
.docx-page :deep(ol) {
  margin: 0 0 0.85rem;
  padding-left: 1.5rem;
}

.docx-page :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.88rem;
}

.docx-page :deep(th),
.docx-page :deep(td) {
  border: 1px solid #cbd5e1;
  padding: 0.45rem 0.65rem;
  text-align: left;
}

.docx-page :deep(img) {
  max-width: 100%;
  height: auto;
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
