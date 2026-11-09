<template>
    <nav class="w-full flex justify-between items-center">
        <div class="header__nav">
            <h3>{{title}}</h3>
        </div>
        <div class="tools-frame flex items-center justify-center gap-4">
            <BaseResearchInput 
                :modelValue="modelValue" 
                :placeholder="resolvedPlaceholder"
                @update:modelValue="$emit('update:modelValue', $event)" 
            />
            <slot name="actions"></slot>
            <toolsButton v-if="showToolsButton" @handleEvent="$emit('handleEvent')"/>
        </div>
    </nav>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
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
        },
        placeholder: {
          type: String,
          default: ""
        }
    },
    components:{
        BaseResearchInput,
        toolsButton
    },
    emits:['handleEvent', 'update:modelValue'],
    setup(props) {
        const resolvedPlaceholder = computed(() => {
            if (props.placeholder) return props.placeholder;
            if (props.title === 'Workspace') return 'Rechercher un dossier...';
            if (props.title === 'Mes clients') return 'Rechercher un client...';
            if (props.title === 'Mes collaborateurs') return 'Rechercher un collaborateur...';
            if (props.title === 'Corbeille') return 'Rechercher dans la corbeille...';
            return 'Rechercher...';
        });

        return {
            resolvedPlaceholder
        };
    }
});
</script>

<style scoped>

</style>
