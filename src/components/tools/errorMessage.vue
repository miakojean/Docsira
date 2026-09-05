<template>
    <div class="main-error" >
        <span v-if="!isLoading">
            {{ label }}
        </span>
        <span class="loading loading-spinner loading-md" v-else></span>
    </div>
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
            default:'Sortir'
        }
    }
}
</script>

<style scoped>

.main-error{
    padding: 0.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    max-width: 350px;
    border-radius: 0.5rem;
    border: none;
    background: #f70776;
    color: #fff;
    font-size: 1rem;
    cursor: pointer;
    transition: 0.2s ease-in-out;
}

.main-error:hover{
    background: #c3195d;
    color: #fff;
    transition: 0.1s ease-in;
    border: none;
}

</style>
