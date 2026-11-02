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
  const isLoading = ref(false);
  const errorMessage = ref('');

  async function fetchHistory(affairId: string) {
    if (!affairId) return [];
    isLoading.value = true;
    errorMessage.value = '';
    try {
      const response = await api(`/sira/affairs/${affairId}/history/`, 'GET');
      if (!response.ok) {
        errorMessage.value = "Impossible de récupérer l'historique SIRA.";
        histories.value = [];
        return [];
      }
      const data = await response.json();
      const items: SiraHistoryItem[] = Array.isArray(data) ? data : (data.results ?? []);
      histories.value = items;
      return items;
    } catch (err) {
      console.error(err);
      errorMessage.value = 'Erreur lors du chargement du journal SIRA.';
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  return {
    histories,
    isLoading,
    errorMessage,
    fetchHistory,
  };
});
