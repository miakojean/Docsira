import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import { open } from '@tauri-apps/plugin-dialog';
import { load } from '@tauri-apps/plugin-store';
import {
  BaseDirectory,
  copyFile,
  exists,
  mkdir,
  readDir,
  readFile,
  remove,
  rename,
  stat,
  writeFile,
} from '@tauri-apps/plugin-fs';
import { appDataDir, join } from '@tauri-apps/api/path';
import { openPath } from '@tauri-apps/plugin-opener';
import { DOCUMENT_MIME_BY_EXT, isAllowedDocumentName } from '../helpers/documentFormats';
import { useDocumentStore, type SiraCategory } from './documentStore';
import { useClientDossierStore } from './dossierStore';

export interface LocalEntry {
  name: string;
  path: string;
  isDirectory: boolean;
  extension: string;
  size: number | null;
  modifiedAt: number | null;
}

export interface BreadcrumbSegment {
  name: string;
  path: string;
}

export type LocalSortOption = 'name_asc' | 'name_desc' | 'date_desc' | 'size_desc';

const STORE_FILE = 'myWorkspaceStore.json';
const FOLDERS_KEY = 'myOpenedFolders';
const VIEW_MODE_KEY = 'mySpaceViewMode';

export function normalizeLocalPath(rawPath: string): string {
  const trimmed = rawPath.trim();
  if (!trimmed) return '';
  if (/^[a-zA-Z]:[/\\]?$/.test(trimmed)) {
    return `${trimmed[0]}:\\`;
  }
  if (trimmed === '/' || trimmed === '\\') return trimmed;
  return trimmed.replace(/[/\\]+$/, '');
}

export function extractBaseName(fullPath: string): string {
  const normalized = normalizeLocalPath(fullPath);
  if (!normalized) return 'Dossier';
  if (/^[a-zA-Z]:\\$/.test(normalized)) return normalized;
  const parts = normalized.split(/[/\\]/).filter(Boolean);
  return parts[parts.length - 1] || normalized;
}

export function extractParentPath(fullPath: string): string | null {
  const normalized = normalizeLocalPath(fullPath);
  if (!normalized || /^[a-zA-Z]:\\$/.test(normalized) || normalized === '/') {
    return null;
  }
  const sepIndex = Math.max(normalized.lastIndexOf('\\'), normalized.lastIndexOf('/'));
  if (sepIndex <= 0) {
    return normalized.startsWith('/') ? '/' : null;
  }
  const candidate = normalized.slice(0, sepIndex);
  if (/^[a-zA-Z]:$/.test(candidate)) {
    return `${candidate}\\`;
  }
  return candidate;
}

export function extractExtension(fileName: string, isDirectory: boolean): string {
  if (isDirectory) return '';
  const lastDot = fileName.lastIndexOf('.');
  if (lastDot <= 0 || lastDot === fileName.length - 1) return '';
  return fileName.slice(lastDot + 1).toLowerCase();
}

function isSameOrDescendantPath(targetPath: string, rootPath: string): boolean {
  const normTarget = normalizeLocalPath(targetPath).toLowerCase();
  const normRoot = normalizeLocalPath(rootPath).toLowerCase();
  if (!normTarget || !normRoot) return false;
  if (normTarget === normRoot) return true;
  const rootWithSep = normRoot.endsWith('\\') || normRoot.endsWith('/') ? normRoot : `${normRoot}\\`;
  const targetAlt = normTarget.replace(/\//g, '\\');
  const rootAlt = rootWithSep.replace(/\//g, '\\');
  return targetAlt.startsWith(rootAlt);
}

export const useLocalManagerStore = defineStore('localManager', () => {
  // States
  const pinnedFolders = ref<string[]>([]);
  const isPinnedLoaded = ref(false);
  const currentRootPath = ref('');
  const currentPath = ref('');
  const entries = ref<LocalEntry[]>([]);
  const viewMode = ref<'list' | 'grid'>('grid');
  const sortBy = ref<LocalSortOption>('name_asc');
  const isLoading = ref(false);
  const isMutating = ref(false);
  const errorMessage = ref('');

  // Getters
  const breadcrumbs = computed<BreadcrumbSegment[]>(() => {
    const active = normalizeLocalPath(currentPath.value);
    if (!active) return [];

    const matchingRoot = pinnedFolders.value
      .map(normalizeLocalPath)
      .filter((root) => isSameOrDescendantPath(active, root))
      .sort((a, b) => b.length - a.length)[0];

    const rootBase = normalizeLocalPath(currentRootPath.value || matchingRoot || active);

    if (!isSameOrDescendantPath(active, rootBase)) {
      return [{ name: extractBaseName(active), path: active }];
    }

    if (active.toLowerCase() === rootBase.toLowerCase()) {
      return [{ name: extractBaseName(rootBase), path: rootBase }];
    }

    const relative = active.slice(rootBase.length).replace(/^[/\\]+/, '');
    const segments = relative.split(/[/\\]/).filter(Boolean);
    const sep = active.includes('\\') ? '\\' : '/';
    const list: BreadcrumbSegment[] = [{ name: extractBaseName(rootBase), path: rootBase }];

    let acc = rootBase;
    for (const seg of segments) {
      acc = acc.endsWith('\\') || acc.endsWith('/') ? `${acc}${seg}` : `${acc}${sep}${seg}`;
      list.push({ name: seg, path: acc });
    }
    return list;
  });

  const parentPath = computed<string | null>(() => {
    const crumbs = breadcrumbs.value;
    if (crumbs.length > 1) {
      return crumbs[crumbs.length - 2].path;
    }
    const active = normalizeLocalPath(currentPath.value);
    const root = normalizeLocalPath(currentRootPath.value);
    if (active && root && active.toLowerCase() !== root.toLowerCase()) {
      return extractParentPath(active);
    }
    return null;
  });

  // Actions
  function clearError() {
    errorMessage.value = '';
  }

  async function savePinnedFolders() {
    const store = await load(STORE_FILE, { autoSave: false });
    await store.set(FOLDERS_KEY, pinnedFolders.value);
    await store.save();
  }

  async function loadPinnedFolders() {
    clearError();
    try {
      const store = await load(STORE_FILE, { autoSave: false });
      const storedFolders = (await store.get(FOLDERS_KEY)) as string[] | undefined;
      if (Array.isArray(storedFolders)) {
        pinnedFolders.value = storedFolders.map(normalizeLocalPath).filter(Boolean);
      }
      const savedView = (await store.get(VIEW_MODE_KEY)) as 'list' | 'grid' | undefined;
      if (savedView === 'list' || savedView === 'grid') {
        viewMode.value = savedView;
      }
      isPinnedLoaded.value = true;
    } catch (error) {
      console.error('Erreur chargement dossiers locaux :', error);
      errorMessage.value = 'Impossible de charger vos dossiers locaux enregistrés.';
    }
  }

  async function setViewMode(mode: 'list' | 'grid') {
    viewMode.value = mode;
    try {
      const store = await load(STORE_FILE, { autoSave: false });
      await store.set(VIEW_MODE_KEY, mode);
      await store.save();
    } catch {
      // Préférence visuelle non bloquante
    }
  }

  async function pickAndPinFolder(): Promise<string | null> {
    clearError();
    try {
      const selectedPath = await open({
        directory: true,
        multiple: false,
        title: 'Sélectionner un dossier local',
      });
      if (!selectedPath || Array.isArray(selectedPath)) return null;

      const normalized = normalizeLocalPath(selectedPath);
      if (!pinnedFolders.value.some((p) => p.toLowerCase() === normalized.toLowerCase())) {
        pinnedFolders.value.push(normalized);
        await savePinnedFolders();
      }
      return normalized;
    } catch (error) {
      console.error('Erreur sélection dossier :', error);
      errorMessage.value = 'Impossible de sélectionner ce dossier.';
      return null;
    }
  }

  async function createRootFolder(rawName: string): Promise<string | null> {
    const cleanName = rawName.trim();
    if (!cleanName || /[/\\]/.test(cleanName)) {
      errorMessage.value = 'Nom de dossier invalide.';
      return null;
    }

    isMutating.value = true;
    clearError();
    try {
      await mkdir(cleanName, {
        baseDir: BaseDirectory.AppData,
        recursive: true,
      });
      const baseDir = await appDataDir();
      const fullPath = normalizeLocalPath(await join(baseDir, cleanName));

      if (!pinnedFolders.value.some((p) => p.toLowerCase() === fullPath.toLowerCase())) {
        pinnedFolders.value.push(fullPath);
        await savePinnedFolders();
      }
      return fullPath;
    } catch (error) {
      console.error('Erreur création dossier local :', error);
      errorMessage.value = 'Impossible de créer le dossier sur le disque.';
      return null;
    } finally {
      isMutating.value = false;
    }
  }

  async function unpinFolder(folderPath: string) {
    clearError();
    const target = normalizeLocalPath(folderPath).toLowerCase();
    pinnedFolders.value = pinnedFolders.value.filter(
      (item) => normalizeLocalPath(item).toLowerCase() !== target
    );
    await savePinnedFolders();
  }

  async function openDirectory(rawDirPath: string, explicitRootPath?: string) {
    const normalized = normalizeLocalPath(rawDirPath);
    if (!normalized) {
      entries.value = [];
      currentPath.value = '';
      return;
    }

    if (!isPinnedLoaded.value) {
      await loadPinnedFolders();
    }

    if (explicitRootPath) {
      currentRootPath.value = normalizeLocalPath(explicitRootPath);
    } else if (!currentRootPath.value || !isSameOrDescendantPath(normalized, currentRootPath.value)) {
      const matchingPinned = pinnedFolders.value
        .map(normalizeLocalPath)
        .filter((root) => isSameOrDescendantPath(normalized, root))
        .sort((a, b) => b.length - a.length)[0];
      currentRootPath.value = matchingPinned || normalized;
    }

    currentPath.value = normalized;
    isLoading.value = true;
    clearError();

    try {
      const rawEntries = await readDir(normalized);
      const visibleEntries = rawEntries.filter((entry) => Boolean(entry.name));

      const enriched = await Promise.all(
        visibleEntries.map(async (entry): Promise<LocalEntry | null> => {
          const name = entry.name;
          if (!name) return null;
          const fullPath = await join(normalized, name);
          const isDirectory = Boolean(entry.isDirectory);
          let size: number | null = null;
          let modifiedAt: number | null = null;

          try {
            const info = await stat(fullPath);
            size = isDirectory ? null : info.size;
            modifiedAt = info.mtime ? info.mtime.getTime() : null;
          } catch {
            // Certains fichiers système refusent stat() ; on conserve quand même l'entrée
          }

          return {
            name,
            path: fullPath,
            isDirectory,
            extension: extractExtension(name, isDirectory),
            size,
            modifiedAt,
          };
        })
      );

      entries.value = enriched.filter((item): item is LocalEntry => item !== null);
    } catch (error) {
      console.error('Erreur lecture dossier local :', error);
      entries.value = [];
      errorMessage.value = "Impossible d'ouvrir ce dossier. Vérifiez qu'il existe encore sur le disque.";
    } finally {
      isLoading.value = false;
    }
  }

  async function refreshCurrentDirectory() {
    if (currentPath.value) {
      await openDirectory(currentPath.value);
    }
  }

  async function createSubfolder(rawName: string): Promise<boolean> {
    const cleanName = rawName.trim();
    if (!currentPath.value) return false;
    if (!cleanName || /[/\\]/.test(cleanName)) {
      errorMessage.value = 'Le nom du dossier ne doit pas contenir de barre oblique.';
      return false;
    }

    isMutating.value = true;
    clearError();
    try {
      const targetPath = await join(currentPath.value, cleanName);
      if (await exists(targetPath)) {
        errorMessage.value = 'Un élément porte déjà ce nom dans ce dossier.';
        return false;
      }
      await mkdir(targetPath, { recursive: false });
      await refreshCurrentDirectory();
      return true;
    } catch (error) {
      console.error('Erreur création sous-dossier :', error);
      errorMessage.value = 'Impossible de créer le sous-dossier.';
      return false;
    } finally {
      isMutating.value = false;
    }
  }

  async function importFilesToCurrentDir(): Promise<number> {
    if (!currentPath.value) return 0;
    clearError();
    try {
      const selected = await open({
        directory: false,
        multiple: true,
        title: 'Ajouter des fichiers dans ce dossier',
      });
      if (!selected) return 0;
      const sourcePaths = Array.isArray(selected) ? selected : [selected];
      if (sourcePaths.length === 0) return 0;

      isMutating.value = true;
      let importedCount = 0;

      for (const srcPath of sourcePaths) {
        const baseName = extractBaseName(srcPath);
        let destPath = await join(currentPath.value, baseName);

        if (await exists(destPath)) {
          const dotIdx = baseName.lastIndexOf('.');
          const stem = dotIdx > 0 ? baseName.slice(0, dotIdx) : baseName;
          const ext = dotIdx > 0 ? baseName.slice(dotIdx) : '';
          let counter = 1;
          while (await exists(destPath)) {
            destPath = await join(currentPath.value, `${stem} (${counter})${ext}`);
            counter++;
          }
        }

        try {
          await copyFile(srcPath, destPath);
          importedCount++;
        } catch {
          const bytes = await readFile(srcPath);
          await writeFile(destPath, bytes);
          importedCount++;
        }
      }

      if (importedCount > 0) {
        await refreshCurrentDirectory();
      }
      return importedCount;
    } catch (error) {
      console.error('Erreur import fichiers locaux :', error);
      errorMessage.value = "Impossible d'importer un ou plusieurs fichiers.";
      return 0;
    } finally {
      isMutating.value = false;
    }
  }

  async function renameEntry(entry: LocalEntry, rawNewName: string): Promise<boolean> {
    const cleanName = rawNewName.trim();
    if (!cleanName || /[/\\]/.test(cleanName)) {
      errorMessage.value = 'Le nom ne doit pas être vide ni contenir de caractère "/" ou "\\".';
      return false;
    }

    const parent = extractParentPath(entry.path);
    if (!parent) {
      errorMessage.value = 'Impossible de déterminer le dossier parent.';
      return false;
    }

    isMutating.value = true;
    clearError();
    try {
      const newPath = await join(parent, cleanName);
      if (newPath.toLowerCase() !== entry.path.toLowerCase() && (await exists(newPath))) {
        errorMessage.value = 'Un élément porte déjà ce nom.';
        return false;
      }

      await rename(entry.path, newPath);

      const idx = pinnedFolders.value.findIndex(
        (p) => normalizeLocalPath(p).toLowerCase() === normalizeLocalPath(entry.path).toLowerCase()
      );
      if (idx !== -1) {
        pinnedFolders.value[idx] = normalizeLocalPath(newPath);
        await savePinnedFolders();
      }

      await refreshCurrentDirectory();
      return true;
    } catch (error) {
      console.error('Erreur renommage local :', error);
      errorMessage.value = 'Impossible de renommer cet élément.';
      return false;
    } finally {
      isMutating.value = false;
    }
  }

  async function deleteEntry(entry: LocalEntry): Promise<boolean> {
    isMutating.value = true;
    clearError();
    try {
      await remove(entry.path, { recursive: entry.isDirectory });

      const normalizedTarget = normalizeLocalPath(entry.path).toLowerCase();
      const filteredPinned = pinnedFolders.value.filter(
        (p) => normalizeLocalPath(p).toLowerCase() !== normalizedTarget
      );
      if (filteredPinned.length !== pinnedFolders.value.length) {
        pinnedFolders.value = filteredPinned;
        await savePinnedFolders();
      }

      await refreshCurrentDirectory();
      return true;
    } catch (error) {
      console.error('Erreur suppression locale :', error);
      errorMessage.value = "Impossible de supprimer cet élément du disque.";
      return false;
    } finally {
      isMutating.value = false;
    }
  }

  async function openWithSystem(targetPath: string) {
    clearError();
    try {
      await openPath(targetPath);
    } catch (error) {
      console.error('Erreur ouverture système :', error);
      errorMessage.value = "Impossible d'ouvrir cet élément avec le système.";
    }
  }

  async function readLocalFileBytes(filePath: string): Promise<Uint8Array | null> {
    clearError();
    try {
      return await readFile(filePath);
    } catch (error) {
      console.error('Erreur lecture fichier local :', error);
      errorMessage.value = 'Impossible de lire le fichier pour la prévisualisation.';
      return null;
    }
  }

  async function collectLocalFilesForUpload(
    targetPath: string,
    isDirectory: boolean
  ): Promise<{ files: File[]; skippedCount: number; errorMessage: string }> {
    const normalized = normalizeLocalPath(targetPath);
    if (!normalized) {
      return { files: [], skippedCount: 0, errorMessage: 'Chemin source invalide.' };
    }

    if (!isDirectory) {
      const fileName = extractBaseName(normalized);
      if (!isAllowedDocumentName(fileName)) {
        return {
          files: [],
          skippedCount: 1,
          errorMessage:
            'Format non autorisé pour le Workspace (seuls les fichiers PDF, Word .doc/.docx et images sont acceptés).',
        };
      }
      const bytes = await readFile(normalized);
      const ext = extractExtension(fileName, false);
      const mime = DOCUMENT_MIME_BY_EXT[ext] ?? '';
      const file = new File([new Uint8Array(bytes)], fileName, mime ? { type: mime } : undefined);
      return { files: [file], skippedCount: 0, errorMessage: '' };
    }

    const dirEntries = await readDir(normalized);
    const candidateNames = dirEntries
      .filter((entry) => !entry.isDirectory && Boolean(entry.name))
      .map((entry) => entry.name as string);

    const validNames = candidateNames.filter((name) => isAllowedDocumentName(name));
    const skippedCount = candidateNames.length - validNames.length;

    if (validNames.length === 0) {
      return {
        files: [],
        skippedCount,
        errorMessage:
          'Aucun fichier compatible (PDF, Word .doc/.docx ou images) trouvé dans ce dossier.',
      };
    }

    const files: File[] = [];
    for (const name of validNames) {
      const fullPath = await join(normalized, name);
      const bytes = await readFile(fullPath);
      const ext = extractExtension(name, false);
      const mime = DOCUMENT_MIME_BY_EXT[ext] ?? '';
      files.push(new File([new Uint8Array(bytes)], name, mime ? { type: mime } : undefined));
    }

    return { files, skippedCount, errorMessage: '' };
  }

  async function sendToWorkspace(
    affairId: string,
    targetPath: string,
    isDirectory: boolean,
    category: SiraCategory
  ): Promise<{ ok: boolean; uploadedCount: number; skippedCount: number }> {
    if (!affairId) {
      errorMessage.value = 'Veuillez sélectionner un dossier de destination dans le Workspace.';
      return { ok: false, uploadedCount: 0, skippedCount: 0 };
    }

    isMutating.value = true;
    clearError();
    try {
      const collected = await collectLocalFilesForUpload(targetPath, isDirectory);
      if (collected.files.length === 0) {
        errorMessage.value = collected.errorMessage || 'Aucun fichier à envoyer.';
        return { ok: false, uploadedCount: 0, skippedCount: collected.skippedCount };
      }

      const docStore = useDocumentStore();
      const dossierStore = useClientDossierStore();
      const ok = await docStore.uploadDocuments(affairId, collected.files, category);
      if (!ok) {
        errorMessage.value = docStore.errorMessage || "Impossible d'envoyer vers le Workspace.";
        return { ok: false, uploadedCount: 0, skippedCount: collected.skippedCount };
      }

      await dossierStore.fetchAllDossiers();
      return {
        ok: true,
        uploadedCount: collected.files.length,
        skippedCount: collected.skippedCount,
      };
    } catch (error) {
      console.error('Erreur envoi vers le Workspace :', error);
      errorMessage.value = 'Erreur lors du transfert vers le Workspace.';
      return { ok: false, uploadedCount: 0, skippedCount: 0 };
    } finally {
      isMutating.value = false;
    }
  }

  return {
    // States
    pinnedFolders,
    isPinnedLoaded,
    currentRootPath,
    currentPath,
    entries,
    viewMode,
    sortBy,
    isLoading,
    isMutating,
    errorMessage,
    // Getters
    breadcrumbs,
    parentPath,
    // Actions
    clearError,
    loadPinnedFolders,
    savePinnedFolders,
    setViewMode,
    pickAndPinFolder,
    createRootFolder,
    unpinFolder,
    openDirectory,
    refreshCurrentDirectory,
    createSubfolder,
    importFilesToCurrentDir,
    renameEntry,
    deleteEntry,
    openWithSystem,
    readLocalFileBytes,
    sendToWorkspace,
  };
});
