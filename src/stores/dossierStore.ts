import { defineStore } from "pinia";
import { ref } from "vue";
import type { ClientPayload } from "./clientStore";

/**
 * Dossier du workspace.
 * ⚠️ DONNÉES STATIQUES : le serveur workspace (backend + frontend) n'est pas encore
 * disponible. Quand il le sera, il suffira de remplacer `fetchWorkspaceDossiers`
 * par un appel API (ex: api("/Workspace/dossiers/", "GET")) et de persister les
 * liens côté serveur dans `linkDossier` / `unlinkDossier`.
 */
export interface WorkspaceDossier {
  id: string;
  client?: ClientPayload;
  name: string;
  reference: string;
  fileCount: number;
  updatedAt: string; // ISO
}

const STATIC_WORKSPACE_DOSSIERS: WorkspaceDossier[] = [
  { id: "ws-001", name: "Contrat de bail commercial", reference: "DOS-2026-001", fileCount: 12, updatedAt: "2026-09-28T10:15:00Z" },
  { id: "ws-002", name: "Litige foncier – Cocody", reference: "DOS-2026-002", fileCount: 27, updatedAt: "2026-10-02T14:40:00Z" },
  { id: "ws-003", name: "Constitution de société SARL", reference: "DOS-2026-003", fileCount: 8, updatedAt: "2026-10-05T09:05:00Z" },
  { id: "ws-004", name: "Succession famille Koné", reference: "DOS-2026-004", fileCount: 19, updatedAt: "2026-10-07T16:20:00Z" },
  { id: "ws-005", name: "Recouvrement de créances", reference: "DOS-2026-005", fileCount: 5, updatedAt: "2026-10-09T11:30:00Z" },
  { id: "ws-006", name: "Divorce par consentement mutuel", reference: "DOS-2026-006", fileCount: 14, updatedAt: "2026-10-10T08:50:00Z" },
];

const STORAGE_KEY = "docsira_client_dossier_links";

function loadLinks(): Record<string, string[]> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export const useClientDossierStore = defineStore("clientDossier", () => {
  const workspaceDossiers = ref<WorkspaceDossier[]>([]);
  // clientId -> liste d'ids de dossiers liés
  const links = ref<Record<string, string[]>>(loadLinks());
  const isLoading = ref(false);

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(links.value));
  }

  // Simule un appel au serveur workspace
  async function fetchWorkspaceDossiers() {
    isLoading.value = true;
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));
      workspaceDossiers.value = STATIC_WORKSPACE_DOSSIERS;
      return true;
    } finally {
      isLoading.value = false;
    }
  }

  function getLinkedDossiers(clientId: string): WorkspaceDossier[] {
    const ids = links.value[clientId] ?? [];
    return STATIC_WORKSPACE_DOSSIERS.filter((d) => ids.includes(d.id));
  }

  function linkDossier(clientId: string, dossierId: string) {
    const current = links.value[clientId] ?? [];
    if (current.includes(dossierId)) return;
    links.value = { ...links.value, [clientId]: [...current, dossierId] };
    persist();
  }

  function unlinkDossier(clientId: string, dossierId: string) {
    const current = links.value[clientId] ?? [];
    links.value = { ...links.value, [clientId]: current.filter((id) => id !== dossierId) };
    persist();
  }

  return {
    workspaceDossiers,
    links,
    isLoading,
    fetchWorkspaceDossiers,
    getLinkedDossiers,
    linkDossier,
    unlinkDossier,
  };
});
