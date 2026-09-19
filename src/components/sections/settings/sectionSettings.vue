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
                    :disabled="authStore.isLoading"
                    label="Enregistrer"
                    type="submit"
                />
            </div>

        </form>

        <form class="main-form" @submit.prevent="editProfile">

            <div class="form-header w-full">
                <h4>Paramètres de compte collaborateur</h4>
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
                    :disabled="authStore.isLoading"
                    label="Enregistrer"
                    type="submit"
                />
            </div>

        </form>

    </section>
</template>

<script lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useAuthStore } from '../../../stores/authStore';
import BaseInput from '../../BaseInput/BaseInput.vue';
import formButton from '../../buttons/formButton.vue';

export default {
    components: {
        BaseInput,
        formButton
    },

    emits: ['update'],

    setup(_props, { emit }) {
        const authStore = useAuthStore();
        const user = computed({
            get: () => authStore.user,
            set: (value) => {
                authStore.user = value;
            },
        });

        const isDisabled = ref<boolean>(false);

        async function editProfile() {
            try {
                isDisabled.value = true;
                await authStore.editProfile({ ...authStore.user, ...user.value });
                emit('update');
            } catch (error) {
                console.error(error);
            } finally {
                isDisabled.value = false;
            }
        }

        onMounted(() => {
            authStore.fetchUserProfile();
        });

        return {
            authStore,
            user,
            editProfile,
            isDisabled,
        };
    },
};
</script>

<style scoped>
.main-form{
    width: 100%;
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
