<template>
    <button class="main-button">
        <span v-if="!isLoading">
            {{ label }}
        </span>
        <span class="loading loading-spinner loading-md" v-else></span>
    </button>
</template>

<script>
export default {

    props:{
        isLoading:{
            type:Boolean,
            default: false
        },
        label: {
            type: String,
            default:'Commencer'
        }
    }

}
</script>

<style scoped>

.main-button{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background-color: var(--primary-color-ligth);
    border-radius: 4px;
    padding: 0.6rem 1.25rem;
    font-size: 0.95rem;
    font-weight: 400;
    color: #fff;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    width: 100%;
    max-width: 200px;
}

.main-button:hover{
    background: var(--primary-color-dark);
    color: #fff;
    transition: 0.3s ease-in;
    border: none;
}

</style>
