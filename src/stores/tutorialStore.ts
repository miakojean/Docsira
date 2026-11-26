import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { load } from '@tauri-apps/plugin-store';
import { api } from '../services/api';
import { useAuthStore, type Customer } from './authStore';
import { useDocumentStore } from './documentStore';

export type TutorialTrack = 'basic' | 'advanced';
export type TutorialPhase = 'idle' | 'welcome' | 'steps';

export type TutorialActionKey =
  | 'visit_customers'
  | 'client_created'
  | 'visit_workspace'
  | 'dossier_created'
  | 'visit_myspace'
  | 'open_affair_detail'
  | 'open_sira_tab'
  | 'document_uploaded'
  | 'open_versions'
  | 'open_comments'
  | 'visit_settings'
  | 'visit_collaborators';

export interface TutorialStepViewerFallback {
  title?: string;
  description?: string;
  targetSelector?: string | string[];
  actionHint?: string;
}

export interface TutorialStep {
  id: string;
  title: string;
  description: string;
  targetSelector?: string | string[];
  requiredAction?: TutorialActionKey;
  actionHint?: string;
  completedHint?: string;
  requiresEdit?: boolean;
  viewerFallback?: TutorialStepViewerFallback;
}

export const BASIC_STEPS: TutorialStep[] = [
  {
    id: 'basic-open-customers',
    title: 'Ouvrir votre répertoire Clients',
    description:
      'Vos clients regroupent toutes leurs fiches et les dossiers qui leur sont rattachés.',
    targetSelector: '[data-tour="nav-customers"]',
    requiredAction: 'visit_customers',
    actionHint: 'Cliquez sur Clients dans le menu à gauche',
    completedHint: 'Répertoire Clients ouvert',
  },
  {
    id: 'basic-create-client',
    title: 'Créer votre premier client',
    description:
      'Ajoutez une fiche client (personne physique ou morale) pour pouvoir y associer un dossier.',
    targetSelector: '[data-tour="header-add-btn"]',
    requiredAction: 'client_created',
    actionHint: 'Cliquez sur + puis enregistrez un client',
    completedHint: 'Client créé',
    requiresEdit: true,
    viewerFallback: {
      title: 'Consulter les clients',
      description:
        'Votre rôle Lecteur permet de consulter les fiches clients et leurs dossiers sans pouvoir en créer.',
      targetSelector: undefined,
      actionHint: 'Cliquez sur Suivant pour continuer la visite',
    },
  },
  {
    id: 'basic-open-workspace',
    title: 'Accéder au Workspace',
    description:
      "Le Workspace rassemble les dossiers d'affaires partagés avec votre cabinet.",
    targetSelector: '[data-tour="nav-workspace"]',
    requiredAction: 'visit_workspace',
    actionHint: 'Cliquez sur Workspace dans le menu à gauche',
    completedHint: 'Workspace ouvert',
  },
  {
    id: 'basic-create-dossier',
    title: 'Créer votre premier dossier',
    description:
      "Créez un dossier d'affaire lié à un client pour y déposer vos pièces et suivre son avancement.",
    targetSelector: '[data-tour="header-add-btn"]',
    requiredAction: 'dossier_created',
    actionHint: 'Cliquez sur + puis créez un dossier lié à votre client',
    completedHint: 'Dossier créé',
    requiresEdit: true,
    viewerFallback: {
      title: 'Parcourir les dossiers',
      description:
        'Votre rôle Lecteur permet de consulter les dossiers du Workspace et leurs pièces.',
      targetSelector: undefined,
      actionHint: 'Cliquez sur Suivant pour continuer la visite',
    },
  },
  {
    id: 'basic-open-myspace',
    title: 'Découvrir Mon espace',
    description:
      'Travaillez sur des dossiers locaux sur votre ordinateur, accessibles même hors connexion.',
    targetSelector: '[data-tour="nav-myspace"]',
    requiredAction: 'visit_myspace',
    actionHint: 'Cliquez sur Mon espace dans le menu à gauche',
    completedHint: 'Mon espace ouvert',
  },
  {
    id: 'basic-support',
    title: 'Support client & fonctions avancées',
    description:
      'Vous maîtrisez les bases. Rendez-vous dans Support client quand vous souhaiterez lancer la visite interactive des fonctions avancées (SIRA, versioning, paramètres, collaborateurs).',
    targetSelector: '[data-tour="nav-support"]',
  },
];

export const ADVANCED_STEPS: TutorialStep[] = [
  {
    id: 'adv-open-dossier',
    title: 'Ouvrir un dossier du Workspace',
    description:
      "Sélectionnez un dossier existant (ou créez-en un avec +) pour explorer l'espace de travail d'une affaire.",
    targetSelector: ['[data-tour="workspace-dossiers-grid"] > :first-child', '[data-tour="header-add-btn"]'],
    requiredAction: 'open_affair_detail',
    actionHint: 'Cliquez sur un dossier pour l’ouvrir (ou créez-en un avec +)',
    completedHint: 'Dossier ouvert',
  },
  {
    id: 'adv-sira-tab',
    title: 'Suivi SIRA et historique',
    description:
      'Chaque catégorie de pièce (Identification, Constitution, Procédures, Livrables, Clôture) fait progresser le dossier de 10 % à 100 %.',
    targetSelector: '[data-tour="affair-tab-sira"]',
    requiredAction: 'open_sira_tab',
    actionHint: 'Cliquez sur l’onglet Historique dans le panneau de gauche',
    completedHint: 'Suivi SIRA affiché',
  },
  {
    id: 'adv-upload-doc',
    title: 'Importer un document dans le dossier',
    description:
      'Ajoutez une pièce (PDF, Word, image) en choisissant sa catégorie SIRA afin de mettre à jour la progression.',
    targetSelector: ['[data-tour="affair-add-doc"]', '[data-tour="affair-empty-add-doc"]'],
    requiredAction: 'document_uploaded',
    actionHint: 'Cliquez sur Ajouter un document puis importez un fichier',
    completedHint: 'Document ajouté',
    requiresEdit: true,
    viewerFallback: {
      title: 'Consulter les documents',
      description:
        'En lecture seule, vous pouvez prévisualiser les pièces du dossier sans ajouter ni modifier de fichier.',
      targetSelector: undefined,
      actionHint: 'Cliquez sur Suivant pour continuer',
    },
  },
  {
    id: 'adv-versioning',
    title: 'Versioning des documents (v1, v2…)',
    description:
      "Remplacez un fichier depuis l'aperçu ou le menu ⋮ d'une pièce : chaque version garde son auteur, sa note et peut être restaurée en un clic.",
    targetSelector: '[data-tour="affair-files-grid"] > :first-child',
    requiredAction: 'open_versions',
    actionHint: 'Ouvrez « Versions » (menu ⋮) ou ajoutez une nouvelle version depuis l’aperçu',
    completedHint: 'Versioning validé',
  },
  {
    id: 'adv-comments',
    title: 'Commentaires & mentions @Document',
    description:
      'Échangez en équipe dans le panneau latéral droit et tapez @ pour citer directement un document du dossier.',
    targetSelector: '[data-tour="affair-comments-toggle"]',
    requiredAction: 'open_comments',
    actionHint: 'Cliquez sur l’icône Commentaires à droite (puis essayez @)',
    completedHint: 'Panneau commentaires ouvert',
  },
  {
    id: 'adv-settings',
    title: 'Ouvrir les Paramètres',
    description:
      "Accédez aux réglages du compte (profil, email, mot de passe) ainsi qu'à la gestion des collaborateurs du cabinet.",
    targetSelector: '[data-tour="nav-settings"]',
    requiredAction: 'visit_settings',
    actionHint: 'Cliquez sur Paramètres dans le menu à gauche',
    completedHint: 'Paramètres ouverts',
  },
  {
    id: 'adv-settings-to-collaborators',
    title: 'Paramètres généraux & sécurité',
    description:
      'Modifiez ici votre profil (Paramètres généraux) et votre mot de passe (Paramètres de sécurité). Ouvrez ensuite Mes collaborateurs pour gérer l’équipe.',
    targetSelector: '[data-tour="settings-nav-collaborators"]',
    requiredAction: 'visit_collaborators',
    actionHint: 'Cliquez sur Mes collaborateurs dans le menu Paramètres',
    completedHint: 'Gestion des collaborateurs ouverte',
  },
  {
    id: 'adv-collaborators',
    title: 'Système de collaborateurs & rôles',
    description:
      'Invitez vos collègues par e-mail avec code d’accès et attribuez un rôle : Administrateur (gestion complète), Collaborateur (édition) ou Lecteur (consultation et commentaires). Vous pouvez aussi générer des liens de partage expirables (.zip) sur vos dossiers.',
    targetSelector: ['[data-tour="header-add-btn"]', '[data-tour="collaborators-grid"]'],
  },
];

interface CachedTutorialState {
  basicCompleted: boolean;
  advancedCompleted: boolean;
}

function getUserCacheKey(user: Customer | null | undefined): string {
  const idPart = user?.id ? String(user.id) : '';
  const namePart = user?.username || user?.email || '';
  return idPart || namePart || 'anonymous';
}

async function readLocalTutorialCache(userKey: string): Promise<CachedTutorialState> {
  const storageKey = `docsira_tutorial_${userKey}`;
  try {
    const store = await load('tutorialStore.json', { autoSave: false });
    const val = await store.get<CachedTutorialState>(storageKey);
    if (val) return val;
  } catch {
    // Fallback localStorage (environnement web hors Tauri)
  }
  try {
    const raw = localStorage.getItem(storageKey);
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<CachedTutorialState>;
      return {
        basicCompleted: Boolean(parsed.basicCompleted),
        advancedCompleted: Boolean(parsed.advancedCompleted),
      };
    }
  } catch {
    // ignore
  }
  return { basicCompleted: false, advancedCompleted: false };
}

async function writeLocalTutorialCache(userKey: string, state: CachedTutorialState) {
  const storageKey = `docsira_tutorial_${userKey}`;
  try {
    localStorage.setItem(storageKey, JSON.stringify(state));
  } catch {
    // ignore
  }
  try {
    const store = await load('tutorialStore.json', { autoSave: false });
    await store.set(storageKey, state);
    await store.save();
  } catch {
    // ignore si hors Tauri
  }
}

export const useTutorialStore = defineStore('tutorial', () => {
  // States
  const activeTrack = ref<TutorialTrack | null>(null);
  const phase = ref<TutorialPhase>('idle');
  const currentStepIndex = ref(0);
  const basicCompleted = ref(false);
  const advancedCompleted = ref(false);
  const checkedUserKey = ref<string | null>(null);
  const currentUserKey = ref<string>('anonymous');
  const completedActions = ref<TutorialActionKey[]>([]);
  const pendingAutoAdvance = ref(false);

  // Getters
  const isOpen = computed(() => phase.value !== 'idle' && activeTrack.value !== null);

  const activeSteps = computed<TutorialStep[]>(() => {
    if (activeTrack.value === 'advanced') return ADVANCED_STEPS;
    if (activeTrack.value === 'basic') return BASIC_STEPS;
    return [];
  });

  const currentStep = computed<TutorialStep | null>(() => {
    if (phase.value !== 'steps') return null;
    const rawStep = activeSteps.value[currentStepIndex.value];
    if (!rawStep) return null;

    const authStore = useAuthStore();
    if (rawStep.requiresEdit && !authStore.canEdit && rawStep.viewerFallback) {
      return {
        ...rawStep,
        title: rawStep.viewerFallback.title ?? rawStep.title,
        description: rawStep.viewerFallback.description ?? rawStep.description,
        targetSelector: rawStep.viewerFallback.targetSelector,
        actionHint: rawStep.viewerFallback.actionHint,
        requiredAction: undefined,
      };
    }

    if (rawStep.id === 'adv-versioning' && useDocumentStore().documents.length === 0) {
      return {
        ...rawStep,
        targetSelector: undefined,
        requiredAction: undefined,
        actionHint: 'Aucun document dans ce dossier pour tester les versions — cliquez sur Suivant',
      };
    }

    return rawStep;
  });

  const totalSteps = computed(() => activeSteps.value.length);
  const isFirstStep = computed(() => currentStepIndex.value <= 0);
  const isLastStep = computed(
    () => totalSteps.value > 0 && currentStepIndex.value >= totalSteps.value - 1
  );

  const isCurrentStepSatisfied = computed(() => {
    const step = currentStep.value;
    if (!step) return true;
    if (step.id === 'adv-versioning' && useDocumentStore().documents.length === 0) {
      return true;
    }
    if (!step.requiredAction) return true;
    return completedActions.value.includes(step.requiredAction);
  });

  // Actions
  function resetProgressState() {
    completedActions.value = [];
    pendingAutoAdvance.value = false;
  }

  async function syncForUser(user: Customer | null | undefined): Promise<boolean> {
    const key = getUserCacheKey(user);
    if (!key || key === 'anonymous') return false;
    currentUserKey.value = key;

    const cached = await readLocalTutorialCache(key);
    const basicDone = Boolean(user?.has_completed_onboarding) || cached.basicCompleted;
    const advancedDone = Boolean(user?.has_completed_advanced_onboarding) || cached.advancedCompleted;

    basicCompleted.value = basicDone;
    advancedCompleted.value = advancedDone;

    if (checkedUserKey.value === key) {
      return false;
    }
    checkedUserKey.value = key;

    if (!basicDone && phase.value === 'idle') {
      activeTrack.value = 'basic';
      phase.value = 'welcome';
      currentStepIndex.value = 0;
      resetProgressState();
      return true;
    }
    return false;
  }

  function startBasicTour(withWelcome = true) {
    activeTrack.value = 'basic';
    currentStepIndex.value = 0;
    resetProgressState();
    phase.value = withWelcome ? 'welcome' : 'steps';
  }

  function beginStepsFromWelcome() {
    if (!activeTrack.value) activeTrack.value = 'basic';
    currentStepIndex.value = 0;
    resetProgressState();
    phase.value = 'steps';
  }

  function startAdvancedTour() {
    activeTrack.value = 'advanced';
    currentStepIndex.value = 0;
    resetProgressState();
    phase.value = 'steps';
  }

  function notifyAction(action: TutorialActionKey) {
    if (phase.value !== 'steps') return;
    if (!completedActions.value.includes(action)) {
      completedActions.value = [...completedActions.value, action];
    }
    if (currentStep.value?.requiredAction === action) {
      pendingAutoAdvance.value = true;
    }
  }

  function consumeAutoAdvance() {
    if (!pendingAutoAdvance.value || phase.value !== 'steps') return;
    pendingAutoAdvance.value = false;
    nextStep();
  }

  function nextStep() {
    if (!isCurrentStepSatisfied.value) return;
    pendingAutoAdvance.value = false;
    if (isLastStep.value) {
      void completeTutorial();
      return;
    }
    currentStepIndex.value += 1;
  }

  function prevStep() {
    pendingAutoAdvance.value = false;
    if (currentStepIndex.value > 0) {
      currentStepIndex.value -= 1;
    }
  }

  function goToStep(index: number) {
    pendingAutoAdvance.value = false;
    if (index >= 0 && index < activeSteps.value.length) {
      currentStepIndex.value = index;
    }
  }

  async function persistTrackCompletion(track: TutorialTrack) {
    if (track === 'advanced') {
      advancedCompleted.value = true;
    } else {
      basicCompleted.value = true;
    }

    const authStore = useAuthStore();
    const key = getUserCacheKey(authStore.user);
    const effectiveKey = key !== 'anonymous' ? key : currentUserKey.value;
    if (effectiveKey && effectiveKey !== 'anonymous') {
      await writeLocalTutorialCache(effectiveKey, {
        basicCompleted: basicCompleted.value,
        advancedCompleted: advancedCompleted.value,
      });
    }

    await authStore.updateLocalOnboardingFlags(
      track === 'advanced'
        ? { has_completed_advanced_onboarding: true }
        : { has_completed_onboarding: true }
    );

    try {
      await api('/account/onboarding/', 'POST', { track }, { requireAuth: true });
    } catch {
      // Déjà persisté localement ; sera resynchronisé ultérieurement si besoin
    }
  }

  async function skipTutorial() {
    const track = activeTrack.value;
    phase.value = 'idle';
    activeTrack.value = null;
    currentStepIndex.value = 0;
    resetProgressState();
    if (track) {
      await persistTrackCompletion(track);
    }
  }

  async function completeTutorial() {
    const track = activeTrack.value;
    phase.value = 'idle';
    activeTrack.value = null;
    currentStepIndex.value = 0;
    resetProgressState();
    if (track) {
      await persistTrackCompletion(track);
    }
  }

  function resetOnLogout() {
    phase.value = 'idle';
    activeTrack.value = null;
    currentStepIndex.value = 0;
    checkedUserKey.value = null;
    basicCompleted.value = false;
    advancedCompleted.value = false;
    resetProgressState();
  }

  return {
    // states
    activeTrack,
    phase,
    currentStepIndex,
    basicCompleted,
    advancedCompleted,
    checkedUserKey,
    completedActions,
    pendingAutoAdvance,
    // getters
    isOpen,
    activeSteps,
    currentStep,
    totalSteps,
    isFirstStep,
    isLastStep,
    isCurrentStepSatisfied,
    // actions
    syncForUser,
    startBasicTour,
    beginStepsFromWelcome,
    startAdvancedTour,
    notifyAction,
    consumeAutoAdvance,
    nextStep,
    prevStep,
    goToStep,
    skipTutorial,
    completeTutorial,
    resetOnLogout,
  };
});
