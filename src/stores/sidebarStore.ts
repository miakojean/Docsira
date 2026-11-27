import { defineStore } from 'pinia';
import { ref } from 'vue';

const STORAGE_KEY = 'docsira_sidebar_reduced';

function readInitialPreference(): boolean | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw === 'true') return true;
    if (raw === 'false') return false;
  } catch {
    // ignore
  }
  return null;
}

export const useSidebarStore = defineStore('sidebar', () => {
  const initial = readInitialPreference();
  const hasExplicitPreference = ref<boolean>(initial !== null);
  const preferredReduced = ref<boolean>(initial ?? false);

  function getEffectiveReduced(defaultReduced = false): boolean {
    if (hasExplicitPreference.value) {
      return preferredReduced.value;
    }
    return defaultReduced;
  }

  function setReduced(value: boolean) {
    hasExplicitPreference.value = true;
    preferredReduced.value = value;
    try {
      localStorage.setItem(STORAGE_KEY, String(value));
    } catch {
      // ignore
    }
    if (typeof document !== 'undefined') {
      document.body.classList.toggle('sidebar-reduced', value);
    }
  }

  function toggleReduced(currentEffective: boolean) {
    setReduced(!currentEffective);
  }

  return {
    hasExplicitPreference,
    preferredReduced,
    getEffectiveReduced,
    setReduced,
    toggleReduced,
  };
});

