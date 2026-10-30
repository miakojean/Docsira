import { defineStore } from 'pinia';
import { ref } from 'vue';
import { load } from '@tauri-apps/plugin-store';
import type { DossierDocument } from './documentStore';

export interface AffairSubfolder {
  id: string;
  affairId: string;
  name: string;
  parentId: string | null;
  createdAt: string;
}

export const useAffairFolderStore = defineStore('affairFolders', () => {
  const folders = ref<AffairSubfolder[]>([]);
  // map: documentId -> folderId
  const docFolderMap = ref<Record<string, string>>({});
  const isLoaded = ref(false);

  // Persistence helpers
  async function loadStore() {
    try {
      const store = await load('affairFoldersStore.json', { autoSave: false });
      const savedFolders = await store.get<AffairSubfolder[]>('folders');
      const savedMap = await store.get<Record<string, string>>('docFolderMap');
      if (Array.isArray(savedFolders)) folders.value = savedFolders;
      if (savedMap && typeof savedMap === 'object') docFolderMap.value = savedMap;
      isLoaded.value = true;
      return;
    } catch {
      // Fallback localStorage si Tauri n'est pas dispo
    }

    try {
      const localFolders = localStorage.getItem('docsira_affair_folders');
      const localMap = localStorage.getItem('docsira_doc_folder_map');
      if (localFolders) folders.value = JSON.parse(localFolders);
      if (localMap) docFolderMap.value = JSON.parse(localMap);
    } catch (e) {
      console.warn('Erreur chargement local des sous-dossiers :', e);
    }
    isLoaded.value = true;
  }

  async function saveStore() {
    try {
      localStorage.setItem('docsira_affair_folders', JSON.stringify(folders.value));
      localStorage.setItem('docsira_doc_folder_map', JSON.stringify(docFolderMap.value));
    } catch (e) {
      console.warn('Erreur sauvegarde localStorage :', e);
    }

    try {
      const store = await load('affairFoldersStore.json', { autoSave: false });
      await store.set('folders', folders.value);
      await store.set('docFolderMap', docFolderMap.value);
      await store.save();
    } catch {
      // Ignore if Tauri store is not accessible
    }
  }

  function createFolder(affairId: string, name: string, parentId: string | null = null): AffairSubfolder {
    const trimmed = name.trim();
    if (!trimmed) throw new Error('Le nom du dossier est obligatoire');

    const newFolder: AffairSubfolder = {
      id: `subfolder_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
      affairId: String(affairId),
      name: trimmed,
      parentId: parentId ? String(parentId) : null,
      createdAt: new Date().toISOString(),
    };

    folders.value.push(newFolder);
    saveStore();
    return newFolder;
  }

  function renameFolder(folderId: string, newName: string) {
    const trimmed = newName.trim();
    if (!trimmed) return;
    const target = folders.value.find((f) => f.id === folderId);
    if (target) {
      target.name = trimmed;
      saveStore();
    }
  }

  function deleteFolder(folderId: string) {
    // Récupérer récursivement tous les sous-dossiers enfants
    const idsToDelete = new Set<string>([folderId]);
    let foundMore = true;
    while (foundMore) {
      foundMore = false;
      for (const f of folders.value) {
        if (f.parentId && idsToDelete.has(f.parentId) && !idsToDelete.has(f.id)) {
          idsToDelete.add(f.id);
          foundMore = true;
        }
      }
    }

    // Les documents associés reviennent à la racine (pas de suppression backend !)
    for (const [docId, fId] of Object.entries(docFolderMap.value)) {
      if (idsToDelete.has(fId)) {
        delete docFolderMap.value[docId];
      }
    }

    // Supprimer les dossiers de la liste
    folders.value = folders.value.filter((f) => !idsToDelete.has(f.id));
    saveStore();
  }

  function assignDocToFolder(docId: string, folderId: string | null) {
    if (!folderId) {
      delete docFolderMap.value[docId];
    } else {
      docFolderMap.value[docId] = folderId;
    }
    saveStore();
  }

  function getSubfolders(affairId: string, parentId: string | null = null): AffairSubfolder[] {
    return folders.value.filter(
      (f) => String(f.affairId) === String(affairId) && (f.parentId ?? null) === (parentId ?? null)
    );
  }

  function getFolder(folderId: string | null): AffairSubfolder | null {
    if (!folderId) return null;
    return folders.value.find((f) => f.id === folderId) ?? null;
  }

  function getFolderPath(folderId: string | null): AffairSubfolder[] {
    const path: AffairSubfolder[] = [];
    let cur = getFolder(folderId);
    while (cur) {
      path.unshift(cur);
      cur = cur.parentId ? getFolder(cur.parentId) : null;
    }
    return path;
  }

  function getFolderDocuments(affairId: string, folderId: string | null, allDocs: DossierDocument[]): DossierDocument[] {
    const affairDocs = allDocs.filter((d) => String(d.affair) === String(affairId));
    if (!folderId) {
      // Racine : documents sans dossier assigné (ou dont le dossier assigné n'existe plus)
      const existingFolderIds = new Set(
        folders.value.filter((f) => String(f.affairId) === String(affairId)).map((f) => f.id)
      );
      return affairDocs.filter((d) => {
        const mapped = docFolderMap.value[d.id];
        return !mapped || !existingFolderIds.has(mapped);
      });
    }
    return affairDocs.filter((d) => docFolderMap.value[d.id] === folderId);
  }

  function getDocCount(folderId: string, allDocs: DossierDocument[]): number {
    return allDocs.filter((d) => docFolderMap.value[d.id] === folderId).length;
  }

  return {
    folders,
    docFolderMap,
    isLoaded,
    loadStore,
    saveStore,
    createFolder,
    renameFolder,
    deleteFolder,
    assignDocToFolder,
    getSubfolders,
    getFolder,
    getFolderPath,
    getFolderDocuments,
    getDocCount,
  };
});
