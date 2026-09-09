<template>
    <isConnected
        :visible="notifPopup.isVisible"
        :action="notifPopup.myMessage"
    />
    <RouterView/>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { invoke } from "@tauri-apps/api/core";
import { ref, onMounted, onUnmounted } from 'vue';
import { watchConnection } from '../src/services/network';
import isConnected from '../src/components/tools/isConnected.vue';

const notifPopup = ref({
    isVisible: false,
    myMessage: "",
    duration: 8000
});

// Déclaration de l'ID d'intervalle à la racine pour y accéder dans les hooks
let intervalId: any;

onMounted(() => {
    // 1. Vérification initiale (logique corrigée)
    invoke<boolean>("is_online").then((estEnLigne: boolean) => {
        if (estEnLigne) {
            notifPopup.value.isVisible = false;
        } else {
            notifPopup.value.isVisible = true;
            notifPopup.value.myMessage = "Vous êtes hors ligne";
        }
    });

    // 2. Une seule surveillance active avec la bonne logique
    intervalId = watchConnection((estEnLigne: boolean) => {
        if (estEnLigne) {
            notifPopup.value.isVisible = false;
        } else {
            notifPopup.value.isVisible = true;
            notifPopup.value.myMessage = "Vous êtes hors ligne";
        }
    });
});

// 3. Nettoyage placé correctement à la racine du composant
onUnmounted(() => {
    if (intervalId) {
        clearInterval(intervalId);
    }
});
</script>
