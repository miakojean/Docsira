<template>
    <nav class="w-full flex justify-between items-center">
        <div class="header__nav">
            <h3>{{title}}</h3>
        </div>
        <BaseInput/>
    </nav>
</template>

<script>
import BaseInput from '../BaseInput/BaseInput.vue';
export default {

    name: "headerNav",
    props:{
        title: {
          type: String,
          default: "Mes collaborateurs"
        }
    },
    components:{
        BaseInput
    },
    setup() {

    }

}

</script>

<style scoped>

</style>
