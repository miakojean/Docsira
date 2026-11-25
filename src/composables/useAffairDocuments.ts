import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { save as saveDialog } from '@tauri-apps/plugin-dialog';
import { writeFile } from '@tauri-apps/plugin-fs';
import mammoth from 'mammoth';
import { useClientDossierStore, type AffairShareLink, type Dossier } from '../stores/dossierStore';
import {
  buildDocumentVersionLineages,
  useDocumentStore,
  type DocumentShareLink,
  type DossierDocument,
  type SiraCategory,
} from '../stores/documentStore';
import { useAffairFolderStore, type AffairSubfolder } from '../stores/affairFolderStore';
import { useCommentStore } from '../stores/commentStore';
import { useSiraStore } from '../stores/siraStore';
import { useAuthStore } from '../stores/authStore';
import { DOCUMENT_MIME_BY_EXT, filterAllowedDocuments } from '../helpers/documentFormats';
import type { PreviewData } from '../components/modale/filePreviewModale.vue';
import type { MoveDocPayload } from '../components/modale/moveDocModale.vue';

export function useAffairDocuments() {
  const route = useRoute();
  const router = useRouter();
  const dossierStore = useClientDossierStore();
  const docStore = useDocumentStore();
  const folderStore = useAffairFolderStore();
  const commentStore = useCommentStore();
  const siraStore = useSiraStore();
  const authStore = useAuthStore();

  const affairId = computed(() => String(route.params.id));
  const dossier = ref<Dossier | null>(null);

  const isDraggingOver = ref(false);
  const diskFileInputRef = ref<HTMLInputElement | null>(null);

  const documents = computed(() => docStore.documents);
  const documentLineages = computed(() => buildDocumentVersionLineages(documents.value));
  const latestDocuments = computed(() => documentLineages.value.map((l) => l.latest));

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

  // Documents du niveau actuel (dernière version de chaque lignée)
  const currentDocuments = computed<DossierDocument[]>(() => {
    return folderStore.getFolderDocuments(affairId.value, currentFolderId.value, latestDocuments.value);
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
    if (!authStore.canEdit) return;
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

  // ---------- Déplacement d'un document (sous-dossier ou autre dossier/affaire) ----------
  const isMoveDocModalOpen = ref(false);
  const docToMove = ref<DossierDocument | null>(null);
  const targetFolderIdForMove = ref<string | null>(null);
  const isMovingDoc = ref(false);

  const otherDossiers = computed<Dossier[]>(() => {
    return dossierStore.allDossiers.filter((d) => String(d.id) !== affairId.value);
  });

  async function openMoveDocModal(doc: DossierDocument) {
    docToMove.value = doc;
    targetFolderIdForMove.value = folderStore.docFolderMap[doc.id] ?? null;
    isMoveDocModalOpen.value = true;
    if (dossierStore.allDossiers.length === 0) {
      await dossierStore.fetchAllDossiers();
    }
  }

  async function confirmMoveDoc(payload: MoveDocPayload) {
    if (!docToMove.value) return;
    if (payload.targetAffairId && payload.targetAffairId !== affairId.value) {
      isMovingDoc.value = true;
      try {
        const ok = await docStore.moveDocumentToAffair(docToMove.value.id, payload.targetAffairId);
        if (ok) {
          folderStore.assignDocToFolder(docToMove.value.id, null);
          isMoveDocModalOpen.value = false;
          docToMove.value = null;
          await Promise.all([refreshDossier(), dossierStore.fetchAllDossiers()]);
        }
      } finally {
        isMovingDoc.value = false;
      }
      return;
    }

    folderStore.assignDocToFolder(docToMove.value.id, payload.targetFolderId);
    isMoveDocModalOpen.value = false;
    docToMove.value = null;
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

  // ---------- Sélection et Import de fichiers avec catégorie SIRA ----------
  const isUploadDocModalOpen = ref(false);
  const filesForUpload = ref<File[]>([]);

  function openUploadDocModal(files?: File[]) {
    if (!authStore.canEdit) return;
    filesForUpload.value = files && files.length > 0 ? [...files] : [];
    isUploadDocModalOpen.value = true;
  }

  function closeUploadDocModal() {
    isUploadDocModalOpen.value = false;
    filesForUpload.value = [];
  }

  async function handleUploadDocs({ files, category }: { files: File[]; category: SiraCategory }) {
    if (files.length === 0) return;
    const prevDocIds = new Set(docStore.documents.map((d) => d.id));
    const success = await docStore.uploadDocuments(affairId.value, files, category);
    if (success) {
      if (currentFolderId.value) {
        for (const d of docStore.documents) {
          if (!prevDocIds.has(d.id)) {
            folderStore.assignDocToFolder(d.id, currentFolderId.value);
          }
        }
      }
      await refreshDossier();
      closeUploadDocModal();
    }
  }

  function pickFromDisk() {
    openUploadDocModal();
  }

  async function onDiskFileInputChange(event: Event) {
    const target = event.target as HTMLInputElement;
    const files = Array.from(target.files ?? []);
    target.value = '';
    if (files.length === 0) return;

    const { valid, errorMessage } = filterAllowedDocuments(files);
    if (errorMessage) docStore.errorMessage = errorMessage;
    if (valid.length > 0) {
      openUploadDocModal(valid);
    }
  }

  async function onDropFiles(e: DragEvent) {
    isDraggingOver.value = false;
    if (!authStore.canEdit) return;
    const dt = e.dataTransfer;
    if (!dt) return;
    const files = Array.from(dt.files);
    if (files.length === 0) return;

    const { valid, errorMessage } = filterAllowedDocuments(files);
    if (errorMessage) docStore.errorMessage = errorMessage;
    if (valid.length > 0) {
      openUploadDocModal(valid);
    }
  }

  // ---------- Visualisation et Téléchargement ----------
  const preview = ref<PreviewData | null>(null);

  async function typedBlob(doc: DossierDocument) {
    const blob = await docStore.fetchFileBlob(doc.id);
    if (!blob) return null;
    const ext = (doc.extension || '').toLowerCase();
    const type = DOCUMENT_MIME_BY_EXT[ext] ?? mimeByExt[ext];
    return type ? new Blob([blob], { type }) : blob;
  }

  async function openDocument(doc: DossierDocument) {
    const ext = (doc.extension || '').toLowerCase();
    const isImg = ['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg'].includes(ext);
    const isPdf = ext === 'pdf';
    const isDocx = ext === 'docx';
    const isLegacyDoc = ext === 'doc';

    closePreview();

    if (isLegacyDoc) {
      preview.value = {
        title: doc.title,
        kind: 'unsupported',
        message: "L'aperçu intégré n'est pas disponible pour l'ancien format Word (.doc). Téléchargez le fichier pour l'ouvrir dans Word.",
        doc,
      };
      return;
    }

    if (!isImg && !isPdf && !isDocx) {
      preview.value = {
        title: doc.title,
        kind: 'unsupported',
        message: `L'aperçu intégré n'est pas disponible pour le format .${ext || 'inconnu'}.`,
        doc,
      };
      return;
    }

    preview.value = {
      title: doc.title,
      kind: 'loading',
      doc,
    };

    const blob = await typedBlob(doc);
    if (!blob) {
      closePreview();
      if (!docStore.errorMessage) {
        docStore.errorMessage = 'Impossible de charger le document pour la visualisation.';
      }
      return;
    }

    if (isImg) {
      preview.value = {
        title: doc.title,
        kind: 'image',
        url: URL.createObjectURL(blob),
        doc,
      };
      return;
    }

    if (isPdf) {
      const buffer = await blob.arrayBuffer();
      preview.value = {
        title: doc.title,
        kind: 'pdf',
        data: buffer,
        doc,
      };
      return;
    }

    if (isDocx) {
      try {
        const arrayBuffer = await blob.arrayBuffer();
        const result = await mammoth.convertToHtml({ arrayBuffer });
        preview.value = {
          title: doc.title,
          kind: 'docx',
          html: result.value,
          doc,
        };
      } catch (err) {
        console.error('Erreur lecture DOCX :', err);
        preview.value = {
          title: doc.title,
          kind: 'unsupported',
          message: "Impossible de prévisualiser ce fichier Word (.docx). Vous pouvez le télécharger pour l'ouvrir dans Word.",
          doc,
        };
      }
    }
  }

  function closePreview() {
    if (preview.value?.url) URL.revokeObjectURL(preview.value.url);
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
  const isRenaming = ref(false);

  function openRename(doc: DossierDocument) {
    docStore.errorMessage = '';
    renamingDoc.value = doc;
  }

  async function confirmRename(newName: string) {
    if (!renamingDoc.value || !newName.trim()) return;
    isRenaming.value = true;
    try {
      const targetId = renamingDoc.value.id;
      const trimmed = newName.trim();
      if (await docStore.renameDocument(targetId, trimmed)) {
        if (docForDetails.value?.id === targetId) {
          docForDetails.value =
            docStore.documents.find((d) => d.id === targetId) ?? {
              ...docForDetails.value,
              title: trimmed,
            };
        }
        renamingDoc.value = null;
      }
    } finally {
      isRenaming.value = false;
    }
  }

  // ---------- Partage par lien (Document ou Dossier entier) ----------
  const isShareModalOpen = ref(false);
  const shareMode = ref<'document' | 'dossier'>('document');
  const docToShare = ref<DossierDocument | null>(null);
  const shareLinks = ref<Array<DocumentShareLink | AffairShareLink>>([]);
  const isShareLoading = ref(false);
  const isShareCreating = ref(false);
  const shareError = ref('');

  const shareTargetTitle = computed(() => {
    if (shareMode.value === 'dossier') {
      if (!dossier.value) return 'Dossier';
      return `${dossier.value.reference_affair} • ${dossier.value.title}`;
    }
    return docToShare.value?.title || docToShare.value?.file_name || '';
  });

  const shareDescription = computed(() => {
    if (shareMode.value === 'dossier') {
      return "Créez un lien de partage pour permettre à un collaborateur ou à un client de télécharger l'ensemble des documents de ce dossier (archive ZIP).";
    }
    return "Créez un lien de partage et envoyez-le à un collaborateur ou à un client pour qu'il puisse consulter et télécharger ce document.";
  });

  async function openShareModal(doc: DossierDocument) {
    shareMode.value = 'document';
    docToShare.value = doc;
    shareLinks.value = [];
    shareError.value = '';
    isShareModalOpen.value = true;
    isShareLoading.value = true;
    try {
      const existing = await docStore.fetchShareLinks(doc.id);
      if (existing.length > 0) {
        shareLinks.value = existing;
      } else {
        const created = await docStore.createShareLink(doc.id, 7);
        if (created) {
          shareLinks.value = [created];
        } else if (docStore.errorMessage) {
          shareError.value = docStore.errorMessage;
        }
      }
    } finally {
      isShareLoading.value = false;
    }
  }

  async function openShareDossierModal() {
    if (!affairId.value) return;
    shareMode.value = 'dossier';
    docToShare.value = null;
    shareLinks.value = [];
    shareError.value = '';
    isShareModalOpen.value = true;
    isShareLoading.value = true;
    try {
      const existing = await dossierStore.fetchAffairShareLinks(affairId.value);
      if (existing.length > 0) {
        shareLinks.value = existing;
      } else {
        const created = await dossierStore.createAffairShareLink(affairId.value, 7);
        if (created) {
          shareLinks.value = [created];
        } else if (dossierStore.errorMessage) {
          shareError.value = dossierStore.errorMessage;
        }
      }
    } finally {
      isShareLoading.value = false;
    }
  }

  function closeShareModal() {
    isShareModalOpen.value = false;
    docToShare.value = null;
    shareError.value = '';
  }

  async function createNewShareLink(expiresInDays: number | null) {
    isShareCreating.value = true;
    shareError.value = '';
    try {
      if (shareMode.value === 'dossier') {
        const created = await dossierStore.createAffairShareLink(affairId.value, expiresInDays);
        if (created) {
          shareLinks.value = [created, ...shareLinks.value];
        } else {
          shareError.value = dossierStore.errorMessage || 'Impossible de créer le lien.';
        }
        return;
      }

      if (!docToShare.value) return;
      const created = await docStore.createShareLink(docToShare.value.id, expiresInDays);
      if (created) {
        shareLinks.value = [created, ...shareLinks.value];
      } else {
        shareError.value = docStore.errorMessage || 'Impossible de créer le lien.';
      }
    } finally {
      isShareCreating.value = false;
    }
  }

  async function revokeExistingShareLink(linkId: string) {
    shareError.value = '';
    if (shareMode.value === 'dossier') {
      const ok = await dossierStore.revokeAffairShareLink(affairId.value, linkId);
      if (ok) {
        shareLinks.value = shareLinks.value.filter((l) => l.id !== linkId);
      } else {
        shareError.value = dossierStore.errorMessage || 'Impossible de révoquer ce lien.';
      }
      return;
    }

    if (!docToShare.value) return;
    const ok = await docStore.revokeShareLink(docToShare.value.id, linkId);
    if (ok) {
      shareLinks.value = shareLinks.value.filter((l) => l.id !== linkId);
    } else {
      shareError.value = docStore.errorMessage || 'Impossible de révoquer ce lien.';
    }
  }

  // ---------- Détails Document ----------
  const isDetailsOpen = ref(false);
  const docForDetails = ref<DossierDocument | null>(null);

  function openDocDetails(doc: DossierDocument) {
    docForDetails.value = doc;
    isDetailsOpen.value = true;
  }

  function previewDetailsDocument() {
    const selected = docForDetails.value;
    isDetailsOpen.value = false;
    if (selected) void openDocument(selected);
  }

  function openCollaboratorSettings() {
    const selected = docForDetails.value;
    isDetailsOpen.value = false;
    if (selected) {
      void openShareModal(selected);
    }
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

  // ---------- Modal SIRA Suivi & Historique ----------
  const isSiraModalOpen = ref(false);

  function openSiraModal() {
    isSiraModalOpen.value = true;
  }

  function closeSiraModal() {
    isSiraModalOpen.value = false;
  }

  async function changeDocumentCategory(doc: DossierDocument, category: SiraCategory) {
    const ok = await docStore.updateDocumentCategory(doc.id, category);
    if (ok) {
      if (docForDetails.value?.id === doc.id) {
        docForDetails.value =
          docStore.documents.find((d) => d.id === doc.id) ?? {
            ...docForDetails.value,
            category,
          };
      }
      await Promise.all([refreshDossier(), siraStore.fetchHistory(affairId.value)]);
    }
  }

  // ---------- Versioning des documents ----------
  const isVersionsModalOpen = ref(false);
  const versionsModalDoc = ref<DossierDocument | null>(null);

  function openVersionsModal(doc: DossierDocument) {
    docStore.errorMessage = '';
    versionsModalDoc.value = doc;
    isVersionsModalOpen.value = true;
  }

  function closeVersionsModal() {
    isVersionsModalOpen.value = false;
    versionsModalDoc.value = null;
  }

  function openDetailsVersions() {
    const selected = docForDetails.value;
    isDetailsOpen.value = false;
    if (selected) {
      openVersionsModal(selected);
    }
  }

  async function handleUploadNewVersion(payload: {
    document: DossierDocument;
    file: File;
    versionNote: string;
  }) {
    const folderId = folderStore.docFolderMap[payload.document.id] ?? null;
    const created = await docStore.uploadNewVersion(payload.document.id, payload.file, {
      versionNote: payload.versionNote,
    });
    if (created) {
      if (folderId) {
        folderStore.assignDocToFolder(created.id, folderId);
      }
      versionsModalDoc.value = created;
      if (docForDetails.value?.id === payload.document.id) {
        docForDetails.value = created;
      }
      await Promise.all([refreshDossier(), siraStore.fetchHistory(affairId.value)]);
    }
  }

  async function handleRestoreVersion(ver: DossierDocument) {
    const fallbackDocId = versionsModalDoc.value?.id;
    const folderId =
      folderStore.docFolderMap[ver.id] ??
      (fallbackDocId ? folderStore.docFolderMap[fallbackDocId] : null) ??
      null;
    const restored = await docStore.restoreDocumentVersion(ver.id);
    if (restored) {
      if (folderId) {
        folderStore.assignDocToFolder(restored.id, folderId);
      }
      if (docForDetails.value && (docForDetails.value.id === ver.id || docForDetails.value.id === fallbackDocId)) {
        docForDetails.value = restored;
      }
      versionsModalDoc.value = restored;
      await Promise.all([refreshDossier(), siraStore.fetchHistory(affairId.value)]);
    }
  }

  async function handleReplaceFromPreview(payload: { doc: DossierDocument; file: File }) {
    const folderId = folderStore.docFolderMap[payload.doc.id] ?? null;
    const created = await docStore.uploadNewVersion(payload.doc.id, payload.file, {
      versionNote: '',
    });
    if (created) {
      if (folderId) {
        folderStore.assignDocToFolder(created.id, folderId);
      }
      if (versionsModalDoc.value?.id === payload.doc.id) {
        versionsModalDoc.value = created;
      }
      if (docForDetails.value?.id === payload.doc.id) {
        docForDetails.value = created;
      }
      await Promise.all([refreshDossier(), siraStore.fetchHistory(affairId.value)]);
      await openDocument(created);
    }
  }

  // ---------- Commentaires collaborateurs ----------
  const isCommentsOpen = ref(false);
  const isCommentNotifDismissed = ref(false);
  const commentInitialDocId = ref<string | null>(null);
  const commentFocusKey = ref(0);
  const commentsCount = computed(() => commentStore.getCommentCount(affairId.value));
  const unreadCommentsCount = computed(() => commentStore.getUnreadCount(affairId.value));
  const latestUnreadComment = computed(() => commentStore.getLatestUnread(affairId.value));

  watch(
    () => latestUnreadComment.value?.id,
    (newId, oldId) => {
      if (newId && newId !== oldId && !isCommentsOpen.value) {
        isCommentNotifDismissed.value = false;
      }
    }
  );

  function dismissCommentNotification() {
    isCommentNotifDismissed.value = true;
  }

  async function markCommentsAsRead() {
    if (!affairId.value) return;
    const ok = await commentStore.markAsRead(affairId.value);
    if (ok) {
      if (dossier.value && dossier.value.id === affairId.value) {
        dossier.value = { ...dossier.value, unread_comments_count: 0 };
      }
      dossierStore.setDossierUnreadComments(affairId.value, 0);
    }
  }

  function openComments(doc?: DossierDocument) {
    commentInitialDocId.value = doc?.id ?? null;
    isCommentsOpen.value = true;
    isCommentNotifDismissed.value = true;
    commentFocusKey.value++;
    void commentStore.fetchComments(affairId.value);
    void markCommentsAsRead();
  }

  function toggleComments() {
    isCommentsOpen.value = !isCommentsOpen.value;
    if (isCommentsOpen.value) {
      isCommentNotifDismissed.value = true;
      void commentStore.fetchComments(affairId.value);
      void markCommentsAsRead();
    }
  }

  function closeComments() {
    isCommentsOpen.value = false;
  }

  function openDocumentById(docId: string) {
    const found = docStore.documents.find((d) => d.id === docId);
    if (found) {
      void openDocument(found);
    }
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

  let commentPollTimer: number | null = null;

  onMounted(async () => {
    const tasks: Promise<unknown>[] = [
      refreshDossier(),
      docStore.fetchDocuments(affairId.value),
      commentStore.fetchUnreadStatus(affairId.value),
    ];
    if (!folderStore.isLoaded) tasks.push(folderStore.loadStore());
    await Promise.all(tasks);

    commentPollTimer = window.setInterval(async () => {
      if (!affairId.value) return;
      const state = await commentStore.fetchUnreadStatus(affairId.value);
      if (isCommentsOpen.value && state && state.unreadCount > 0) {
        await commentStore.fetchComments(affairId.value);
        await markCommentsAsRead();
      }
    }, 20000);
  });

  watch(affairId, async () => {
    closePreview();
    isCommentsOpen.value = false;
    isCommentNotifDismissed.value = false;
    commentInitialDocId.value = null;
    currentFolderId.value = null;
    const tasks: Promise<unknown>[] = [
      refreshDossier(),
      docStore.fetchDocuments(affairId.value),
      commentStore.fetchUnreadStatus(affairId.value),
    ];
    if (!folderStore.isLoaded) tasks.push(folderStore.loadStore());
    await Promise.all(tasks);
  });

  onUnmounted(() => {
    if (commentPollTimer !== null) {
      window.clearInterval(commentPollTimer);
      commentPollTimer = null;
    }
    closePreview();
  });

  return {
    affairId,
    dossier,
    docStore,
    folderStore,
    documents,
    latestDocuments,
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
    otherDossiers,
    isMovingDoc,
    openMoveDocModal,
    confirmMoveDoc,
    onDocDropOnFolder,
    // Actions fichiers / navigation
    goBack,
    refreshDossier,
    pickFromDisk,
    onDiskFileInputChange,
    onDropFiles,
    // Modale import document avec catégorie SIRA
    isUploadDocModalOpen,
    filesForUpload,
    openUploadDocModal,
    closeUploadDocModal,
    handleUploadDocs,
    // Preview / download
    preview,
    openDocument,
    closePreview,
    downloadDocument,
    // Rename doc
    renamingDoc,
    isRenaming,
    openRename,
    confirmRename,
    // Share link
    isShareModalOpen,
    docToShare,
    shareTargetTitle,
    shareDescription,
    shareLinks,
    isShareLoading,
    isShareCreating,
    shareError,
    openShareModal,
    openShareDossierModal,
    closeShareModal,
    createNewShareLink,
    revokeExistingShareLink,
    // Details doc
    isDetailsOpen,
    docForDetails,
    openDocDetails,
    previewDetailsDocument,
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
    // SIRA Avancement & Traçabilité
    isSiraModalOpen,
    openSiraModal,
    closeSiraModal,
    changeDocumentCategory,
    // Versioning
    isVersionsModalOpen,
    versionsModalDoc,
    openVersionsModal,
    closeVersionsModal,
    openDetailsVersions,
    handleUploadNewVersion,
    handleRestoreVersion,
    handleReplaceFromPreview,
    // Commentaires collaborateurs
    isCommentsOpen,
    isCommentNotifDismissed,
    commentInitialDocId,
    commentFocusKey,
    commentsCount,
    unreadCommentsCount,
    latestUnreadComment,
    dismissCommentNotification,
    openComments,
    toggleComments,
    closeComments,
    openDocumentById,
  };
}

export type AffairDocumentsController = ReturnType<typeof useAffairDocuments>;
