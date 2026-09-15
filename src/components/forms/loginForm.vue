<template>
    <form class="form-ui" @submit.prevent="login">
        <h3>Se connecter</h3>

        <BaseInput
            label="Entrer email/username"
            placeholder="example@email.com/JohnDoe"
            v-model="credentials.username"
            :errorMessage="errorMessageState.usernameError"
        />

        <BaseInput
            v-if="usePassword"
            label="Entrer mot de passe"
            placeholder="Entrer votre mot de passe"
            type="password"
            v-model="credentials.password"
            :errorMessage="errorMessageState.passwordError"
        />

        <mainButton type="submit" label="Se connecter" :isLoading="authStore.isLoading" />

        <errorMessage :label="authStore.message.errorMessage" v-if="authStore.message.errorMessage" />

        <div class="password-frame w-full flex justify-center items-center gap-2" v-if="!usePassword" @click="setPassword" >
            <h4>Se connecter avec mot de passe</h4>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 0 1 3 3m3 0a6 6 0 0 1-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1 1 21.75 8.25Z" />
            </svg>
        </div>
        <h4 @click="setPassword" v-else>Obtenir un code</h4>

        <p v-if="authStore.message.succesMessage">{{ authStore.message.succesMessage }}</p>

        <div class="divider-form"></div>

        <p>Pas de compte? <RouterLink to='/register'>Créez-en un ici</RouterLink> </p>

        <exitButton label="Sortir" @click="exit" type="button" v-if="!credentials.username && !credentials.password"/>

        <div class="credits-policy flex justify-center items-center">
            <p>
                En utilisant Docsira vous acceptez les <span>conditions d'utilisations</span> et les <span>politiques de confidentialité</span>
            </p>
        </div>
    </form>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getCurrentWindow } from '@tauri-apps/api/window';
import { useAuthStore, type Customer } from '../../stores/authStore';

import BaseInput from '../BaseInput/BaseInput.vue';
import mainButton from '../buttons/mainButton.vue';
import exitButton from '../buttons/exitButton.vue';
import errorMessage from '../tools/errorMessage.vue';

// Déclaration des emits avec setup
const emit = defineEmits(['handleLogin']);

const authStore = useAuthStore();

const credentials = ref<Pick<Customer, "username" | "email" | "password">>({
    username: "",
    password: "",
    email: ""
});

const errorMessageState = ref({
    usernameError: "",
    passwordError: ""
});

const usePassword = ref<boolean>(true);

const setPassword = () => {
    usePassword.value = !usePassword.value;
};

const isValid = (): boolean => {
    let valid = true;
    errorMessageState.value.usernameError = "";
    errorMessageState.value.passwordError = "";

    if (credentials.value.username === "" && !usePassword.value) {
        errorMessageState.value.usernameError = "Entrer le nom d'utilisateur";
        valid = false;
    }

    if (credentials.value.password === "" && usePassword.value) {
        errorMessageState.value.passwordError = "Entrer mot de passe";
        valid = false;
    }

    return valid;
};

const login = async () => {
    if (!isValid()) return;

    const identifier = credentials.value.username.trim();
    await authStore.Login({
        username: identifier.includes('@') ? undefined : identifier,
        email: identifier.includes('@') ? identifier : undefined,
        password: credentials.value.password,
    });

    emit('handleLogin', credentials.value);
};

const exit = async () => {
    await getCurrentWindow().close();
};

onMounted(() => {
    authStore.message.errorMessage = "";
    authStore.message.succesMessage = "";
});
</script>

<style scoped>
/* Ton CSS existant */
form h3{
    margin-bottom: 1rem;
    font-size: 1.5rem;
    font-weight: 500;
}
form h4{
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
}
.divider-form {
    width: 100%;
    height: 1px;
    border: 1px solid #f7f3f3;
    margin: 0 1rem;
}
p { color: #969292; }
a { color: #222222; font-weight: 500; }
.credits-policy { padding: 1rem; font-size: 12px; color: #969292; display: flex; justify-content: center; align-items: center; }
.credits-policy p{ text-align: center; }
.credits-policy span { color: #222222; font-weight: 500; }
.password-frame h4{ width: 100; }
.password-frame svg{ font-size: 12px; }
</style>
