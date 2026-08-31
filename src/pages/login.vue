<template>
  <main class="container">
    <form action="" class="form-container w-full flex flex-col items-center justify-center gap-2">
        <BaseInput 
        label="Entrer email/username" 
        placeholder="example@email.com/JohnDoe"
        v-model="credentials.username"
        :errorMessage="errorMessage.usernameError"
        />
        <BaseInput 
            label="Mot de passe" 
            type="password" 
            placeholder="mot de passe"
            v-model="credentials.password"
            :errorMessage="errorMessage.passwordError"
        />

        <p>{{ succesMessage }}</p>
        <mainButton @click="login"/>
    </form>
  </main>
</template>

<script setup lang="ts">
import {useRouter} from 'vue-router';
import { reactive, ref } from "vue";
import { invoke } from "@tauri-apps/api/core";

import mainButton from "../components/buttons/mainButton.vue";
import BaseInput from '../components/BaseInput/BaseInput.vue';

const router = useRouter();

const credentials = ref({
    username: "",
    password: ""
})

const errorMessage = ref({
    usernameError:"",
    passwordError:""
})

function isValid(){
    
    let isValid = true;

    if (credentials.value.username ==""){
        errorMessage.value.usernameError="Entrer le nom d'utilisateur"
        isValid = false
        return isValid;
    }

    if (credentials.value.password == ""){
        errorMessage.value.passwordError="Entrer mot de passe"
        isValid = false
        return isValid;
    }

    return isValid;
}

const succesMessage = ref("");

function login(){

    if (!isValid()) return;

    succesMessage.value = "Félcitations vousy êtes parvenus";

    return succesMessage.value;
  
}


</script>

<style scoped>

  h4{
    font-size: 2rem;
    font-weight: 500;
    line-height: 1.5;
    max-width: 500px;
    text-align: center;
  }

  @keyframes gradient {
    0% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
    100% {
      background-position: 0% 50%;
    }
  }

  .animated-gradient {
    background: linear-gradient(45deg, #2e49c3, #1b191d, #020202);
    background-size: 200% 200%;
    animation: gradient 15s ease infinite;
  }

</style>