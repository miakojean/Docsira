<template>
    <section class="main-section w-full flex flex-col justify-center items-center gap-4">

        <form class="main-form" @submit.prevent="editProfile">

            <div class="form-header w-full">
                <h3>Paramètres généraux</h3>
            </div>

            <div class="form-body w-full grid grid-cols-3 gap-4">

                <BaseInput
                    label="Nom d'utilisateur"
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

        <form class="main-form" @submit.prevent="handleChangePassword">

            <div class="attention-paragraph w-full flex justify-start gap-4">
                <p class="">Pensez à changer votre mot si vous êtes nouveau!</p>

                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                </svg>
            </div>


            <div class="form-header w-full">
                <h4>Paramètres de sécurité</h4>
            </div>

            <div class="form-body w-full grid grid-cols-3 gap-4" v-if="changePassword">

                <BaseInput
                    label="Mot de passe actuel"
                    placeholder="Entre l'actuel mot de passe"
                    type="password"
                />

                <BaseInput
                    label="Nouveau mot de passe actuel"
                    placeholder="Entre l'actuel mot de passe"
                    type="password"
                />

                <BaseInput
                    label="Confirmer le nouveau mot de passe actuel"
                    placeholder="Entre l'actuel mot de passe"
                    type="password"
                />

            </div>

            <div class="form-footer w-full flex justify-end">
                <formButton
                    :disabled="authStore.isLoading"
                    label="changer mot de passe"
                    type="button"
                    @click="changePassword = !changePassword"
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

        const passwordForm = ref({
            old_password:"",
            new_password:"",
            confirm_password:""
        })

        const isDisabled = ref<boolean>(false);

        const changePassword = ref<boolean>(false);

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

        async function handleChangePassword(){
            try {
                isDisabled.value = true;
                await authStore.ChangePassword(passwordForm.value)
                emit('update')
            } catch (error) {
              console.error(error);
            }
            finally{
              isDisabled.value = false;
            }
        }

        onMounted(() => {
            authStore.fetchUserProfile();
        });

        return {
            authStore,
            changePassword,
            handleChangePassword,
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

.attention-paragraph{
    border-radius: 4px;
    padding: 0.8rem;
    background: #f8dada;
    color: #fd2727;
}
</style>
