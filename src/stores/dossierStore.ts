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
      const response = await api("/affairs/", "GET");
      if (!response.ok) {
        errorMessage.value = "Impossible de charger les dossiers";
        return false;
      }
      const data = await response.json();
      allDossiers.value = Array.isArray(data) ? data : [];
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
      const response = await api(`/affairs/?client=${clientId}`, "GET");
      if (!response.ok) {
        errorMessage.value = "Impossible de charger les dossiers";
        return false;
      }
      const data = await response.json();
      dossiersByClient.value = {
        ...dossiersByClient.value,
        [clientId]: Array.isArray(data) ? data : [],
      };
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    } finally {
      isLoading.value = false;
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
    addDossier,
    updateDossier,
    deleteDossier,
  };
});
