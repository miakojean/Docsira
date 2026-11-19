import type { Dossier } from '../stores/dossierStore';
import type { DossierTypeOption } from './dossierTypes';

export const DOSSIER_STATUT_OPTIONS: DossierTypeOption[] = [
  { value: 'ALL', label: 'Tous les statuts' },
  { value: 'NOUVEAU', label: 'Nouveaux' },
  { value: 'EN_COURS', label: 'En cours' },
  { value: 'EN_ATTENTE', label: 'En attente' },
  { value: 'TERMINE', label: 'Terminés' },
  { value: 'CLOTURE', label: 'Clôturés' },
];

export const DOSSIER_SORT_OPTIONS: DossierTypeOption[] = [
  { value: 'date_desc', label: "Plus récents d'abord" },
  { value: 'date_asc', label: "Plus anciens d'abord" },
  { value: 'alpha_asc', label: 'Ordre alphabétique (A → Z)' },
  { value: 'alpha_desc', label: 'Ordre alphabétique (Z → A)' },
  { value: 'ref_asc', label: 'Référence (croissante)' },
  { value: 'docs_desc', label: 'Nombre de documents' },
  { value: 'progression_desc', label: 'Progression (décroissante)' },
];

/**
 * Trie une liste de dossiers selon le critère sélectionné.
 */
export function sortDossiers(dossiers: Dossier[], sortBy: string): Dossier[] {
  const list = [...dossiers];
  switch (sortBy) {
    case 'date_asc':
      return list.sort((a, b) => new Date(a.creation_date || 0).getTime() - new Date(b.creation_date || 0).getTime());
    case 'alpha_asc':
      return list.sort((a, b) => (a.title || '').localeCompare(b.title || '', 'fr', { sensitivity: 'base' }));
    case 'alpha_desc':
      return list.sort((a, b) => (b.title || '').localeCompare(a.title || '', 'fr', { sensitivity: 'base' }));
    case 'ref_asc':
      return list.sort((a, b) =>
        (a.reference_affair || '').localeCompare(b.reference_affair || '', 'fr', { sensitivity: 'base', numeric: true })
      );
    case 'docs_desc':
      return list.sort((a, b) => (b.documents_count ?? 0) - (a.documents_count ?? 0));
    case 'progression_desc':
      return list.sort((a, b) => (b.progression ?? 0) - (a.progression ?? 0));
    case 'date_desc':
    default:
      return list.sort((a, b) => new Date(b.creation_date || 0).getTime() - new Date(a.creation_date || 0).getTime());
  }
}

