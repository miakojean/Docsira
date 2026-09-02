<template>
    <button class="main-button">
        <span v-if="!isLoading">
            commencer
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
  padding: 0.8rem;
  width: 100%;
  max-width: 350px;
  border-radius: 0.5rem;
  border: none;
  background: #222222;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  transition: 0.2s ease-in-out;
}

.main-button:hover{
    background: #0f0e0e;
    color: #fff;
    transition: 0.1s ease-in;
    border: none;
}

</style>
