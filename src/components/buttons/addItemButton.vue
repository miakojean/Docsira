<template>
    <button class="outline-btn" @click="$emit('add')">
        {{btnLabel}}
    </button>
</template>

<script>
export default {
    props:{
        btnLabel:{
            type:String,
            default:"Ouvrir un dossier"
        }
    }
}
</script>

<style scoped>

.outline-btn {
    width: 100%;
    max-width: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background-color: transparent;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 0.6rem 1.25rem;
    font-size: 0.95rem;
    font-weight: 400;
    color: #374151;
    cursor: pointer;
    transition: all 0.2s ease;
}

.outline-btn:hover {
    background-color: #f9fafb;
    color: #111827;
}

.btn-icon {
    font-size: 1.2rem;
    line-height: 1;
}

</style>
