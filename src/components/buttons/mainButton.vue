<template>
  <button class="main-button">
    <span>
        commencer
    </span>
  </button>
</template>

<script>
export default {

}
</script>

<style scoped>

.main-button{
  padding: 0.8rem;
  width: 100%;
  max-width: 200px;
  border-radius: 0.5rem;
  border: none;
  background: #3a8dd1;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  transition: 0.2s ease-in-out;
}

.main-button:hover{
    background: #0c88ee;
    color: #fff;
    transition: 0.1s ease-in;
    border: none;
}

</style>