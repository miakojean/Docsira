<template>
    <nav class="w-full flex justify-between items-center">
        <div class="header__nav">
            <h3>{{title}}</h3>
        </div>
        <div class="tools-frame flex items-center justify-center gap-4">
            <BaseResearchInput />
            <toolsButton @handleEvent="$emit('handleEvent')"/>
        </div>
    </nav>
</template>

<script>
import BaseResearchInput from '../BaseInput/BaseResearchInput.vue';
import toolsButton from '../buttons/toolsButton.vue';
export default {

    name: "headerNav",
    props:{
        title: {
          type: String,
          default: "Mes collaborateurs"
        }
    },
    components:{
        BaseResearchInput,
        toolsButton
    },
    emits:['handleEvent'],
    setup() {

    }

}

</script>

<style scoped>

</style>
