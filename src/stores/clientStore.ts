import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "../services/api";

export type TypeClient = "PERSONNE_PHYSIQUE" | "PERSONNE_MORALE";
export type StatutClient = "ACTIF" | "INACTIF" | "PROSPECT" | "ARCHIVE";

// Correspond à ClientSerializer (le GET /Client renvoie un tableau brut)
export interface ClientListItem {
  id: string; // UUID
  reference_client: string;
  type_client: TypeClient;
  statut: StatutClient;
  nom_complet: string;
  nom: string;
  prenoms: string;
  raison_sociale: string;
  telephone_1: string;
  telephone_2: string;
  email: string;
  adresse: string;
  ville: string;
  commune: string;
  pays?: string;
  charge_de_clientele: number | string | null;
  date_creation: string;
  date_premier_contact: string | null;
}

export interface ClientPayload {
  type_client: TypeClient;
  statut?: StatutClient;
  nom?: string;
  prenoms?: string;
  date_naissance?: string | null;
  lieu_naissance?: string;
  raison_sociale?: string;
  forme_juridique?: string;
  numero_rccm?: string;
  numero_cc?: string;
  representant_legal_nom?: string;
  representant_legal_fonction?: string;
  telephone_1: string;
  telephone_2?: string;
  email?: string;
  adresse?: string;
  ville?: string;
  commune?: string;
  pays?: string;
  notes?: string;
}

export const useClientStore = defineStore("client", () => {
  const clients = ref<ClientListItem[]>([]);
  const isLoading = ref(false);
  const fieldErrors = ref<Record<string, string>>({});
  const errorMessage = ref("");

  async function fetchClients() {
    isLoading.value = true;
    errorMessage.value = "";
    try {
      const response = await api("/Client/", "GET");
      if (!response.ok) {
        errorMessage.value = "Impossible de charger la liste des clients";
        return false;
      }
      const data = await response.json();
      // Le backend renvoie directement un tableau ; on garde une tolérance sur l'ancien format
      clients.value = Array.isArray(data) ? data : (data?.clients ?? []);
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function addClient(payload: ClientPayload) {
    isLoading.value = true;
    errorMessage.value = "";
    fieldErrors.value = {};
    try {
      // Les champs vides sont retirés pour ne pas violer les validateurs (dates, email...)
      const cleaned = Object.fromEntries(
        Object.entries(payload).filter(([, v]) => v !== "" && v !== null && v !== undefined),
      );
      const response = await api("/Client/", "POST", cleaned);
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const errors = data?.errors ?? {};
        for (const [key, value] of Object.entries(errors)) {
          fieldErrors.value[key] = Array.isArray(value) ? String(value[0]) : String(value);
        }
        errorMessage.value =
          fieldErrors.value.non_field_errors || data?.message || "Création du client impossible";
        return false;
      }
      // Ajout optimiste en tête de liste puis resynchronisation
      if (data?.client) clients.value.unshift(data.client);
      await fetchClients();
      return true;
    } catch (error) {
      console.error(error);
      errorMessage.value = "Erreur serveur, veuillez réessayer plus tard";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  return { clients, isLoading, fieldErrors, errorMessage, fetchClients, addClient };
});
