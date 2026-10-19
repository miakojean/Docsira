import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "../services/api";

/** Document renvoyé par /affairs/<id>/documents/ (DocumentSerializer). */
export interface DossierDocument {
  id: string;
  affair: string;
  title: string;
  file_name: string;
  extension: string;
  size: number;
  download_url: string;
  uploaded_at: string;
  /** Document dont celui-ci découle (null pour la racine). */
  parent: string | null;
  relation: DocumentRelation;
  version: number;
  pos_x: number | null;
  pos_y: number | null;
}

export type DocumentRelation = "INITIAL" | "ADDED" | "UPDATED";

export const useDocumentStore = defineStore("documents", () => {
  const documents = ref<DossierDocument[]>([]);
  const isLoading = ref(false);
  const isUploading = ref(false);
  const errorMessage = ref("");

  async function fetchDocuments(affairId: string) {
    isLoading.value = true;
    errorMessage.value = "";
    try {
      const response = await api(`/affairs/${affairId}/documents/`, "GET");
      if (!response.ok) {
        errorMessage.value = "Impossible de charger les documents";
        documents.value = [];
        return false;
      }
      const data = await response.json();
      documents.value = Array.isArray(data) ? data : (data.results ?? []);
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /** Envoie des fichiers choisis sur le disque dur de l'utilisateur. */
  async function uploadDocuments(affairId: string, files: File[]) {
    if (files.length === 0) return false;
    isUploading.value = true;
    errorMessage.value = "";
    try {
      const form = new FormData();
      for (const file of files) form.append("files", file, file.name);

      const response = await api(`/affairs/${affairId}/documents/`, "POST", form);
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        errorMessage.value = data?.error ?? "Import des documents impossible";
        return false;
      }
      documents.value = [...(Array.isArray(data) ? data : [data]), ...documents.value];
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    } finally {
      isUploading.value = false;
    }
  }

  /** Dépose une nouvelle version d'un document : elle est reliée à l'ancienne. */
  async function uploadNewVersion(id: string, file: File, posX?: number, posY?: number) {
    isUploading.value = true;
    errorMessage.value = "";
    try {
      const form = new FormData();
      form.append("file", file, file.name);
      if (posX != null && !isNaN(posX)) form.append("pos_x", String(Math.round(posX)));
      if (posY != null && !isNaN(posY)) form.append("pos_y", String(Math.round(posY)));

      const response = await api(`/affairs/documents/${id}/versions/`, "POST", form);
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        errorMessage.value = data?.error ?? "Mise à jour du document impossible";
        return null;
      }
      const newDoc = data as DossierDocument;
      if (!documents.value.some((d) => d.id === newDoc.id)) {
        documents.value = [newDoc, ...documents.value];
      }
      return newDoc;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return null;
    } finally {
      isUploading.value = false;
    }
  }

  /** Mémorise la position d'un document sur l'espace de travail. */
  async function moveDocument(id: string, x: number, y: number) {
    const local = documents.value.find((d) => d.id === id);
    if (local) {
      local.pos_x = x;
      local.pos_y = y;
    }
    try {
      await api(`/affairs/documents/${id}/`, "PATCH", { pos_x: x, pos_y: y });
    } catch (error) {
      console.error(error);
    }
  }

  async function renameDocument(id: string, title: string) {
    errorMessage.value = "";
    try {
      const response = await api(`/affairs/documents/${id}/`, "PATCH", { title });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        errorMessage.value = data?.title?.[0] ?? "Renommage impossible";
        return false;
      }
      documents.value = documents.value.map((d) => (d.id === id ? data : d));
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    }
  }

  async function deleteDocument(id: string) {
    errorMessage.value = "";
    try {
      const response = await api(`/affairs/documents/${id}/`, "DELETE");
      if (!response.ok) {
        errorMessage.value = "Suppression du document impossible";
        return false;
      }
      // Le serveur recolle la chaîne : les suivants se rattachent au précédent
      const removed = documents.value.find((d) => d.id === id);
      documents.value = documents.value
        .filter((d) => d.id !== id)
        .map((d) => (d.parent === id ? { ...d, parent: removed?.parent ?? null } : d));
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    }
  }

  /** Télécharge le contenu binaire (endpoint authentifié). */
  async function fetchFileBlob(id: string): Promise<Blob | null> {
    try {
      const response = await api(`/affairs/documents/${id}/download/`, "GET");
      if (!response.ok) return null;
      return await response.blob();
    } catch (error) {
      console.error(error);
      return null;
    }
  }

  return {
    documents,
    isLoading,
    isUploading,
    errorMessage,
    fetchDocuments,
    uploadDocuments,
    uploadNewVersion,
    moveDocument,
    renameDocument,
    deleteDocument,
    fetchFileBlob,
  };
});
