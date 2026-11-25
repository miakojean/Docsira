import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from '../services/api';
import type { SiraCategory } from './documentStore';

export interface SiraHistoryItem {
  id: string;
  affair_id: string;
  previous_progression: number;
  new_progression: number;
  action_type: string;
  document_title?: string | null;
  category?: SiraCategory | null;
  author?: string | null;
  timestamp: string;
  details: string;
}

export interface SiraStep {
  category: SiraCategory;
  label: string;
  threshold: number;
  description: string;
  iconName: string;
}

export const SIRA_STEPS: SiraStep[] = [
  {
    category: 'IDENTIFICATION',
    label: 'Identification',
    threshold: 45,
    description: 'Pièces d’identité, KBIS, mandat initial',
    iconName: 'user',
  },
  {
    category: 'CONSTITUTION',
    label: 'Constitution',
    threshold: 60,
    description: 'Statuts, conventions, actes constitutifs',
    iconName: 'folder',
  },
  {
    category: 'PROCEDURES',
    label: 'Procédures',
    threshold: 75,
    description: 'Dépôts greffe, formalités, assignations',
    iconName: 'scale',
  },
  {
    category: 'LIVRABLES',
    label: 'Livrables',
    threshold: 90,
    description: 'Actes signés, PV définitifs, contrats',
    iconName: 'box',
  },
  {
    category: 'CLOTURE',
    label: 'Clôture',
    threshold: 100,
    description: 'Facturation finale, décharge, archivage',
    iconName: 'check',
  },
];

export function getSiraCategoryMeta(category?: SiraCategory | string | null) {
  switch (category) {
    case 'IDENTIFICATION':
      return {
        label: 'Identification',
        threshold: 45,
        color: '#0284c7',
        bg: '#e0f2fe',
        border: '#bae6fd',
      };
    case 'CONSTITUTION':
      return {
        label: 'Constitution',
        threshold: 60,
        color: '#4f46e5',
        bg: '#e0e7ff',
        border: '#c7d2fe',
      };
    case 'PROCEDURES':
      return {
        label: 'Procédures',
        threshold: 75,
        color: '#7c3aed',
        bg: '#ede9fe',
        border: '#ddd6fe',
      };
    case 'LIVRABLES':
      return {
        label: 'Livrables',
        threshold: 90,
        color: '#d97706',
        bg: '#fef3c7',
        border: '#fde68a',
      };
    case 'CLOTURE':
      return {
        label: 'Clôture',
        threshold: 100,
        color: '#059669',
        bg: '#d1fae5',
        border: '#a7f3d0',
      };
    default:
      return {
        label: 'Non classé',
        threshold: 10,
        color: '#64748b',
        bg: '#f1f5f9',
        border: '#e2e8f0',
      };
  }
}

export const useSiraStore = defineStore('sira', () => {
  const histories = ref<SiraHistoryItem[]>([]);
  const totalCount = ref(0);
  const currentPage = ref(1);
  const hasMore = ref(false);
  const activeActionFilter = ref('');
  const isLoading = ref(false);
  const errorMessage = ref('');

  async function fetchHistory(
    affairId: string,
    options?: { actionType?: string; page?: number; append?: boolean }
  ) {
    if (!affairId) return [];
    const targetPage = options?.page ?? 1;
    const actionType = options?.actionType !== undefined ? options.actionType : activeActionFilter.value;
    if (options?.actionType !== undefined) {
      activeActionFilter.value = options.actionType;
    }

    isLoading.value = true;
    errorMessage.value = '';
    try {
      const params = new URLSearchParams({ page: String(targetPage) });
      if (actionType) {
        params.set('action_type', actionType);
      }

      const response = await api(`/sira/affairs/${affairId}/history/?${params.toString()}`, 'GET');
      if (!response.ok) {
        errorMessage.value = "Impossible de récupérer l'historique SIRA.";
        if (!options?.append) {
          histories.value = [];
          totalCount.value = 0;
          hasMore.value = false;
        }
        return [];
      }
      const data = await response.json();
      const items: SiraHistoryItem[] = Array.isArray(data) ? data : (data.results ?? []);
      totalCount.value = Array.isArray(data) ? items.length : Number(data.count ?? items.length);
      hasMore.value = Boolean(!Array.isArray(data) && data.next);
      currentPage.value = targetPage;

      if (options?.append) {
        const existingIds = new Set(histories.value.map((h) => h.id));
        histories.value = [...histories.value, ...items.filter((h) => !existingIds.has(h.id))];
      } else {
        histories.value = items;
      }
      return items;
    } catch (err) {
      console.error(err);
      errorMessage.value = 'Erreur lors du chargement du journal SIRA.';
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMoreHistory(affairId: string) {
    if (!hasMore.value || isLoading.value) return [];
    return fetchHistory(affairId, {
      actionType: activeActionFilter.value,
      page: currentPage.value + 1,
      append: true,
    });
  }

  return {
    histories,
    totalCount,
    currentPage,
    hasMore,
    activeActionFilter,
    isLoading,
    errorMessage,
    fetchHistory,
    loadMoreHistory,
  };
});
