<template>
    <main class="page-container">
        <registrationForm @registered="isSuccessModalOpen = true" />
        <succesModale
            :isOpen="isSuccessModalOpen"
            @close="closeSuccessModal"
            @handleEvent="closeSuccessModal"
        />
    </main>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import registrationForm from '../../components/forms/registrationForm.vue';
import succesModale from '../../components/modale/succesModale.vue';

const isSuccessModalOpen = ref(false);
const router = useRouter();

function closeSuccessModal() {
    isSuccessModalOpen.value = false;
    router.push('/login');
}
</script>

<style scoped>



</style>
