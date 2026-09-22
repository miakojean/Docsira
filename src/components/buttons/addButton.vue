<template>
    <button class="add-btn" @click="">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 0 1 3 3m3 0a6 6 0 0 1-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1 1 21.75 8.25Z" />
        </svg>
        {{label}}
    </button>
</template>

<script lang="ts">
export default {
    props: {
        label:{
            type:String,
            default: "changer mot de passe"
        }
  }
}
</script>

<style scoped>
/* --- Bouton Ajouter --- */
.add-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #ffffff; /* Bleu inspiré de votre maquette */
  color: var(--primary-color-dark);
  border: none;
  border-radius: 4px; /* Bords arrondis */
  padding: 0.8rem 1.2rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(67, 132, 234, 0.2);
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.add-btn:hover {
  background-color: #d1dcef;
  transition: 0.2s ease-in-out;
  transform: translateY(-2px);
}

.add-btn:active {
  transform: scale(0.98);
}

.btn-icon {
  width: 18px;
  height: 18px;
}
</style>
