<template>
  <Teleport to="body">
    <Transition name="modal-fade" :duration="250">
      <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card" role="dialog" aria-modal="true">
          <div class="modal-header">
            <div>
              <h3 class="modal-title">Partager par lien</h3>
              <p v-if="resolvedTitle" class="modal-subtitle">
                {{ resolvedTitle }}
              </p>
            </div>
            <button type="button" class="close-btn" @click="closeModal" aria-label="Fermer la modale">
              &times;
            </button>
          </div>

          <div class="modal-body">
            <p class="share-description">
              {{ description || "Créez un lien de partage et envoyez-le à un collaborateur ou à un client pour qu'il puisse consulter et télécharger ce document." }}
            </p>

            <!-- Création d'un nouveau lien -->
            <div class="create-row">
              <select v-model="selectedDuration" class="duration-select" :disabled="isCreating">
                <option :value="1">Expire dans 24 heures</option>
                <option :value="7">Expire dans 7 jours</option>
                <option :value="30">Expire dans 30 jours</option>
                <option :value="null">Sans expiration</option>
              </select>
              <button
                type="button"
                class="btn btn-primary"
                :disabled="isCreating"
                @click="$emit('create', selectedDuration)"
              >
                {{ isCreating ? 'Création...' : 'Nouveau lien' }}
              </button>
            </div>

            <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

            <!-- Lien principal prêt à copier -->
            <div v-if="isLoading" class="loading-box">
              <span>Préparation du lien de partage...</span>
            </div>

            <div v-else-if="primaryLink" class="active-link-box">
              <label class="field-label">Lien prêt à partager</label>
              <div class="link-input-group">
                <input
                  ref="linkInputRef"
                  type="text"
                  :value="primaryLink.share_url"
                  class="link-input"
                  readonly
                  @focus="onFocus"
                />
                <button
                  type="button"
                  class="btn-copy"
                  :class="{ 'is-copied': copiedId === primaryLink.id }"
                  @click="copyLink(primaryLink)"
                >
                  {{ copiedId === primaryLink.id ? 'Copié !' : 'Copier' }}
                </button>
              </div>
              <span class="link-meta">
                {{ formatExpiry(primaryLink) }} • {{ primaryLink.download_count }} accès
              </span>
            </div>

            <!-- Liste de tous les liens actifs -->
            <div v-if="!isLoading && links.length > 0" class="links-history">
              <h4 class="history-title">Liens actifs ({{ links.length }})</h4>
              <div class="links-list">
                <div v-for="item in links" :key="item.id" class="link-row">
                  <div class="link-row-info">
                    <span class="link-row-url" :title="item.share_url">{{ item.share_url }}</span>
                    <span class="link-row-meta">
                      {{ formatExpiry(item) }} • {{ item.download_count }} accès
                    </span>
                  </div>
                  <div class="link-row-actions">
                    <button
                      type="button"
                      class="mini-btn"
                      @click="copyLink(item)"
                    >
                      {{ copiedId === item.id ? 'Copié' : 'Copier' }}
                    </button>
                    <button
                      type="button"
                      class="mini-btn is-danger"
                      title="Révoquer ce lien"
                      @click="$emit('revoke', item.id)"
                    >
                      Révoquer
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn" @click="closeModal">Fermer</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue';
import type { DossierDocument } from '../../stores/documentStore';

export interface ShareLinkItem {
  id: string;
  token: string;
  share_url: string;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
  is_expired: boolean;
  download_count: number;
}

const props = withDefaults(
  defineProps<{
    isOpen: boolean;
    document?: DossierDocument | null;
    targetTitle?: string;
    description?: string;
    links?: ShareLinkItem[];
    isLoading?: boolean;
    isCreating?: boolean;
    errorMessage?: string;
  }>(),
  {
    isOpen: false,
    document: null,
    targetTitle: '',
    description: '',
    links: () => [],
    isLoading: false,
    isCreating: false,
    errorMessage: '',
  }
);

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'create', expiresInDays: number | null): void;
  (e: 'revoke', linkId: string): void;
}>();

const selectedDuration = ref<number | null>(7);
const copiedId = ref<string | null>(null);

const resolvedTitle = computed(
  () => props.targetTitle || props.document?.title || props.document?.file_name || ''
);
const primaryLink = computed(() => props.links.find((l) => !l.is_expired) ?? props.links[0] ?? null);

const onFocus = (event: FocusEvent) => {
  const target = event.target as HTMLInputElement | null;
  target?.select();
};

const copyLink = async (item: ShareLinkItem) => {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(item.share_url);
    } else {
      const textarea = window.document.createElement('textarea');
      textarea.value = item.share_url;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      window.document.body.appendChild(textarea);
      textarea.select();
      window.document.execCommand('copy');
      window.document.body.removeChild(textarea);
    }
    copiedId.value = item.id;
    setTimeout(() => {
      if (copiedId.value === item.id) copiedId.value = null;
    }, 2000);
  } catch (err) {
    console.error('Échec de la copie :', err);
  }
};

function formatExpiry(item: ShareLinkItem): string {
  if (!item.expires_at) return 'Sans expiration';
  if (item.is_expired) return 'Expiré';
  const date = new Date(item.expires_at);
  return `Expire le ${date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })}`;
}

const closeModal = () => {
  copiedId.value = null;
  emit('close');
};

watch(
  () => props.isOpen,
  (newVal) => {
    window.document.body.style.overflow = newVal ? 'hidden' : '';
    if (newVal) {
      selectedDuration.value = 7;
      copiedId.value = null;
    }
  }
);

onUnmounted(() => {
  window.document.body.style.overflow = '';
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal-card {
  background: #ffffff;
  border-radius: 18px;
  padding: 1.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.14);
  width: 100%;
  max-width: 520px;
  max-height: 88vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.modal-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #111827;
}

.modal-subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  color: #64748b;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.65rem;
  cursor: pointer;
  color: #9ca3af;
  line-height: 1;
  padding: 0;
}

.close-btn:hover {
  color: #ef4444;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.share-description {
  margin: 0;
  font-size: 0.88rem;
  color: #4b5563;
  line-height: 1.45;
}

.create-row {
  display: flex;
  gap: 0.6rem;
  align-items: center;
}

.duration-select {
  flex: 1;
  padding: 0.58rem 0.8rem;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #111827;
  font-size: 0.86rem;
  outline: none;
}

.duration-select:focus {
  border-color: var(--primary-color, #2563eb);
  background: #ffffff;
}

.error-text {
  margin: 0;
  font-size: 0.82rem;
  color: #dc2626;
}

.loading-box {
  padding: 1rem;
  text-align: center;
  font-size: 0.88rem;
  color: #64748b;
  background: #f8fafc;
  border-radius: 10px;
}

.active-link-box {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
}

.link-input-group {
  display: flex;
  align-items: center;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 0.25rem;
}

.link-input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 0.48rem 0.65rem;
  font-size: 0.84rem;
  color: #1e293b;
  width: 100%;
  outline: none;
}

.btn-copy {
  background-color: #ffffff;
  border: 1px solid #d1d5db;
  color: #374151;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.82rem;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.btn-copy:hover {
  background-color: #f3f4f6;
}

.btn-copy.is-copied {
  background-color: #16a34a;
  border-color: #16a34a;
  color: #ffffff;
}

.link-meta {
  font-size: 0.76rem;
  color: #64748b;
}

.links-history {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border-top: 1px solid #f1f5f9;
  padding-top: 0.85rem;
}

.history-title {
  margin: 0;
  font-size: 0.82rem;
  font-weight: 700;
  color: #334155;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  max-height: 170px;
  overflow-y: auto;
}

.link-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  padding: 0.5rem 0.7rem;
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.link-row-info {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.link-row-url {
  font-size: 0.78rem;
  font-weight: 500;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.link-row-meta {
  font-size: 0.72rem;
  color: #64748b;
}

.link-row-actions {
  display: flex;
  gap: 0.35rem;
  flex-shrink: 0;
}

.mini-btn {
  padding: 0.28rem 0.55rem;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  font-size: 0.74rem;
  font-weight: 600;
  cursor: pointer;
}

.mini-btn:hover {
  background: #f1f5f9;
}

.mini-btn.is-danger {
  color: #dc2626;
  border-color: #fecaca;
}

.mini-btn.is-danger:hover {
  background: #fef2f2;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: 0.58rem 1rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.86rem;
  cursor: pointer;
  border: none;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color, #2563eb);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-dark, #1d4ed8);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
