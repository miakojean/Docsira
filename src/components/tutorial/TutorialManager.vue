<template>
  <Teleport to="body">
    <Transition name="welcome-fade">
      <TutorialWelcomeModal
        v-if="tutorialStore.phase === 'welcome'"
        :userName="displayName"
        @start="handleStartFromWelcome"
        @skip="tutorialStore.skipTutorial()"
      />
    </Transition>

    <template v-if="tutorialStore.phase === 'steps' && tutorialStore.currentStep && tutorialStore.activeTrack">
      <TutorialSpotlightMask
        :active="true"
        :suspended="hasAppModalOpen"
        :targetSelector="tutorialStore.currentStep.targetSelector"
        :recheckKey="`${route.fullPath}:${tutorialStore.currentStep.id}`"
        @targetRect="targetRect = $event"
      />

      <TutorialTooltipCard
        :step="tutorialStore.currentStep"
        :track="tutorialStore.activeTrack"
        :currentIndex="tutorialStore.currentStepIndex"
        :totalSteps="tutorialStore.totalSteps"
        :targetRect="targetRect"
        :isFirst="tutorialStore.isFirstStep"
        :isLast="tutorialStore.isLastStep"
        :canAdvance="tutorialStore.isCurrentStepSatisfied"
        :isSatisfied="tutorialStore.isCurrentStepSatisfied"
        :docked="hasAppModalOpen"
        @next="tutorialStore.nextStep()"
        @prev="tutorialStore.prevStep()"
        @skip="tutorialStore.skipTutorial()"
        @finish="tutorialStore.completeTutorial()"
        @openSupport="handleOpenSupport"
      />
    </template>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { useTutorialStore } from '../../stores/tutorialStore';
import TutorialSpotlightMask from './TutorialSpotlightMask.vue';
import TutorialTooltipCard from './TutorialTooltipCard.vue';
import TutorialWelcomeModal from './TutorialWelcomeModal.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const tutorialStore = useTutorialStore();

const targetRect = ref<DOMRect | null>(null);
const hasAppModalOpen = ref(false);

let modalObserver: MutationObserver | null = null;
let autoAdvanceTimer: ReturnType<typeof setTimeout> | null = null;

function clearAutoAdvanceTimer() {
  if (autoAdvanceTimer !== null) {
    clearTimeout(autoAdvanceTimer);
    autoAdvanceTimer = null;
  }
}

function updateAppModalState() {
  if (typeof document === 'undefined') {
    hasAppModalOpen.value = false;
    return;
  }
  hasAppModalOpen.value = Boolean(
    document.querySelector('.modal-overlay, .versions-modal-overlay, .preview-backdrop')
  );
}

const displayName = computed(() => {
  const u = authStore.user;
  const full = `${u?.first_name || ''} ${u?.last_name || ''}`.trim();
  return full || u?.username || '';
});

function detectRouteActions(path: string) {
  if (tutorialStore.phase !== 'steps') return;

  if (path === '/dashboard/Customer' || path === '/dashboard/Customer/') {
    tutorialStore.notifyAction('visit_customers');
  } else if (path === '/dashboard/affairs' || path === '/dashboard/affairs/') {
    tutorialStore.notifyAction('visit_workspace');
  } else if (/^\/dashboard\/affairs\/[^/]+/.test(path)) {
    tutorialStore.notifyAction('open_affair_detail');
  } else if (path.startsWith('/dashboard/mySpace')) {
    tutorialStore.notifyAction('visit_myspace');
  } else if (path.startsWith('/dashboard/settings/collaborators')) {
    tutorialStore.notifyAction('visit_collaborators');
  } else if (path === '/dashboard/settings' || path === '/dashboard/settings/') {
    tutorialStore.notifyAction('visit_settings');
  }
}

watch(
  () => [
    authStore.isAuthenticated,
    authStore.user?.id,
    authStore.user?.username,
    authStore.user?.has_completed_onboarding,
    route.path,
  ] as const,
  async ([isAuth]) => {
    if (!isAuth) {
      tutorialStore.resetOnLogout();
      return;
    }
    if (!route.meta?.requiresAuth) return;
    const u = authStore.user;
    if (!u?.id && !u?.username) return;
    await tutorialStore.syncForUser(u);
  },
  { immediate: true }
);

watch(
  () => [tutorialStore.phase, tutorialStore.activeTrack, tutorialStore.currentStepIndex] as const,
  async ([phase, track, stepIndex]) => {
    if (phase !== 'steps' || stepIndex !== 0) return;

    if (track === 'advanced') {
      if (route.path !== '/dashboard/affairs' && !/^\/dashboard\/affairs\/[^/]+/.test(route.path)) {
        await router.push('/dashboard/affairs');
      }
      detectRouteActions(router.currentRoute.value.path);
    } else if (track === 'basic' && route.path !== '/dashboard') {
      await router.push('/dashboard');
    }
  }
);

watch(
  () => [tutorialStore.phase, route.path] as const,
  ([phase, path]) => {
    if (phase === 'steps') {
      detectRouteActions(path);
    }
  },
  { immediate: true }
);

watch(
  () => [tutorialStore.pendingAutoAdvance, hasAppModalOpen.value, tutorialStore.currentStepIndex] as const,
  ([pending, modalOpen]) => {
    clearAutoAdvanceTimer();
    if (pending && !modalOpen && tutorialStore.phase === 'steps') {
      autoAdvanceTimer = setTimeout(() => {
        autoAdvanceTimer = null;
        tutorialStore.consumeAutoAdvance();
      }, 550);
    }
  }
);

async function handleStartFromWelcome() {
  if (route.path !== '/dashboard') {
    await router.push('/dashboard');
  }
  tutorialStore.beginStepsFromWelcome();
}

async function handleOpenSupport() {
  await tutorialStore.completeTutorial();
  await router.push('/dashboard/support');
}

onMounted(() => {
  updateAppModalState();
  if (typeof MutationObserver !== 'undefined' && typeof document !== 'undefined') {
    modalObserver = new MutationObserver(() => {
      updateAppModalState();
    });
    modalObserver.observe(document.body, { childList: true, subtree: true });
  }
});

onUnmounted(() => {
  clearAutoAdvanceTimer();
  if (modalObserver) {
    modalObserver.disconnect();
    modalObserver = null;
  }
});
</script>

<style>
.welcome-fade-enter-active,
.welcome-fade-leave-active {
  transition: opacity 0.28s ease;
}

.welcome-fade-enter-from,
.welcome-fade-leave-to {
  opacity: 0;
}
</style>
