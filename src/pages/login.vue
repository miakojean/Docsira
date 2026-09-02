<template>
    <main class="container">
        <loginForm />
    </main>
</template>

<script setup lang="ts">
import loginForm from '../components/forms/loginForm.vue';

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

    .open-account {
        font-size: 1rem;
        font-weight: 500;
        color: #0c88ee;
        text-decoration: underline;
        cursor: pointer;
    }

</style>
