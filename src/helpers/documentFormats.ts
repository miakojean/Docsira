export const ALLOWED_DOCUMENT_EXTENSIONS = [
  'pdf',
  'doc',
  'docx',
  'png',
  'jpg',
  'jpeg',
  'webp',
  'gif',
] as const;

export const MAX_DOCUMENT_SIZE_BYTES = 25 * 1024 * 1024;

export type AllowedDocumentExtension = (typeof ALLOWED_DOCUMENT_EXTENSIONS)[number];

export const ALLOWED_DOCUMENT_ACCEPT =
  '.pdf,.doc,.docx,.png,.jpg,.jpeg,.webp,.gif,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/png,image/jpeg,image/webp,image/gif';

export const TAURI_DOCUMENT_FILTERS = [
  {
    name: 'Documents PDF, Word et Images',
    extensions: [...ALLOWED_DOCUMENT_EXTENSIONS],
  },
];

export const DOCUMENT_MIME_BY_EXT: Record<string, string> = {
  pdf: 'application/pdf',
  doc: 'application/msword',
  docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  png: 'image/png',
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  webp: 'image/webp',
  gif: 'image/gif',
};

export function getFileExtension(name: string): string {
  const clean = name.trim();
  const idx = clean.lastIndexOf('.');
  if (idx === -1) return '';
  return clean.slice(idx + 1).toLowerCase();
}

export function isAllowedDocumentName(name: string): boolean {
  const ext = getFileExtension(name);
  return (ALLOWED_DOCUMENT_EXTENSIONS as readonly string[]).includes(ext);
}

export function filterAllowedDocuments(files: File[]): {
  valid: File[];
  rejected: File[];
  errorMessage: string;
} {
  const valid: File[] = [];
  const rejected: File[] = [];
  const rejectedReasons: string[] = [];

  for (const file of files) {
    if (!isAllowedDocumentName(file.name)) {
      rejected.push(file);
      rejectedReasons.push(`${file.name} (format non autorisé)`);
    } else if (file.size === 0) {
      rejected.push(file);
      rejectedReasons.push(`${file.name} (fichier vide)`);
    } else if (file.size > MAX_DOCUMENT_SIZE_BYTES) {
      rejected.push(file);
      rejectedReasons.push(`${file.name} (> 25 Mo)`);
    } else {
      valid.push(file);
    }
  }

  let errorMessage = '';
  if (rejected.length > 0) {
    const details = rejectedReasons.slice(0, 3).join(', ');
    const extra = rejected.length > 3 ? ` (+${rejected.length - 3})` : '';
    errorMessage = `Fichier(s) refusé(s) (${details}${extra}) : formats PDF/Word/images uniquement, 25 Mo max.`;
  }

  return { valid, rejected, errorMessage };
}

