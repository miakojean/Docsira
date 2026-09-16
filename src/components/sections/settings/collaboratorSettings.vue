<template>
    <div class="main-section gap-2 ">
        <headerNav title="Mes collaborateurs"/>
        <div class="h-full w-full flex justify-center items-center">
            <emptyCards />
        </div>
    </div>
</template>

<script setup lang="ts">
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
</script>

<style scoped >

</style>
