<template>
  <aside
    class="comments-sidebar"
    :class="{ 'is-collapsed': !isOpen }"
    aria-label="Commentaires collaborateurs"
  >
    <!-- État replié : rail vertical avec l'icône commentaire et le partage -->
    <div v-if="!isOpen" class="collapsed-rail">
      <button
        type="button"
        class="comment-icon-btn"
        :class="{ 'has-unread': unreadCount > 0 }"
        :title="unreadCount > 0 ? `${unreadCount} nouveau(x) commentaire(s) — Cliquer pour ouvrir` : 'Ouvrir les commentaires'"
        aria-label="Ouvrir les commentaires"
        :aria-expanded="false"
        @click="$emit('toggle')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="comment-icon-svg">
          <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
        </svg>
        <span v-if="unreadCount > 0" class="unread-dot-count">
          {{ unreadCount > 9 ? '9+' : unreadCount }}
        </span>
      </button>

      <button
        v-if="canShare"
        type="button"
        class="comment-icon-btn"
        title="Partager le dossier par lien"
        aria-label="Partager le dossier par lien"
        @click="$emit('share')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="comment-icon-svg">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" />
        </svg>
      </button>
    </div>

    <!-- État ouvert : panneau latéral des commentaires -->
    <template v-else>
      <header class="panel-header">
        <h3 class="panel-title">Commentaires</h3>
        <button
          type="button"
          class="comment-icon-btn is-active"
          title="Fermer les commentaires"
          aria-label="Fermer les commentaires"
          :aria-expanded="true"
          @click="$emit('toggle')"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="comment-icon-svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
          </svg>
        </button>
      </header>

      <!-- Filtre discret par document (uniquement s'il y a des documents dans le dossier) -->
      <div v-if="documents.length > 0" class="filter-bar">
        <label for="comment-filter-doc" class="filter-label">Afficher</label>
        <select
          id="comment-filter-doc"
          v-model="filterDocumentId"
          class="filter-select"
        >
          <option :value="null">Tous les échanges ({{ totalCount }})</option>
          <option v-for="doc in documents" :key="doc.id" :value="doc.id">
            {{ doc.title || doc.file_name }}
          </option>
        </select>
      </div>

      <!-- Erreur éventuelle -->
      <div v-if="errorMessage" class="error-line">
        <span>{{ errorMessage }}</span>
        <button type="button" class="text-action" @click="commentStore.errorMessage = ''">Masquer</button>
      </div>

      <!-- Fil des commentaires -->
      <div ref="listRef" class="comments-list-area">
        <div v-if="isLoading && threads.length === 0" class="state-box">
          <LogoLoader size="md" label="Chargement des échanges..." />
        </div>

        <div v-else-if="threads.length === 0" class="empty-box">
          <p class="empty-title">Aucun commentaire pour le moment</p>
          <p class="empty-subtitle">
            {{ filterDocumentId ? 'Aucun échange lié à ce document.' : 'Démarrez une discussion avec votre équipe ci-dessous.' }}
          </p>
        </div>

        <div v-else class="threads-stack">
          <article
            v-for="thread in threads"
            :key="thread.root.id"
            class="thread-block"
          >
            <!-- Commentaire racine -->
            <div class="comment-item">
              <div class="avatar-circle" aria-hidden="true">{{ thread.root.author_initials }}</div>
              <div class="comment-content-col">
                <div class="comment-meta">
                  <span class="author-name">{{ thread.root.author_name }}</span>
                  <span class="meta-sep">·</span>
                  <time class="comment-time" :title="formatFullDate(thread.root.created_at)">
                    {{ formatRelativeDate(thread.root.created_at) }}
                  </time>
                  <template v-if="thread.root.is_edited">
                    <span class="meta-sep">·</span>
                    <span class="edited-note">modifié</span>
                  </template>
                </div>

                <button
                  v-if="thread.root.document && thread.root.document_title"
                  type="button"
                  class="doc-ref-link"
                  @click="onClickDocumentRef(thread.root.document)"
                >
                  Document : {{ thread.root.document_title }}
                </button>

                <!-- Mode édition -->
                <div v-if="editingId === thread.root.id" class="inline-edit-box">
                  <textarea
                    v-model="editingContent"
                    rows="3"
                    class="comment-textarea"
                    :disabled="isSubmitting"
                    @keydown.ctrl.enter.prevent="saveEdit(thread.root.id)"
                    @keydown.meta.enter.prevent="saveEdit(thread.root.id)"
                  ></textarea>
                  <div class="inline-edit-actions">
                    <button type="button" class="btn-subtle" :disabled="isSubmitting" @click="cancelEdit">
                      Annuler
                    </button>
                    <button
                      type="button"
                      class="btn-send"
                      :disabled="!editingContent.trim() || isSubmitting"
                      @click="saveEdit(thread.root.id)"
                    >
                      Enregistrer
                    </button>
                  </div>
                </div>

                <!-- Texte du commentaire -->
                <p v-else class="comment-text">{{ thread.root.content }}</p>

                <!-- Actions discrètes -->
                <div v-if="editingId !== thread.root.id" class="comment-actions">
                  <button type="button" class="text-action" @click="startReply(thread.root)">
                    Répondre
                  </button>
                  <button
                    v-if="thread.root.can_edit"
                    type="button"
                    class="text-action"
                    @click="startEdit(thread.root)"
                  >
                    Modifier
                  </button>

                  <template v-if="thread.root.can_delete">
                    <template v-if="confirmDeleteId === thread.root.id">
                      <span class="confirm-prompt">Supprimer ?</span>
                      <button
                        type="button"
                        class="text-action is-danger"
                        :disabled="isSubmitting"
                        @click="confirmDelete(thread.root.id)"
                      >
                        Confirmer
                      </button>
                      <button type="button" class="text-action" @click="confirmDeleteId = null">
                        Annuler
                      </button>
                    </template>
                    <button
                      v-else
                      type="button"
                      class="text-action is-danger"
                      @click="confirmDeleteId = thread.root.id"
                    >
                      Supprimer
                    </button>
                  </template>
                </div>
              </div>
            </div>

            <!-- Réponses (1 niveau d'indentation avec filet vertical fin) -->
            <div v-if="thread.replies.length > 0" class="replies-list">
              <div
                v-for="reply in thread.replies"
                :key="reply.id"
                class="comment-item is-reply"
              >
                <div class="avatar-circle is-small" aria-hidden="true">{{ reply.author_initials }}</div>
                <div class="comment-content-col">
                  <div class="comment-meta">
                    <span class="author-name">{{ reply.author_name }}</span>
                    <span class="meta-sep">·</span>
                    <time class="comment-time" :title="formatFullDate(reply.created_at)">
                      {{ formatRelativeDate(reply.created_at) }}
                    </time>
                    <template v-if="reply.is_edited">
                      <span class="meta-sep">·</span>
                      <span class="edited-note">modifié</span>
                    </template>
                  </div>

                  <div v-if="editingId === reply.id" class="inline-edit-box">
                    <textarea
                      v-model="editingContent"
                      rows="2"
                      class="comment-textarea"
                      :disabled="isSubmitting"
                      @keydown.ctrl.enter.prevent="saveEdit(reply.id)"
                      @keydown.meta.enter.prevent="saveEdit(reply.id)"
                    ></textarea>
                    <div class="inline-edit-actions">
                      <button type="button" class="btn-subtle" :disabled="isSubmitting" @click="cancelEdit">
                        Annuler
                      </button>
                      <button
                        type="button"
                        class="btn-send"
                        :disabled="!editingContent.trim() || isSubmitting"
                        @click="saveEdit(reply.id)"
                      >
                        Enregistrer
                      </button>
                    </div>
                  </div>

                  <p v-else class="comment-text">{{ reply.content }}</p>

                  <div v-if="editingId !== reply.id" class="comment-actions">
                    <button
                      v-if="reply.can_edit"
                      type="button"
                      class="text-action"
                      @click="startEdit(reply)"
                    >
                      Modifier
                    </button>

                    <template v-if="reply.can_delete">
                      <template v-if="confirmDeleteId === reply.id">
                        <span class="confirm-prompt">Supprimer ?</span>
                        <button
                          type="button"
                          class="text-action is-danger"
                          :disabled="isSubmitting"
                          @click="confirmDelete(reply.id)"
                        >
                          Confirmer
                        </button>
                        <button type="button" class="text-action" @click="confirmDeleteId = null">
                          Annuler
                        </button>
                      </template>
                      <button
                        v-else
                        type="button"
                        class="text-action is-danger"
                        @click="confirmDeleteId = reply.id"
                      >
                        Supprimer
                      </button>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </article>
        </div>
      </div>

      <!-- Zone de rédaction fixe en bas -->
      <footer class="composer-area">
        <div v-if="replyingTo" class="replying-banner">
          <span>En réponse à <strong>{{ replyingTo.author_name }}</strong></span>
          <button type="button" class="text-action" @click="replyingTo = null">Annuler</button>
        </div>

        <div v-if="!replyingTo && documents.length > 0" class="composer-doc-row">
          <label for="comment-target-doc" class="composer-doc-label">Objet</label>
          <select
            id="comment-target-doc"
            v-model="composeDocumentId"
            class="composer-doc-select"
            :disabled="isSubmitting"
          >
            <option :value="null">Commentaire général sur le dossier</option>
            <option v-for="doc in documents" :key="doc.id" :value="doc.id">
              Document : {{ doc.title || doc.file_name }}
            </option>
          </select>
        </div>

        <textarea
          ref="composerInputRef"
          v-model="draftContent"
          rows="3"
          class="comment-textarea"
          placeholder="Écrire un commentaire… (Ctrl + Entrée pour envoyer)"
          :disabled="isSubmitting"
          @keydown.ctrl.enter.prevent="submitComment"
          @keydown.meta.enter.prevent="submitComment"
        ></textarea>

        <div class="composer-footer">
          <span class="char-hint">{{ draftContent.trim().length }} / 4000</span>
          <button
            type="button"
            class="btn-send"
            :disabled="!draftContent.trim() || isSubmitting"
            @click="submitComment"
          >
            {{ isSubmitting ? 'Envoi...' : replyingTo ? 'Répondre' : 'Envoyer' }}
          </button>
        </div>
      </footer>
    </template>
  </aside>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue';
import { useCommentStore, type AffairComment, type UnreadCommentPreview } from '../../../stores/commentStore';
import type { DossierDocument } from '../../../stores/documentStore';
import LogoLoader from '../../tools/LogoLoader.vue';

const props = withDefaults(
  defineProps<{
    isOpen: boolean;
    affairId: string;
    documents?: DossierDocument[];
    initialDocumentId?: string | null;
    focusKey?: number;
    unreadCount?: number;
    latestUnread?: UnreadCommentPreview | null;
    canShare?: boolean;
  }>(),
  {
    documents: () => [],
    initialDocumentId: null,
    focusKey: 0,
    unreadCount: 0,
    latestUnread: null,
    canShare: true,
  }
);

const emit = defineEmits<{
  (e: 'toggle'): void;
  (e: 'share'): void;
  (e: 'openDocument', documentId: string): void;
}>();

const commentStore = useCommentStore();

const filterDocumentId = ref<string | null>(null);
const composeDocumentId = ref<string | null>(null);
const draftContent = ref('');
const replyingTo = ref<AffairComment | null>(null);
const editingId = ref<string | null>(null);
const editingContent = ref('');
const confirmDeleteId = ref<string | null>(null);

const listRef = ref<HTMLDivElement | null>(null);
const composerInputRef = ref<HTMLTextAreaElement | null>(null);

const isLoading = computed(() => commentStore.isLoading);
const isSubmitting = computed(() => commentStore.isSubmitting);
const errorMessage = computed(() => commentStore.errorMessage);
const totalCount = computed(() => commentStore.getCommentCount(props.affairId));
const threads = computed(() => commentStore.getThreads(props.affairId, filterDocumentId.value));

watch(
  () => props.affairId,
  () => {
    filterDocumentId.value = null;
    composeDocumentId.value = null;
    draftContent.value = '';
    replyingTo.value = null;
    editingId.value = null;
    editingContent.value = '';
    confirmDeleteId.value = null;
  }
);

watch(
  () => props.focusKey,
  async () => {
    filterDocumentId.value = props.initialDocumentId ?? null;
    composeDocumentId.value = props.initialDocumentId ?? null;
    confirmDeleteId.value = null;
    editingId.value = null;
    replyingTo.value = null;
    await nextTick();
    composerInputRef.value?.focus();
  }
);

watch(
  () => filterDocumentId.value,
  (val) => {
    if (!replyingTo.value) {
      composeDocumentId.value = val;
    }
  }
);

async function submitComment() {
  const text = draftContent.value.trim();
  if (!text || isSubmitting.value) return;

  const created = await commentStore.addComment(props.affairId, {
    content: text,
    document: replyingTo.value ? replyingTo.value.document : composeDocumentId.value,
    parent: replyingTo.value ? replyingTo.value.id : null,
  });

  if (created) {
    draftContent.value = '';
    replyingTo.value = null;
    await nextTick();
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight;
    }
  }
}

async function startReply(comment: AffairComment) {
  editingId.value = null;
  confirmDeleteId.value = null;
  replyingTo.value = comment;
  await nextTick();
  composerInputRef.value?.focus();
}

function startEdit(comment: AffairComment) {
  replyingTo.value = null;
  confirmDeleteId.value = null;
  editingId.value = comment.id;
  editingContent.value = comment.content;
}

function cancelEdit() {
  editingId.value = null;
  editingContent.value = '';
}

async function saveEdit(commentId: string) {
  const text = editingContent.value.trim();
  if (!text || isSubmitting.value) return;
  const ok = await commentStore.updateComment(props.affairId, commentId, text);
  if (ok) {
    cancelEdit();
  }
}

async function confirmDelete(commentId: string) {
  const ok = await commentStore.deleteComment(props.affairId, commentId);
  if (ok) {
    confirmDeleteId.value = null;
    if (replyingTo.value?.id === commentId) {
      replyingTo.value = null;
    }
  }
}

function onClickDocumentRef(documentId: string) {
  emit('openDocument', documentId);
}

function formatRelativeDate(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  const diffSec = Math.floor((Date.now() - date.getTime()) / 1000);
  if (diffSec < 60) return "à l'instant";
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `il y a ${diffMin} min`;
  const diffHour = Math.floor(diffMin / 60);
  if (diffHour < 24) return `il y a ${diffHour} h`;
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatFullDate(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  return date.toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' });
}
</script>

<style scoped>
.comments-sidebar {
  width: 340px;
  flex-shrink: 0;
  height: 100%;
  min-height: 0;
  background: #ffffff;
  border-left: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.comments-sidebar.is-collapsed {
  width: 56px;
  background: #fafafa;
}

.collapsed-rail {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.65rem;
  padding-top: 0.95rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.95rem 1.15rem;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.panel-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
}

.comment-icon-btn {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #475569;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.comment-icon-btn.has-unread {
  border-color: var(--primary-color, #005792);
  color: var(--primary-color, #005792);
  background: #f0f7ff;
}

.unread-dot-count {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: 999px;
  background: #dc2626;
  color: #ffffff;
  font-size: 0.66rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fafafa;
  line-height: 1;
}

.comment-icon-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
  border-color: #cbd5e1;
}

.comment-icon-btn.is-active {
  color: var(--primary-color, #005792);
  border-color: #cbd5e1;
}

.comment-icon-svg {
  width: 22px;
  height: 22px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 1.1rem;
  border-bottom: 1px solid #f1f5f9;
  background: #fafafa;
  flex-shrink: 0;
}

.filter-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  white-space: nowrap;
}

.filter-select {
  flex: 1;
  min-width: 0;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.36rem 0.55rem;
  font-size: 0.82rem;
  color: #1e293b;
  background: #ffffff;
  outline: none;
}

.filter-select:focus {
  border-color: var(--primary-color, #005792);
}

.error-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.6rem 1.1rem;
  border-bottom: 1px solid #fecaca;
  background: #fef2f2;
  color: #b91c1c;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.comments-list-area {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0.45rem 1.1rem 1rem;
}

.state-box,
.empty-box {
  height: 100%;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 1.5rem 0.75rem;
}

.empty-title {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
  color: #1e293b;
}

.empty-subtitle {
  margin: 0.35rem 0 0;
  font-size: 0.8rem;
  color: #64748b;
  max-width: 260px;
}

.threads-stack {
  display: flex;
  flex-direction: column;
}

.thread-block {
  padding: 0.9rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.thread-block:last-child {
  border-bottom: none;
}

.comment-item {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
}

.avatar-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #334155;
  font-size: 0.72rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-circle.is-small {
  width: 24px;
  height: 24px;
  font-size: 0.66rem;
}

.comment-content-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.22rem;
}

.comment-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.3rem;
  font-size: 0.78rem;
}

.author-name {
  font-weight: 600;
  color: #0f172a;
}

.meta-sep {
  color: #cbd5e1;
}

.comment-time,
.edited-note {
  color: #64748b;
  font-size: 0.75rem;
}

.doc-ref-link {
  align-self: flex-start;
  background: none;
  border: none;
  padding: 0;
  margin: 0.05rem 0;
  font-size: 0.76rem;
  color: var(--primary-color, #005792);
  cursor: pointer;
  text-align: left;
}

.doc-ref-link:hover {
  text-decoration: underline;
}

.comment-text {
  margin: 0.1rem 0 0;
  font-size: 0.87rem;
  line-height: 1.5;
  color: #1e293b;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.comment-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.7rem;
  margin-top: 0.22rem;
}

.text-action {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.76rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
}

.text-action:hover:not(:disabled) {
  color: #0f172a;
  text-decoration: underline;
}

.text-action.is-danger:hover:not(:disabled) {
  color: #dc2626;
}

.text-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-prompt {
  font-size: 0.75rem;
  color: #64748b;
}

.replies-list {
  margin-top: 0.75rem;
  margin-left: 0.85rem;
  padding-left: 0.8rem;
  border-left: 1.5px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.inline-edit-box {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin-top: 0.2rem;
}

.inline-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.45rem;
}

.composer-area {
  padding: 0.85rem 1.1rem 1rem;
  border-top: 1px solid #e5e7eb;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-shrink: 0;
}

.replying-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.76rem;
  color: #475569;
  padding-bottom: 0.15rem;
}

.composer-doc-row {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.composer-doc-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}

.composer-doc-select {
  flex: 1;
  min-width: 0;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.34rem 0.5rem;
  font-size: 0.78rem;
  color: #334155;
  background: #f8fafc;
  outline: none;
}

.composer-doc-select:focus {
  border-color: var(--primary-color, #005792);
  background: #ffffff;
}

.comment-textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 0.6rem 0.75rem;
  font-size: 0.85rem;
  line-height: 1.45;
  color: #0f172a;
  background: #f9fafb;
  resize: vertical;
  outline: none;
  font-family: inherit;
}

.comment-textarea:focus {
  border-color: var(--primary-color, #005792);
  background: #ffffff;
}

.composer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.char-hint {
  font-size: 0.72rem;
  color: #94a3b8;
}

.btn-subtle {
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #475569;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-subtle:hover:not(:disabled) {
  background: #f8fafc;
}

.btn-send {
  padding: 0.45rem 1rem;
  border-radius: 8px;
  border: none;
  background: var(--primary-color, #005792);
  color: #ffffff;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-send:hover:not(:disabled) {
  background: var(--primary-color-dark, #00456b);
}

.btn-send:disabled,
.btn-subtle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 1100px) {
  .comments-sidebar:not(.is-collapsed) {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    z-index: 50;
    box-shadow: -8px 0 24px rgba(15, 23, 42, 0.12);
  }
}
</style>
