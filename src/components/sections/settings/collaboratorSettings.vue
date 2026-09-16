<template>
    <div class="main-section gap-2 ">
        <headerNav title="Mes collaborateurs"/>
        <div class="h-full w-full flex justify-center items-center">
            <emptyCards @add="handleAdd"/>
        </div>

        <inviteModale :isOpen="isOpen" @close="()=> {isOpen = false}"/>
    </div>
</template>

<script setup lang="ts">
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
import inviteModale from '../../modale/inviteModale.vue';
import { ref } from 'vue';

const isOpen = ref<boolean>(false);

function handleAdd() {
    isOpen.value = true;
}
</script>

<style scoped >

</style>
