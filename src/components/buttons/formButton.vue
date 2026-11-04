<template>
    <button
        class="main-button"
        :class="{ disabled }"
        :disabled="disabled || isLoading"
        type="button"
        @click="$emit('click')"
    >
        <span v-if="!isLoading">{{ label }}</span>
        <LogoLoader v-else size="sm" :inline="true" />
    </button>
</template>

<script>
import LogoLoader from '../tools/LogoLoader.vue';

export default {
    components: {
        LogoLoader
    },
    emits: ['click'],
    props: {
        isLoading: { type: Boolean, default: false },
        label: { type: String, default: 'Commencer' },
        disabled: { type: Boolean, default: true }
    }
}
</script>

<style scoped>
.main-button {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.8rem;
    width: 100%;
    max-width: 200px;
    border-radius: 0.5rem;
    border: none;
    background: var(--primary-color);
    color: #fff;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: 0.2s ease-in-out;
}

.main-button:not(.disabled):hover {
    background: var(--primary-color-dark);
    transform: translateY(-2px);
}

.disabled {
    background: #9fc9de;
    cursor: not-allowed;
}
</style>
