<template>
    <!-- Écran de chargement au lancement de l'application -->
    <Transition name="splash-fade">
        <div v-if="isBooting" class="app-splash-screen">
            <div class="splash-content">
                <LogoLoader size="xl" />
                <div class="splash-branding">
                    <h2 class="splash-title">DocSira</h2>
                    <p class="splash-subtitle">Préparation de votre espace de travail...</p>
                </div>
            </div>
        </div>
    </Transition>

    <isConnected
        :visible="notifPopup.isVisible"
        :action-text="notifPopup.myMessage"
        :is-online="notifPopup.isOnline"
    />
    <RouterView/>
</template>

<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router';
import { ref, onMounted, onUnmounted } from 'vue';
import { checkConnection, watchConnection } from '../src/services/network';
import isConnected from '../src/components/tools/isConnected.vue';
import LogoLoader from '../src/components/tools/LogoLoader.vue';

const router = useRouter();
const isBooting = ref(true);

const notifPopup = ref({
    isVisible: false,
    myMessage: "",
    isOnline: false,
    duration: 8000
});

let intervalId: ReturnType<typeof setInterval> | undefined;
let bootTimerId: ReturnType<typeof setTimeout> | undefined;

onMounted(async () => {
    const minSplashDelay = new Promise((resolve) => {
        bootTimerId = setTimeout(resolve, 1500);
    });

    // Attente parallèle du routeur, de la vérification réseau initiale et du délai d'animation fluide
    const [, estEnLigne] = await Promise.all([
        router.isReady(),
        checkConnection().catch(() => true),
        minSplashDelay,
    ]);

    isBooting.value = false;

    if (!estEnLigne) {
        notifPopup.value.isVisible = true;
        notifPopup.value.myMessage = "Vous n'êtes pas connecté à internet";
    }

    intervalId = watchConnection((enLigne) => {
        notifPopup.value.isVisible = true;
        notifPopup.value.isOnline = enLigne;
        if (enLigne) {
            notifPopup.value.myMessage = "Vous êtes connecté à internet";
        } else {
            notifPopup.value.myMessage = "Vous n'êtes pas connecté à internet";
        }
    });
});

onUnmounted(() => {
    if (intervalId) clearInterval(intervalId);
    if (bootTimerId) clearTimeout(bootTimerId);
});
</script>

<style scoped>
.app-splash-screen {
    position: fixed;
    inset: 0;
    z-index: 99999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle at 50% 45%, #ffffff 0%, #f1f5f9 100%);
    user-select: none;
}

.splash-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.splash-branding {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
    text-align: center;
}

.splash-title {
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #0c306c;
    margin: 0;
}

.splash-subtitle {
    font-size: 0.9rem;
    font-weight: 400;
    color: #64748b;
    margin: 0;
    animation: subtitle-pulse 2s ease-in-out infinite;
}

@keyframes subtitle-pulse {
    0%, 100% {
        opacity: 0.65;
    }
    50% {
        opacity: 1;
    }
}

/* Transition de sortie fluide et immersive */
.splash-fade-leave-active {
    transition: opacity 0.45s cubic-bezier(0.4, 0, 0.2, 1), transform 0.45s cubic-bezier(0.4, 0, 0.2, 1);
}

.splash-fade-leave-to {
    opacity: 0;
    transform: scale(1.03);
}
</style>
