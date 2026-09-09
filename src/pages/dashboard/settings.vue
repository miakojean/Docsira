<template>
    <div class="main-layout">
        <sidebar/>
        <main class="main-content">
            <h1>Paramètres</h1>
            <BaseInput placeholder="Entrer votre nom"/>
            <BaseInput placeholder="Entrer votre email" type="email"/>
            <BaseInput placeholder="Entrer votre mot de passe" type="password"/>
            <BaseInput placeholder="Confirmer votre mot de passe" type="password"/>
            <mainButton/>
            <secondButton label="Annuler"/>
        </main>
    </div>
</template>

<script setup lang="ts">
import sidebar from '../../components/navbar/sidebar.vue'
import BaseInput from '../../components/BaseInput/BaseInput.vue';
import mainButton from '../../components/buttons/mainButton.vue';
import secondButton from '../../components/buttons/secondButton.vue';

</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: #f9fafb;
}

.main-content {
    flex: 1;
    width: 100%;
    min-width: 0;
    min-height: 0;
    height: 100%;
    display: flex;
    justify-content: flex-start;
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
    overflow: hidden;
    overflow-x: hidden;
    background: #e9ebee;
    scrollbar-width: thin;
}

</style>
