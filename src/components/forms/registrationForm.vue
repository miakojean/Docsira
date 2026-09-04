<template>
    <form action=""
        class=" form-ui w-full flex flex-col items-center justify-center gap-4"
        @submit.prevent="login"
    >
        <h3 class="">Ouvrir un compte</h3>

        <BaseInput
            label="Entrer nom d'entreprise"
            placeholder="ex:Caladriusllc"
            v-model="credentials.username"
            :errorMessage="errorMessage.usernameError"
        />

        <BaseInput
            label="Entrer email"
            placeholder="example@email.com"
            v-model="credentials.email"
            :errorMessage="errorMessage.emailError"
        />

        <BaseInput
            label="Entrer mot de passe"
            placeholder="Entrer votre mot de passe"
            type="password"
            v-model="credentials.password"
            :errorMessage="errorMessage.passwordError"
        />

        <mainButton type="submit" label="Commencer" :isLoading="authStore.isLoading"/>

        <p>{{succesMessage}}</p>

        <div class="divider-form"></div>

        <p>Déjà un compte? <RouterLink to='/login'>se connecter ici</RouterLink> </p>

        <exitButton label="Sortir" @click="exit" type="button"/>

        <div class="credits-policy flex justify-center items-center">
            <p>
                En utilisant Docsira vous
                acceptez les <span>conditions d'utilisations</span> et
                les <span>politiques de confidentialité</span>
            </p>
        </div>
    </form>
</template>

<script lang="ts">
import { getCurrentWindow } from '@tauri-apps/api/window';

import { ref } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore, type Customer } from '../../stores/authStore';

import BaseInput from '../BaseInput/BaseInput.vue';
import mainButton from '../buttons/mainButton.vue';
import exitButton from '../buttons/exitButton.vue';


export default {
    components: {
        BaseInput,
        mainButton,
        exitButton
    },
    emits:['handleLogin'],
    setup(props, { emit }) {

        // State
        //
        const authStore = useAuthStore();

        const router = useRouter();

        const credentials = ref<Pick<Customer, "username" | "password" | "email">>({
            username: "",
            password: "",
            email: ""
        })

        const errorMessage = ref({
            usernameError:"",
            passwordError:"",
            emailError: "",
        })

        const succesMessage = ref("");

        const usePassword = ref<boolean>(false);

        // Getters
        //
        const setPassword = () => {
            usePassword.value = !usePassword.value
        }

        function isValid() :boolean {
            let valid = true;

            // Réinitialiser les messages d'erreur (optionnel)
            errorMessage.value.usernameError = "";
            errorMessage.value.passwordError = "";
            errorMessage.value.emailError = "";

            if (credentials.value.username.trim() === "") {
                errorMessage.value.usernameError = "Entrer le nom d'utilisateur";
                valid = false;
            }

            if (credentials.value.email.trim() === "") {
                errorMessage.value.emailError = "Entrer une email valide";
                valid = false;
            }

            if (credentials.value.password.trim() === "") {
                errorMessage.value.passwordError = "Entrer mot de passe";
                valid = false;
            }

              return valid;
        }

        // Actions

        async function login(){

            if (!isValid()) return;

            const response = await authStore.Registration(credentials.value);

            router.push('/login')

            return response;
        }

        async function exit() {
            await getCurrentWindow().close();
        }

        return {
            authStore,
            router,
            credentials,
            errorMessage,
            usePassword,
            setPassword,
            succesMessage,
            login,
            exit
        }
    }
}
</script>

<style scoped>
form h3{
    margin-bottom: 2rem;
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

p {
    color: #969292;
}

a{
    color: #222222;
    font-weight: 500;
}

.credits-policy {
    padding: 1rem;
    font-size: 12px;
    color: #969292;
    display: flex;
    justify-content: center;
    align-items: center;
}

.credits-policy p{
    text-align: center;
}

.credits-policy span {
    color: #222222;
    font-weight: 500;
}

.password-frame h4{
    width: 100;
}

.password-frame svg{
    font-size: 12px;
}
</style>
