<template>
    <nav class="w-full flex justify-between items-center">
        <div class="header__nav">
            <h3>{{title}}</h3>
        </div>
        <div class="tools-frame flex items-center justify-center gap-4">
            <BaseResearchInput :modelValue="modelValue" @update:modelValue="$emit('update:modelValue', $event)" />
            <toolsButton v-if="showToolsButton" @handleEvent="$emit('handleEvent')"/>
        </div>
    </nav>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import BaseResearchInput from '../BaseInput/BaseResearchInput.vue';
import toolsButton from '../buttons/toolsButton.vue';

export default defineComponent({
    name: "headerNav",
    props:{
        title: {
          type: String,
          default: "Mes collaborateurs"
        },
        showToolsButton: {
          type: Boolean,
          default: true
        },
        modelValue: {
          type: String,
          default: ""
        }
    },
    components:{
        BaseResearchInput,
        toolsButton
    },
    emits:['handleEvent', 'update:modelValue'],
    setup() {
        return {};
    }
});
</script>

<style scoped>

</style>
