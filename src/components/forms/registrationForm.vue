<template>
    <form action=""
        class=" form-ui w-full flex flex-col items-center justify-center gap-4"
        @submit.prevent="login"
    >
        <h3 class="">Ouvrir un compte</h3>

        <BaseInput
            label="Entrer email/username"
            placeholder="example@email.com/JohnDoe"
            v-model="credentials.username"
            :errorMessage="errorMessage.usernameError"
        />

        <BaseInput
            v-if="usePassword"
            label="Entrer mot de passe"
            placeholder="Entrer votre mot de passe"
            type="password"
            v-model="credentials.password"
            :errorMessage="errorMessage.passwordError"
        />

        <mainButton type="submit" label="Commencer"/>

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
import BaseInput from '../BaseInput/BaseInput.vue';
import mainButton from '../buttons/mainButton.vue';
import exitButton from '../buttons/exitButton.vue';

import api from '../../services/api';
import { useRouter } from 'vue-router';

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

        const router = useRouter();

        const credentials = ref({
            username: "",
            password: ""
        })

        const errorMessage = ref({
            usernameError:"",
            passwordError:""
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

            if (credentials.value.username === "" && !usePassword.value) {
                errorMessage.value.usernameError = "Entrer le nom d'utilisateur";
                valid = false;
            }

            if (credentials.value.password === "" && usePassword.value) {
                errorMessage.value.passwordError = "Entrer mot de passe";
                valid = false;
            }

              return valid;
        }

        // Actions

        async function login(){

            //if (!isValid()) return;

            const response = await api('http://test.tauri.app/data.json', 'GET');

            emit('handleLogin', credentials.value);

            console.log(response.status);
            console.log(response.statusText);

            return response;
      }

        async function exit() {
          await getCurrentWindow().close();
        }

        return {
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
