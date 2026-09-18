
<template>
    <isConnected
        :visible="notifPopup.isVisible"
        :action-text="notifPopup.myMessage"
        :is-online="notifPopup.isOnline"
    />
    <RouterView/>
</template>

<script setup lang="ts">
import { RouterView} from 'vue-router';
import { ref, onMounted, onUnmounted } from 'vue';
import {checkConnection, watchConnection} from '../src/services/network'
import isConnected from '../src/components/tools/isConnected.vue'

const notifPopup = ref({
    isVisible: false,
    myMessage: "",
    isOnline: false,
    duration: 8000
});

onMounted(() => {
    // Vérification initiale
    checkConnection().then((estEnLigne:boolean) => {
        if (!estEnLigne) {
            notifPopup.value.isVisible = true;
            notifPopup.value.myMessage = "Vous n'êtes pas connecté à internet";
        }
    });

    const intervalId = watchConnection((estEnLigne) => {
        notifPopup.value.isVisible = true;
        notifPopup.value.isOnline = estEnLigne;
        if (estEnLigne) {
          notifPopup.value.myMessage = "Vous êtes connecté à internet";
        } else {
          notifPopup.value.myMessage = "Vous n'êtes pas connecté à internet";
        }
    });

    // N'oubliez pas de nettoyer l'intervalle à la destruction du composant
    onUnmounted(() => clearInterval(intervalId));
});

</script>