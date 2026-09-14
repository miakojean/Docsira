<template>
    <section class="main-section w-full flex flex-col justify-center items-center gap-4">

        <h3>Paramètres généraux</h3>

        <form class="main-form">

            <BaseInput
                label="Nom d'entreprise"
                v-model="user.username"
            />

            <BaseInput
                label="Nom de famille"
                v-model="user.last_name"
            />

            <BaseInput
                label="Prenoms"
                v-model="user.first_name"
            />

            <BaseInput
                label="Email"
                v-model="user.email"
            />

            <BaseInput
                label="Nom d'entreprise"
                v-model="user.username"
            />

        </form>
    </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Customer } from '../../../stores/authStore';
import { useAuthStore } from '../../../stores/authStore';
import BaseInput from '../../BaseInput/BaseInput.vue';

const authStore = useAuthStore();

const user = ref<Customer>(authStore.user);

onMounted(() => {
  authStore.fetchUserProfile();
})
</script>

<style scoped>
.main-form{
    width: 100%;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1rem;
    padding: 1rem;
    background: #fff;

}
</style>
