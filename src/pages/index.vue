<template>
  <main class="page-container">
    <h4>
      Bienvenu dans Docsira
    </h4>
    <mainButton @click="start"/>
  </main>
</template>

<script setup lang="ts">
import {useRouter} from 'vue-router';
import mainButton from "../components/buttons/mainButton.vue";
import { ref } from "vue";
import { invoke } from "@tauri-apps/api/core";

const greetMsg = ref("");
const name = ref("");
const result = ref<number>(0);

const router = useRouter();

function start(){
  router.push('/login')
}


</script>

<style scoped>

  h4{
    font-size: 2rem;
    font-weight: 500;
    line-height: 1.5;
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