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

  for (const file of files) {
    if (isAllowedDocumentName(file.name)) {
      valid.push(file);
    } else {
      rejected.push(file);
    }
  }

  let errorMessage = '';
  if (rejected.length > 0) {
    const names = rejected
      .slice(0, 3)
      .map((f) => f.name)
      .join(', ');
    const extra = rejected.length > 3 ? ` (+${rejected.length - 3})` : '';
    errorMessage = `Format non autorisé (${names}${extra}) : seuls les documents PDF (.pdf), Word (.doc, .docx) et images (.png, .jpg, .jpeg, .webp, .gif) sont acceptés.`;
  }

  return { valid, rejected, errorMessage };
}

