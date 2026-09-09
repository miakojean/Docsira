<template>
    <footer>
        <p>DocSira by Adn consulting</p>

        <div class="view-switcher" role="group" aria-label="Mode d'affichage">
            <button
                type="button"
                class="view-button"
                :class="{ active: view === 'list' }"
                :aria-pressed="view === 'list'"
                title="Afficher en liste"
                @click="emit('update:view', 'list')"
            >
                <span aria-hidden="true">☷</span>
                <span>Liste</span>
            </button>
            <button
                type="button"
                class="view-button"
                :class="{ active: view === 'grid' }"
                :aria-pressed="view === 'grid'"
                title="Afficher en grille"
                @click="emit('update:view', 'grid')"
            >
                <span aria-hidden="true">▦</span>
                <span>Grille</span>
            </button>
        </div>
    </footer>
</template>

<script setup lang="ts">
defineProps<{ view: 'list' | 'grid' }>();

const emit = defineEmits<{
    'update:view': [view: 'list' | 'grid'];
}>();
</script>

<style scoped>
footer{
    padding: 0.75rem 1rem;
    background: #f9fafb;
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    border-top: 1px solid #e5e7eb;
}

footer p{
    font-size: 0.8rem;
    color: #64748b;
}

.view-switcher {
    display: flex;
    gap: 0.25rem;
    padding: 0.2rem;
    border: 1px solid #dbe3ea;
    border-radius: 0.5rem;
    background: #ffffff;
}

.view-button {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.6rem;
    border: 0;
    border-radius: 0.35rem;
    background: transparent;
    color: #64748b;
    cursor: pointer;
    font: inherit;
    font-size: 0.8rem;
}

.view-button.active {
    background: #e0f2fe;
    color: #005792;
}
</style>
