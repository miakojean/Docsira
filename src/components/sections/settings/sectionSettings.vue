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
                    disabled
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
                <p>Pensez à changer votre mot de passe si vous aviez été invité !</p>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                     stroke-width="1.5" stroke="currentColor" class="size-6">
                    <path stroke-linecap="round" stroke-linejoin="round"
                          d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                </svg>
            </div>

            <div class="form-header w-full">
                <h4>Paramètres de sécurité</h4>
            </div>

            <div class="form-body w-full grid grid-cols-3 gap-4" v-if="changePassword">
                <BaseInput
                    label="Mot de passe actuel"
                    placeholder="Entrez votre mot de passe actuel"
                    type="password"
                    autocomplete="current-password"
                    v-model="passwordForm.old_password"
                    :errorMessage="errors.old_password"
                />

                <BaseInput
                    label="Nouveau mot de passe"
                    placeholder="Entrez le nouveau mot de passe"
                    type="password"
                    autocomplete="new-password"
                    v-model="passwordForm.new_password"
                    :errorMessage="errors.new_password"
                />

                <BaseInput
                    label="Confirmer le nouveau mot de passe"
                    placeholder="Confirmez le nouveau mot de passe"
                    type="password"
                    autocomplete="new-password"
                    v-model="passwordForm.confirm_password"
                    :errorMessage="errors.confirm_password"
                />
            </div>

            <!-- Feedback messages -->
            <p v-if="errorMessage" class="feedback error">{{ errorMessage }}</p>
            <p v-if="successMessage" class="feedback success">{{ successMessage }}</p>

            <div class="form-footer w-full flex justify-end gap-4">
                <addButton
                    :disabled="isDisabled"
                    label="Changer mot de passe"
                    type="button"
                    @click="togglePasswordForm"
                    v-if="!changePassword"
                />

                <template v-else>
                    <button
                        type="button"
                        class="btn-cancel"
                        :disabled="isDisabled"
                        @click="togglePasswordForm"
                    >
                        Annuler
                    </button>

                    <formButton
                        :disabled="isDisabled"
                        label="Enregistrer"
                        type="submit"
                    />
                </template>
            </div>
        </form>

    </section>
</template>

<script lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useAuthStore } from '../../../stores/authStore';

import BaseInput from '../../BaseInput/BaseInput.vue';
import formButton from '../../buttons/formButton.vue';
import addButton from '../../buttons/addButton.vue';

export default {
    components: { BaseInput, formButton, addButton },
    emits: ['update'],

    setup(_props, { emit }) {
        const authStore = useAuthStore();

        const user = computed({
            get: () => authStore.user,
            set: (value) => { authStore.user = value; },
        });

        const passwordForm = reactive({
            old_password: '',
            new_password: '',
            confirm_password: '',
        });

        const errors = reactive({
            old_password: '',
            new_password: '',
            confirm_password: '',
        });

        const isDisabled = ref(false);
        const changePassword = ref(false);
        const errorMessage = ref('');
        const successMessage = ref('');

        /* ---------- Profile ---------- */
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

        /* ---------- Password helpers ---------- */
        function resetPasswordForm() {
            passwordForm.old_password = '';
            passwordForm.new_password = '';
            passwordForm.confirm_password = '';
            errors.old_password = '';
            errors.new_password = '';
            errors.confirm_password = '';
            errorMessage.value = '';
            successMessage.value = '';
        }

        function togglePasswordForm() {
            changePassword.value = !changePassword.value;
            resetPasswordForm();
        }

        /**
         * Validates the password form.
         * @returns true if valid, false otherwise.
         */
        function validatePasswordForm(): boolean {
            // Reset field errors
            errors.old_password = '';
            errors.new_password = '';
            errors.confirm_password = '';
            errorMessage.value = '';

            let isValid = true;

            if (!passwordForm.old_password) {
                errors.old_password = 'Le mot de passe actuel est requis.';
                isValid = false;
            }

            if (!passwordForm.new_password) {
                errors.new_password = 'Le nouveau mot de passe est requis.';
                isValid = false;
            } else if (passwordForm.new_password.length < 8) {
                errors.new_password = 'Le mot de passe doit contenir au moins 8 caractères.';
                isValid = false;
            } else if (passwordForm.new_password === passwordForm.old_password) {
                errors.new_password = "Le nouveau mot de passe doit être différent de l'ancien.";
                isValid = false;
            }

            if (!passwordForm.confirm_password) {
                errors.confirm_password = 'Veuillez confirmer le nouveau mot de passe.';
                isValid = false;
            } else if (passwordForm.new_password !== passwordForm.confirm_password) {
                errors.confirm_password = 'Les mots de passe ne correspondent pas.';
                isValid = false;
            }

            return isValid;
        }

        /* ---------- Password submit ---------- */
        async function handleChangePassword() {
            successMessage.value = '';
            errorMessage.value = '';

            if (!validatePasswordForm()) {
                return;
            }

            try {
                isDisabled.value = true;
                const passwordChanged = await authStore.ChangePassword({
                    old_password: passwordForm.old_password,
                    new_password: passwordForm.new_password,
                    confirm_password: passwordForm.confirm_password,
                });

                if (!passwordChanged) {
                    errorMessage.value = authStore.message.errorMessage;
                    return;
                }

                successMessage.value = 'Mot de passe modifié avec succès.';
                resetPasswordForm();
                changePassword.value = false; // close the form
                emit('update');
            } catch (error: any) {
                console.error(error);
                errorMessage.value =
                    error?.response?.data?.message ||
                    'Une erreur est survenue lors du changement de mot de passe.';
            } finally {
                isDisabled.value = false;
            }
        }

        onMounted(() => {
            authStore.fetchUserProfile();
        });

        return {
            authStore,
            changePassword,
            passwordForm,
            errors,
            errorMessage,
            successMessage,
            handleChangePassword,
            togglePasswordForm,
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

.feedback {
    width: 100%;
    padding: 0.6rem 0.9rem;
    border-radius: 4px;
    font-size: 0.9rem;
}
.feedback.error {
    background: #f8dada;
    color: #fd2727;
}
.feedback.success {
    background: #daf8e0;
    color: #1a9e3f;
}

.btn-cancel {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    border: 1px solid #ccc;
    background: #fff;
    cursor: pointer;
}
.btn-cancel:hover:not(:disabled) {
    background: #f5f5f5;
}
.btn-cancel:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}
</style>
