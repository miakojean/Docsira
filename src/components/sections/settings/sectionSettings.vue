<template>
    <section class="main-section w-full flex flex-col justify-center items-center gap-4">

        <form class="main-form" @submit.prevent="editProfile">

            <div class="form-header w-full">
                <h3>Paramètres généraux</h3>
            </div>

            <div class="form-body w-full grid grid-cols-3 gap-4">

                <BaseInput
                    label="Nom d'entreprise"
                    v-model="user.username"
                />

                <BaseInput
                    label="Email"
                    v-model="user.email"
                />

                <BaseInput
                    label="Type de compte"
                    v-model="user.account_type"
                />

                <BaseInput
                    label="Nom du responsable"
                    v-model="user.last_name"
                />

                <BaseInput
                    label="Prenoms du responsable"
                    v-model="user.first_name"
                />

            </div>

            <div class="form-footer w-full flex justify-end">
                <formButton
                    :disabled="isDisabled"
                    label="Enregistrer"
                />
            </div>

        </form>
    </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Customer } from '../../../stores/authStore';
import { useAuthStore } from '../../../stores/authStore';
import BaseInput from '../../BaseInput/BaseInput.vue';
import formButton from '../../buttons/formButton.vue';

const authStore = useAuthStore();

const user = ref<Customer>(authStore.user);

const isDisabled = ref<boolean>(false);

async function editProfile() {
  try {
    isDisabled.value = true;
    await authStore.editProfile(user.value);
  } catch (error) {

    console.error(error);
  } finally {
    isDisabled.value = false;
  }
}

onMounted(() => {
  authStore.fetchUserProfile();
})
</script>

<style scoped>
.main-form{
    width: 100%;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    background: #fff;
}

.main-section h3{
    width: 100%;
    text-align: left;
}
</style>
