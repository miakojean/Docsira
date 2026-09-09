
<template>
    <isConnected
        :visible="notifPopup.isVisible"
        :action-text="notifPopup.myMessage"
    />
    <RouterView/>
</template>

<script setup lang="ts">
import { RouterView} from 'vue-router';
import { invoke } from "@tauri-apps/api/core";
import { ref, onMounted, onUnmounted } from 'vue';
import {watchConnection} from '../src/services/network'
import isConnected from '../src/components/tools/isConnected.vue'

const notifPopup = ref({
    isVisible: false,
    myMessage: "",
    duration: 8000
});

onMounted(() => {
    // Vérification initiale
    invoke<boolean>("is_online").then((estEnLigne:boolean) => {
        notifPopup.value.isVisible = !estEnLigne;
        notifPopup.value.myMessage="vous êtes hors ligne";
    });

    // Surveillance des changements toutes les 5 secondes
    const intervalId = watchConnection((estEnLigne) => {
        estEnLigne ? notifPopup.value.isVisible = true : notifPopup.value.isVisible = false;
        notifPopup.value.myMessage="vous êtes hors ligne";
    });

    watchConnection((estEnLigne) => {
        if (estEnLigne) {
          notifPopup.value.isVisible = false;
          //notifPopup.value.myMessage="vous êtes hors ligne";

        } else {
          notifPopup.value.isVisible = true;
          notifPopup.value.myMessage="vous êtes hors ligne";
        }
    });

    // N'oubliez pas de nettoyer l'intervalle à la destruction du composant
    onUnmounted(() => clearInterval(intervalId));
});

</script>