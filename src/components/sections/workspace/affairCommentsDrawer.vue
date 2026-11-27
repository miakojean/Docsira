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
        data-tour="affair-comments-toggle"
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
            Démarrez une discussion avec votre équipe ci-dessous.
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
                <p v-else class="comment-text">
                  <template v-for="(seg, idx) in parseCommentSegments(thread.root.content)" :key="idx">
                    <button
                      v-if="seg.type === 'doc' && seg.docId"
                      type="button"
                      class="doc-mention-chip"
                      :title="`Ouvrir ${seg.label}`"
                      @click="onClickDocumentRef(seg.docId)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="doc-mention-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                      </svg>
                      <span>{{ seg.label }}</span>
                    </button>
                    <span v-else-if="seg.type === 'doc'" class="doc-mention-chip is-missing">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="doc-mention-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                      </svg>
                      <span>{{ seg.label }}</span>
                    </span>
                    <template v-else>{{ seg.text }}</template>
                  </template>
                </p>

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

                  <p v-else class="comment-text">
                    <template v-for="(seg, idx) in parseCommentSegments(reply.content)" :key="idx">
                      <button
                        v-if="seg.type === 'doc' && seg.docId"
                        type="button"
                        class="doc-mention-chip"
                        :title="`Ouvrir ${seg.label}`"
                        @click="onClickDocumentRef(seg.docId)"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="doc-mention-icon">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                        </svg>
                        <span>{{ seg.label }}</span>
                      </button>
                      <span v-else-if="seg.type === 'doc'" class="doc-mention-chip is-missing">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="doc-mention-icon">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                        </svg>
                        <span>{{ seg.label }}</span>
                      </span>
                      <template v-else>{{ seg.text }}</template>
                    </template>
                  </p>

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

        <div class="composer-input-wrap">
          <!-- Popover d'identification de document (@) -->
          <div v-if="mentionOpen && documents.length > 0" class="mention-popover" role="listbox" aria-label="Identifier un document">
            <div class="mention-popover-header">
              <span>Identifier un document</span>
              <span class="mention-popover-hint">↑↓ · Entrée</span>
            </div>
            <div v-if="filteredMentionDocs.length === 0" class="mention-empty">
              Aucun document correspondant
            </div>
            <button
              v-for="(doc, idx) in filteredMentionDocs"
              :key="doc.id"
              type="button"
              role="option"
              :aria-selected="idx === mentionActiveIndex"
              class="mention-option"
              :class="{ 'is-active': idx === mentionActiveIndex }"
              @mousedown.prevent="selectMentionDoc(doc)"
              @mouseenter="mentionActiveIndex = idx"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="mention-option-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
              <span class="mention-option-title">{{ getDocDisplayName(doc) }}</span>
              <span v-if="doc.extension" class="mention-option-ext">{{ doc.extension.replace(/^\./, '').toUpperCase() }}</span>
            </button>
          </div>

          <textarea
            ref="composerInputRef"
            v-model="draftContent"
            rows="3"
            class="comment-textarea"
            :placeholder="documents.length > 0 ? 'Écrire un commentaire… Tapez @ pour identifier un document' : 'Écrire un commentaire… (Ctrl + Entrée pour envoyer)'"
            :disabled="isSubmitting"
            @input="updateMentionState"
            @click="updateMentionState"
            @keydown="onComposerKeydown"
            @blur="closeMentionPopover"
          ></textarea>
        </div>

        <div class="composer-footer">
          <div class="composer-footer-left">
            <button
              v-if="documents.length > 0"
              type="button"
              class="mention-trigger-btn"
              :class="{ 'is-active': mentionOpen }"
              title="Identifier un document (@)"
              aria-label="Identifier un document"
              :disabled="isSubmitting"
              @mousedown.prevent="triggerMentionPicker"
            >
              <span class="mention-at-symbol">@</span>
              <span>Document</span>
            </button>
            <span class="char-hint">{{ draftContent.trim().length }} / 4000</span>
          </div>
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
    unreadCount?: number;
    latestUnread?: UnreadCommentPreview | null;
    canShare?: boolean;
  }>(),
  {
    documents: () => [],
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

const draftContent = ref('');
const replyingTo = ref<AffairComment | null>(null);
const editingId = ref<string | null>(null);
const editingContent = ref('');
const confirmDeleteId = ref<string | null>(null);

// Mentions de documents (@)
const mentionOpen = ref(false);
const mentionQuery = ref('');
const mentionTriggerStart = ref(-1);
const mentionActiveIndex = ref(0);

const listRef = ref<HTMLDivElement | null>(null);
const composerInputRef = ref<HTMLTextAreaElement | null>(null);

const isLoading = computed(() => commentStore.isLoading);
const isSubmitting = computed(() => commentStore.isSubmitting);
const errorMessage = computed(() => commentStore.errorMessage);
const threads = computed(() => commentStore.getThreads(props.affairId));

function getDocDisplayName(doc: DossierDocument): string {
  return (doc.title || doc.file_name || 'Document').trim();
}

const filteredMentionDocs = computed(() => {
  const q = mentionQuery.value.trim().toLowerCase();
  if (!q) return props.documents;
  return props.documents.filter((doc) => {
    const title = (doc.title || '').toLowerCase();
    const fileName = (doc.file_name || '').toLowerCase();
    return title.includes(q) || fileName.includes(q);
  });
});

watch(filteredMentionDocs, (list) => {
  if (mentionActiveIndex.value >= list.length) {
    mentionActiveIndex.value = 0;
  }
});

watch(
  () => props.affairId,
  () => {
    draftContent.value = '';
    replyingTo.value = null;
    editingId.value = null;
    editingContent.value = '';
    confirmDeleteId.value = null;
    closeMentionPopover();
  }
);

function closeMentionPopover() {
  mentionOpen.value = false;
  mentionQuery.value = '';
  mentionTriggerStart.value = -1;
  mentionActiveIndex.value = 0;
}

function updateMentionState() {
  const el = composerInputRef.value;
  if (!el || props.documents.length === 0) {
    closeMentionPopover();
    return;
  }
  const cursorPos = el.selectionStart ?? draftContent.value.length;
  const textBeforeCursor = draftContent.value.slice(0, cursorPos);
  const match = textBeforeCursor.match(/(^|\s)@([^\n@\]]*)$/);
  if (!match) {
    closeMentionPopover();
    return;
  }
  const leadingSpaceLen = match[1].length;
  mentionTriggerStart.value = cursorPos - match[0].length + leadingSpaceLen;
  mentionQuery.value = match[2] ?? '';
  mentionOpen.value = true;
}

async function triggerMentionPicker() {
  if (isSubmitting.value || props.documents.length === 0) return;
  if (mentionOpen.value) {
    closeMentionPopover();
    return;
  }
  const el = composerInputRef.value;
  const current = draftContent.value;
  const start = el?.selectionStart ?? current.length;
  const end = el?.selectionEnd ?? start;
  const needsSpace = start > 0 && !/\s/.test(current[start - 1]);
  const insertion = needsSpace ? ' @' : '@';
  draftContent.value = current.slice(0, start) + insertion + current.slice(end);
  const nextCursor = start + insertion.length;
  await nextTick();
  if (el) {
    el.focus();
    el.setSelectionRange(nextCursor, nextCursor);
  }
  updateMentionState();
}

async function selectMentionDoc(doc: DossierDocument) {
  const el = composerInputRef.value;
  const current = draftContent.value;
  const cursorPos = el?.selectionStart ?? current.length;
  const replaceStart = mentionTriggerStart.value >= 0 ? mentionTriggerStart.value : cursorPos;
  const safeName = getDocDisplayName(doc).replace(/[\[\]]/g, '');
  const token = `@[${safeName}] `;
  draftContent.value = current.slice(0, replaceStart) + token + current.slice(cursorPos);
  const nextCursor = replaceStart + token.length;
  closeMentionPopover();
  await nextTick();
  if (el) {
    el.focus();
    el.setSelectionRange(nextCursor, nextCursor);
  }
}

function onComposerKeydown(event: KeyboardEvent) {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault();
    void submitComment();
    return;
  }

  if (!mentionOpen.value) return;

  if (event.key === 'Escape') {
    event.preventDefault();
    closeMentionPopover();
    return;
  }

  const list = filteredMentionDocs.value;
  if (list.length === 0) return;

  if (event.key === 'ArrowDown') {
    event.preventDefault();
    mentionActiveIndex.value = (mentionActiveIndex.value + 1) % list.length;
  } else if (event.key === 'ArrowUp') {
    event.preventDefault();
    mentionActiveIndex.value = (mentionActiveIndex.value - 1 + list.length) % list.length;
  } else if (event.key === 'Enter' || event.key === 'Tab') {
    event.preventDefault();
    const chosen = list[mentionActiveIndex.value] ?? list[0];
    if (chosen) {
      void selectMentionDoc(chosen);
    }
  }
}

type CommentSegment =
  | { type: 'text'; text: string }
  | { type: 'doc'; label: string; docId: string | null };

function parseCommentSegments(content: string): CommentSegment[] {
  if (!content) return [];
  const segments: CommentSegment[] = [];
  const regex = /@\[([^\]]+)\]/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: 'text', text: content.slice(lastIndex, match.index) });
    }
    const label = match[1].trim();
    const normalized = label.toLowerCase();
    const matchedDoc = props.documents.find(
      (d) =>
        getDocDisplayName(d).toLowerCase() === normalized ||
        (d.file_name || '').trim().toLowerCase() === normalized
    );
    segments.push({
      type: 'doc',
      label,
      docId: matchedDoc?.id ?? null,
    });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < content.length) {
    segments.push({ type: 'text', text: content.slice(lastIndex) });
  }
  return segments;
}

async function submitComment() {
  const text = draftContent.value.trim();
  if (!text || isSubmitting.value) return;

  closeMentionPopover();

  const created = await commentStore.addComment(props.affairId, {
    content: text,
    document: null,
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

.doc-mention-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.08rem 0.45rem;
  margin: 0 0.08rem;
  border-radius: 6px;
  color: var(--primary-color, #005792);
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.35;
  vertical-align: baseline;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}

.doc-mention-chip:hover {
  text-decoration: underline;
}

.doc-mention-chip.is-missing {
  background: #f1f5f9;
  border-color: #e2e8f0;
  color: #64748b;
  cursor: default;
}

.doc-mention-icon {
  width: 13px;
  height: 13px;
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

.composer-input-wrap {
  position: relative;
}

.mention-popover {
  position: absolute;
  left: 0;
  right: 0;
  bottom: calc(100% + 6px);
  max-height: 220px;
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.14);
  z-index: 30;
  padding: 0.3rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.mention-popover-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.3rem 0.5rem 0.35rem;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: #64748b;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 0.15rem;
}

.mention-popover-hint {
  font-weight: 500;
  text-transform: none;
  color: #94a3b8;
}

.mention-empty {
  padding: 0.65rem 0.5rem;
  font-size: 0.78rem;
  color: #94a3b8;
  text-align: center;
}

.mention-option {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.55rem;
  border: none;
  border-radius: 7px;
  background: transparent;
  color: #1e293b;
  font-size: 0.81rem;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.12s ease;
}

.mention-option:hover,
.mention-option.is-active {
  background: #eff6ff;
  color: var(--primary-color, #005792);
}

.mention-option-icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
  color: #64748b;
}

.mention-option.is-active .mention-option-icon {
  color: var(--primary-color, #005792);
}

.mention-option-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.mention-option-ext {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  background: #f1f5f9;
  color: #64748b;
  flex-shrink: 0;
}

.composer-footer-left {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.mention-trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.28rem 0.55rem;
  border-radius: 7px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mention-trigger-btn:hover:not(:disabled),
.mention-trigger-btn.is-active {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: var(--primary-color, #005792);
}

.mention-trigger-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mention-at-symbol {
  font-weight: 700;
  font-size: 0.82rem;
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