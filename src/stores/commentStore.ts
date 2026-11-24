import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from '../services/api';

export interface AffairComment {
  id: string;
  affair: string;
  document: string | null;
  document_title: string | null;
  parent: string | null;
  author: string;
  author_name: string;
  author_initials: string;
  content: string;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
  can_edit: boolean;
  can_delete: boolean;
}

export interface AffairCommentThread {
  root: AffairComment;
  replies: AffairComment[];
}

export interface AddCommentPayload {
  content: string;
  document?: string | null;
  parent?: string | null;
}

function extractError(data: any, fallback: string): string {
  if (!data) return fallback;
  if (typeof data.error === 'string' && data.error) return data.error;
  if (Array.isArray(data.content) && data.content[0]) return String(data.content[0]);
  if (typeof data.detail === 'string' && data.detail) return data.detail;
  return fallback;
}

export const useCommentStore = defineStore('comments', () => {
  // States
  const commentsByAffair = ref<Record<string, AffairComment[]>>({});
  const isLoading = ref(false);
  const isSubmitting = ref(false);
  const errorMessage = ref('');

  // Getters
  function getComments(affairId: string): AffairComment[] {
    return commentsByAffair.value[affairId] ?? [];
  }

  function getCommentCount(affairId: string): number {
    return getComments(affairId).length;
  }

  function getThreads(affairId: string, documentId: string | null = null): AffairCommentThread[] {
    const all = getComments(affairId);
    const byId = new Map<string, AffairComment>(all.map((c) => [c.id, c]));
    const repliesMap = new Map<string, AffairComment[]>();

    for (const c of all) {
      if (c.parent && byId.has(c.parent)) {
        const list = repliesMap.get(c.parent) ?? [];
        list.push(c);
        repliesMap.set(c.parent, list);
      }
    }

    const roots = all.filter((c) => !c.parent || !byId.has(c.parent));
    const threads = roots.map((root) => ({
      root,
      replies: repliesMap.get(root.id) ?? [],
    }));

    if (!documentId) return threads;

    return threads.filter(
      (t) =>
        t.root.document === documentId ||
        t.replies.some((reply) => reply.document === documentId)
    );
  }

  // Actions
  async function fetchComments(affairId: string): Promise<boolean> {
    if (!affairId) return false;
    isLoading.value = true;
    errorMessage.value = '';
    try {
      const response = await api(`/affairs/${affairId}/comments/`, 'GET');
      const data = await response.json().catch(() => null);
      if (!response.ok || !Array.isArray(data)) {
        errorMessage.value = extractError(data, 'Impossible de charger les commentaires');
        return false;
      }
      commentsByAffair.value = {
        ...commentsByAffair.value,
        [affairId]: data as AffairComment[],
      };
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = 'Erreur serveur lors du chargement des commentaires';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function addComment(
    affairId: string,
    payload: AddCommentPayload,
  ): Promise<AffairComment | null> {
    if (!affairId) return null;
    isSubmitting.value = true;
    errorMessage.value = '';
    try {
      const body: Record<string, unknown> = { content: payload.content };
      if (payload.document) body.document = payload.document;
      if (payload.parent) body.parent = payload.parent;

      const response = await api(`/affairs/${affairId}/comments/`, 'POST', body);
      const data = await response.json().catch(() => null);
      if (!response.ok || !data) {
        errorMessage.value = extractError(data, "Impossible d'envoyer le commentaire");
        return null;
      }

      const created = data as AffairComment;
      const current = commentsByAffair.value[affairId] ?? [];
      commentsByAffair.value = {
        ...commentsByAffair.value,
        [affairId]: [...current, created],
      };
      return created;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur lors de l'envoi du commentaire";
      return null;
    } finally {
      isSubmitting.value = false;
    }
  }

  async function updateComment(
    affairId: string,
    commentId: string,
    content: string,
  ): Promise<boolean> {
    isSubmitting.value = true;
    errorMessage.value = '';
    try {
      const response = await api(`/affairs/comments/${commentId}/`, 'PATCH', { content });
      const data = await response.json().catch(() => null);
      if (!response.ok || !data) {
        errorMessage.value = extractError(data, 'Modification du commentaire impossible');
        return false;
      }

      const updated = data as AffairComment;
      const current = commentsByAffair.value[affairId] ?? [];
      commentsByAffair.value = {
        ...commentsByAffair.value,
        [affairId]: current.map((c) => (c.id === commentId ? updated : c)),
      };
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = 'Erreur serveur lors de la modification';
      return false;
    } finally {
      isSubmitting.value = false;
    }
  }

  async function deleteComment(affairId: string, commentId: string): Promise<boolean> {
    isSubmitting.value = true;
    errorMessage.value = '';
    try {
      const response = await api(`/affairs/comments/${commentId}/`, 'DELETE');
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        errorMessage.value = extractError(data, 'Suppression du commentaire impossible');
        return false;
      }

      const current = commentsByAffair.value[affairId] ?? [];
      commentsByAffair.value = {
        ...commentsByAffair.value,
        [affairId]: current.filter((c) => c.id !== commentId && c.parent !== commentId),
      };
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = 'Erreur serveur lors de la suppression';
      return false;
    } finally {
      isSubmitting.value = false;
    }
  }

  return {
    commentsByAffair,
    isLoading,
    isSubmitting,
    errorMessage,
    getComments,
    getCommentCount,
    getThreads,
    fetchComments,
    addComment,
    updateComment,
    deleteComment,
  };
});

