import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { open as openDialog, save as saveDialog } from '@tauri-apps/plugin-dialog';
import { readFile, writeFile } from '@tauri-apps/plugin-fs';
import { useClientDossierStore, type Dossier } from '../stores/dossierStore';
import { useDocumentStore, type DossierDocument } from '../stores/documentStore';
import { useAffairFolderStore, type AffairSubfolder } from '../stores/affairFolderStore';
import type { PreviewData } from '../components/modale/filePreviewModale.vue';

export function useAffairDocuments() {
  const route = useRoute();
  const router = useRouter();
  const dossierStore = useClientDossierStore();
  const docStore = useDocumentStore();
  const folderStore = useAffairFolderStore();

  const affairId = computed(() => String(route.params.id));
  const dossier = ref<Dossier | null>(null);

  const isDraggingOver = ref(false);
  const diskFileInputRef = ref<HTMLInputElement | null>(null);

  const documents = computed(() => docStore.documents);

  // ---------- Sous-dossiers de l'affaire ----------
  const currentFolderId = ref<string | null>(null);

  // Tous les sous-dossiers de cette affaire
  const subfolders = computed<AffairSubfolder[]>(() => {
    return folderStore.folders.filter((f) => String(f.affairId) === affairId.value);
  });

  // Sous-dossiers enfants du niveau actuel
  const currentSubfolders = computed<AffairSubfolder[]>(() => {
    return folderStore.getSubfolders(affairId.value, currentFolderId.value);
  });

  // Documents du niveau actuel
  const currentDocuments = computed<DossierDocument[]>(() => {
    return folderStore.getFolderDocuments(affairId.value, currentFolderId.value, documents.value);
  });

  // Dossier actif
  const currentFolder = computed<AffairSubfolder | null>(() => {
    return folderStore.getFolder(currentFolderId.value);
  });

  // Fil d'Ariane
  const folderBreadcrumbs = computed<AffairSubfolder[]>(() => {
    return folderStore.getFolderPath(currentFolderId.value);
  });

  // État vide : ni sous-dossiers ni documents à ce niveau
  const isEmptyCurrentView = computed(() => {
    return currentSubfolders.value.length === 0 && currentDocuments.value.length === 0;
  });

  // ---------- Modale création / renommage de sous-dossier ----------
  const isFolderModalOpen = ref(false);
  const folderModalMode = ref<'create' | 'rename'>('create');
  const folderToRename = ref<AffairSubfolder | null>(null);
  const folderModalName = ref('');

  function openCreateFolder() {
    folderModalMode.value = 'create';
    folderToRename.value = null;
    folderModalName.value = '';
    isFolderModalOpen.value = true;
  }

  function openRenameFolder(folder: AffairSubfolder) {
    folderModalMode.value = 'rename';
    folderToRename.value = folder;
    folderModalName.value = folder.name;
    isFolderModalOpen.value = true;
  }

  function confirmSaveFolder(name: string) {
    if (folderModalMode.value === 'create') {
      folderStore.createFolder(affairId.value, name, currentFolderId.value);
    } else if (folderToRename.value) {
      folderStore.renameFolder(folderToRename.value.id, name);
    }
    isFolderModalOpen.value = false;
  }

  // ---------- Modale suppression de sous-dossier ----------
  const isDeleteFolderOpen = ref(false);
  const folderToDelete = ref<AffairSubfolder | null>(null);

  function openDeleteFolder(folder: AffairSubfolder) {
    folderToDelete.value = folder;
    isDeleteFolderOpen.value = true;
  }

  function confirmDeleteFolder() {
    if (!folderToDelete.value) return;
    const deletedId = folderToDelete.value.id;
    const parentId = folderToDelete.value.parentId;
    folderStore.deleteFolder(deletedId);
    if (currentFolderId.value === deletedId) {
      currentFolderId.value = parentId;
    }
    isDeleteFolderOpen.value = false;
    folderToDelete.value = null;
  }

  // ---------- Déplacement d'un document dans un sous-dossier ----------
  const isMoveDocModalOpen = ref(false);
  const docToMove = ref<DossierDocument | null>(null);
  const targetFolderIdForMove = ref<string | null>(null);

  function openMoveDocModal(doc: DossierDocument) {
    docToMove.value = doc;
    targetFolderIdForMove.value = folderStore.docFolderMap[doc.id] ?? null;
    isMoveDocModalOpen.value = true;
  }

  function confirmMoveDoc(folderId: string | null) {
    if (docToMove.value) {
      folderStore.assignDocToFolder(docToMove.value.id, folderId);
      isMoveDocModalOpen.value = false;
      docToMove.value = null;
    }
  }

  function onDocDropOnFolder(docId: string, folderId: string) {
    folderStore.assignDocToFolder(docId, folderId);
  }

  const mimeByExt: Record<string, string> = {
    pdf: 'application/pdf',
    png: 'image/png',
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    gif: 'image/gif',
    webp: 'image/webp',
    svg: 'image/svg+xml',
    txt: 'text/plain',
  };

  function extOf(name: string) {
    const i = name.lastIndexOf('.');
    return i === -1 ? '' : name.slice(i + 1).toLowerCase();
  }

  function goBack() {
    router.push('/dashboard/affairs');
  }

  async function refreshDossier() {
    if (!affairId.value) return;
    const fetched = await dossierStore.fetchDossier(affairId.value);
    if (fetched) {
      dossier.value = fetched;
    } else {
      dossier.value = dossierStore.allDossiers.find((d: Dossier) => d.id === affairId.value) ?? null;
    }
  }

  // ---------- Sélection et Import de fichiers ----------
  async function pickFromDisk() {
    try {
      const selected = await openDialog({
        multiple: true,
        directory: false,
        title: 'Choisir des documents sur votre ordinateur',
      });
      if (!selected) return;
      const paths = Array.isArray(selected) ? selected : [selected];
      if (paths.length > 0) {
        await importPaths(paths);
      }
    } catch (error) {
      console.warn('openDialog non disponible, passage par le sélecteur HTML :', error);
      if (diskFileInputRef.value) {
        diskFileInputRef.value.value = '';
        diskFileInputRef.value.click();
      }
    }
  }

  async function importPaths(paths: string[]) {
    if (paths.length === 0) return;
    const files: File[] = [];
    for (const path of paths) {
      try {
        const bytes = await readFile(path);
        const name = path.split(/[\\/]/).pop() || 'document';
        files.push(new File([bytes], name, { type: mimeByExt[extOf(name)] || 'application/octet-stream' }));
      } catch (error) {
        console.error(`Lecture impossible du fichier : ${path}`, error);
      }
    }
    if (files.length === 0) {
      if (diskFileInputRef.value) {
        diskFileInputRef.value.value = '';
        diskFileInputRef.value.click();
      }
      return;
    }
    const prevDocIds = new Set(docStore.documents.map((d) => d.id));
    if (await docStore.uploadDocuments(affairId.value, files)) {
      if (currentFolderId.value) {
        for (const d of docStore.documents) {
          if (!prevDocIds.has(d.id)) {
            folderStore.assignDocToFolder(d.id, currentFolderId.value);
          }
        }
      }
      await refreshDossier();
    }
  }

  async function onDiskFileInputChange(event: Event) {
    const target = event.target as HTMLInputElement;
    const files = Array.from(target.files ?? []);
    target.value = '';
    if (files.length === 0) return;
    const prevDocIds = new Set(docStore.documents.map((d) => d.id));
    if (await docStore.uploadDocuments(affairId.value, files)) {
      if (currentFolderId.value) {
        for (const d of docStore.documents) {
          if (!prevDocIds.has(d.id)) {
            folderStore.assignDocToFolder(d.id, currentFolderId.value);
          }
        }
      }
      await refreshDossier();
    }
  }

  async function onDropFiles(e: DragEvent) {
    isDraggingOver.value = false;
    const dt = e.dataTransfer;
    if (!dt) return;
    const files = Array.from(dt.files);
    if (files.length > 0) {
      const prevDocIds = new Set(docStore.documents.map((d) => d.id));
      if (await docStore.uploadDocuments(affairId.value, files)) {
        if (currentFolderId.value) {
          for (const d of docStore.documents) {
            if (!prevDocIds.has(d.id)) {
              folderStore.assignDocToFolder(d.id, currentFolderId.value);
            }
          }
        }
        await refreshDossier();
      }
    }
  }

  // ---------- Visualisation et Téléchargement ----------
  const preview = ref<PreviewData | null>(null);

  async function typedBlob(doc: DossierDocument) {
    const blob = await docStore.fetchFileBlob(doc.id);
    if (!blob) return null;
    const type = mimeByExt[doc.extension];
    return type ? new Blob([blob], { type }) : blob;
  }

  async function openDocument(doc: DossierDocument) {
    const ext = (doc.extension || '').toLowerCase();
    const isImg = ['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg'].includes(ext);
    const isPdf = ext === 'pdf';

    if (!isImg && !isPdf) {
      return downloadDocument(doc);
    }

    const blob = await typedBlob(doc);
    if (!blob) {
      docStore.errorMessage = 'Impossible de charger le document pour la visualisation.';
      return;
    }

    closePreview();
    preview.value = {
      url: URL.createObjectURL(blob),
      title: doc.title,
      kind: isImg ? 'image' : 'pdf',
      doc,
    };
  }

  function closePreview() {
    if (preview.value) URL.revokeObjectURL(preview.value.url);
    preview.value = null;
  }

  async function downloadDocument(doc: DossierDocument) {
    try {
      const target = await saveDialog({ defaultPath: doc.file_name || doc.title });
      if (!target) return;
      const blob = await docStore.fetchFileBlob(doc.id);
      if (!blob) {
        docStore.errorMessage = 'Impossible de télécharger le document';
        return;
      }
      await writeFile(target, new Uint8Array(await blob.arrayBuffer()));
    } catch (error) {
      console.error('Erreur téléchargement :', error);
      docStore.errorMessage = "Impossible d'enregistrer le fichier sur le disque";
    }
  }

  // ---------- Renommage Document ----------
  const renamingDoc = ref<DossierDocument | null>(null);

  function openRename(doc: DossierDocument) {
    renamingDoc.value = doc;
  }

  async function confirmRename(newName: string) {
    if (!renamingDoc.value || !newName.trim()) return;
    if (await docStore.renameDocument(renamingDoc.value.id, newName.trim())) {
      renamingDoc.value = null;
    }
  }

  // ---------- Détails Document ----------
  const isDetailsOpen = ref(false);
  const docForDetails = ref<DossierDocument | null>(null);

  function openDocDetails(doc: DossierDocument) {
    docForDetails.value = doc;
    isDetailsOpen.value = true;
  }

  function openCollaboratorSettings() {
    isDetailsOpen.value = false;
    router.push('/dashboard/settings/collaborators');
  }

  function downloadDetailsDocument() {
    const selected = docForDetails.value;
    isDetailsOpen.value = false;
    if (selected) void downloadDocument(selected);
  }

  function renameDetailsDocument() {
    const selected = docForDetails.value;
    isDetailsOpen.value = false;
    if (selected) openRename(selected);
  }

  function deleteDetailsDocument() {
    const selected = docForDetails.value;
    isDetailsOpen.value = false;
    if (selected) openDelete(selected);
  }

  // ---------- Suppression Document ----------
  const isDeleteOpen = ref(false);
  const docToDelete = ref<DossierDocument | null>(null);
  const isDeleting = ref(false);

  function openDelete(doc: DossierDocument) {
    docToDelete.value = doc;
    isDeleteOpen.value = true;
  }

  async function confirmDelete() {
    if (!docToDelete.value) return;
    isDeleting.value = true;
    try {
      const ok = await docStore.deleteDocument(docToDelete.value.id);
      if (ok) {
        folderStore.assignDocToFolder(docToDelete.value.id, null);
        isDeleteOpen.value = false;
        docToDelete.value = null;
        await refreshDossier();
      }
    } finally {
      isDeleting.value = false;
    }
  }

  onMounted(async () => {
    await Promise.all([
      refreshDossier(),
      docStore.fetchDocuments(affairId.value),
      folderStore.loadStore(),
    ]);
  });

  watch(affairId, async () => {
    closePreview();
    currentFolderId.value = null;
    await Promise.all([
      refreshDossier(),
      docStore.fetchDocuments(affairId.value),
      folderStore.loadStore(),
    ]);
  });

  onUnmounted(() => {
    closePreview();
  });

  return {
    affairId,
    dossier,
    docStore,
    folderStore,
    documents,
    currentFolderId,
    subfolders,
    currentSubfolders,
    currentDocuments,
    currentFolder,
    folderBreadcrumbs,
    isEmptyCurrentView,
    isDraggingOver,
    diskFileInputRef,
    // Modales sous-dossier
    isFolderModalOpen,
    folderModalMode,
    folderModalName,
    openCreateFolder,
    openRenameFolder,
    confirmSaveFolder,
    isDeleteFolderOpen,
    folderToDelete,
    openDeleteFolder,
    confirmDeleteFolder,
    // Modale déplacer
    isMoveDocModalOpen,
    docToMove,
    targetFolderIdForMove,
    openMoveDocModal,
    confirmMoveDoc,
    onDocDropOnFolder,
    // Actions fichiers / navigation
    goBack,
    refreshDossier,
    pickFromDisk,
    onDiskFileInputChange,
    onDropFiles,
    // Preview / download
    preview,
    openDocument,
    closePreview,
    downloadDocument,
    // Rename doc
    renamingDoc,
    openRename,
    confirmRename,
    // Details doc
    isDetailsOpen,
    docForDetails,
    openDocDetails,
    openCollaboratorSettings,
    downloadDetailsDocument,
    renameDetailsDocument,
    deleteDetailsDocument,
    // Delete doc
    isDeleteOpen,
    docToDelete,
    isDeleting,
    openDelete,
    confirmDelete,
  };
}

export type AffairDocumentsController = ReturnType<typeof useAffairDocuments>;
