import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "../services/api";
import type { ClientListItem } from "./clientStore";

/** Dossier (Affair) renvoyé par GET /affairs/ (AffairSerializer). */
export interface Dossier {
  id: string;
  reference_affair: string;
  title: string;
  type_affair: string;
  statut: string;
  creation_date: string;
  client: ClientListItem | null;
  documents_count?: number;
  /** Extensions des derniers documents (max 3), pour l'aperçu du dossier. */
  documents_preview?: string[];
}

/** Récupère toutes les pages d'un endpoint DRF paginé (ou une simple liste). */
async function fetchAllPages(url: string): Promise<Dossier[] | null> {
  const items: Dossier[] = [];
  const separator = url.includes("?") ? "&" : "?";
  let page = 1;
  for (;;) {
    const response = await api(`${url}${separator}page=${page}`, "GET");
    if (!response.ok) return null;
    const data = await response.json();
    if (Array.isArray(data)) return data;
    items.push(...(data.results ?? []));
    if (!data.next) return items;
    page += 1;
  }
}

export interface DossierPayload {
  title: string;
  client_id: string;
  type_affair?: string;
}

export const useClientDossierStore = defineStore("clientDossier", () => {
  // clientId -> dossiers du client
  const dossiersByClient = ref<Record<string, Dossier[]>>({});
  // Tous les dossiers du cabinet (page workspace)
  const allDossiers = ref<Dossier[]>([]);
  const isLoading = ref(false);
  const errorMessage = ref("");
  const fieldErrors = ref<Record<string, string>>({});

  async function fetchAllDossiers() {
    isLoading.value = true;
    errorMessage.value = "";
    try {
      const items = await fetchAllPages("/affairs/");
      if (!items) {
        errorMessage.value = "Impossible de charger les dossiers";
        return false;
      }
      allDossiers.value = items;
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchClientDossiers(clientId: string) {
    isLoading.value = true;
    errorMessage.value = "";
    try {
      const items = await fetchAllPages(`/affairs/?client=${clientId}`);
      if (!items) {
        errorMessage.value = "Impossible de charger les dossiers";
        return false;
      }
      dossiersByClient.value = {
        ...dossiersByClient.value,
        [clientId]: items,
      };
      // Debugging
      console.log("Dossier du client", dossiersByClient.value)
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /** Charge un dossier précis (page de détail). */
  async function fetchDossier(id: string): Promise<Dossier | null> {
    try {
      const response = await api(`/affairs/${id}/`, "GET");
      if (!response.ok) return null;
      return (await response.json()) as Dossier;
    } catch (error) {
      console.error(error);
      return null;
    }
  }

  async function addDossier(payload: DossierPayload) {
    isLoading.value = true;
    errorMessage.value = "";
    fieldErrors.value = {};
    try {
      const response = await api("/affairs/", "POST", {
        type_affair: "AUTRE",
        ...payload,
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        for (const [key, value] of Object.entries(data ?? {})) {
          fieldErrors.value[key] = Array.isArray(value) ? String(value[0]) : String(value);
        }
        errorMessage.value = "Création du dossier impossible";
        return false;
      }
      const current = dossiersByClient.value[payload.client_id] ?? [];
      dossiersByClient.value = {
        ...dossiersByClient.value,
        [payload.client_id]: [data, ...current],
      };
      allDossiers.value = [data, ...allDossiers.value];
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateDossier(
    id: string,
    payload: { title?: string; client_id?: string; type_affair?: string; statut?: string }
  ) {
    isLoading.value = true;
    errorMessage.value = "";
    fieldErrors.value = {};
    try {
      const response = await api(`/affairs/${id}/`, "PATCH", payload);
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        for (const [key, value] of Object.entries(data ?? {})) {
          fieldErrors.value[key] = Array.isArray(value) ? String(value[0]) : String(value);
        }
        errorMessage.value = "Modification du dossier impossible";
        return false;
      }

      // Mise à jour dans allDossiers
      const idx = allDossiers.value.findIndex((d) => d.id === id);
      if (idx !== -1) {
        allDossiers.value[idx] = data;
      }

      // Mise à jour dans dossiersByClient
      for (const clientId of Object.keys(dossiersByClient.value)) {
        dossiersByClient.value[clientId] = dossiersByClient.value[clientId].filter((d) => d.id !== id);
      }
      if (data.client?.id) {
        const cId = data.client.id;
        if (dossiersByClient.value[cId]) {
          dossiersByClient.value[cId] = [data, ...dossiersByClient.value[cId]];
        }
      }
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteDossier(id: string) {
    isLoading.value = true;
    errorMessage.value = "";
    try {
      const response = await api(`/affairs/${id}/`, "DELETE");
      if (!response.ok) {
        errorMessage.value = "Suppression du dossier impossible";
        return false;
      }
      allDossiers.value = allDossiers.value.filter((d) => d.id !== id);
      for (const clientId of Object.keys(dossiersByClient.value)) {
        dossiersByClient.value[clientId] = dossiersByClient.value[clientId].filter((d) => d.id !== id);
      }
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    dossiersByClient,
    allDossiers,
    isLoading,
    errorMessage,
    fieldErrors,
    fetchAllDossiers,
    fetchClientDossiers,
    fetchDossier,
    addDossier,
    updateDossier,
    deleteDossier,
  };
});
