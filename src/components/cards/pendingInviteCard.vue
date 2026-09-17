<template>
    <div class="empty-card-container">

        <!-- 1. En-tête (Header) aligné à gauche avec bordure inférieure -->
        <div class="header-section">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="header-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
            </svg>
            <h3 class="header-title">Mes collaborateurs</h3>
        </div>

        <!-- 2. Corps (Body) central avec l'illustration et les textes -->
        <div class="body-section">
            <div class="illustration-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="success-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
            </div>

            <!-- Hiérarchie des textes -->
            <div class="text-content">
                <p class="main-text">Invitation envoyée</p>
                <p class="sub-text">En cours de validation par l'utilisateur.</p>
            </div>
        </div>

        <!-- 3. Pied de page (Footer) avec le bouton "Outlined" -->
        <div class="footer-section">
            <!-- On émet un événement 'resend' pour renvoyer une invitation -->
            <button class="outline-btn" @click="$emit('resend')">
                <span class="btn-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 1rem; height: 1rem;">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
                    </svg>
                </span>
                Renvoyer une invitation
            </button>
        </div>

    </div>
</template>

<script setup lang="ts">
const emit = defineEmits(['resend']);
</script>

<style scoped>
/* --- Conteneur principal (La Carte Blanche) --- */
.empty-card-container {
    background-color: #ffffff;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    width: 100%;
    max-width: 420px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
}

/* --- En-tête (Header) --- */
.header-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #f3f4f6;
    margin-bottom: 2rem;
}

.header-icon {
    width: 20px;
    height: 20px;
    color: #111827;
}

.header-title {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #111827;
}

/* --- Corps (Body) --- */
.body-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
    margin-bottom: 2rem;
}

/* Effet de cercle gris clair derrière l'image */
.illustration-wrapper {
    width: 120px;
    height: 120px;
    background-color: #f0fdf4; /* Vert très clair */
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
}

.success-icon {
    width: 60%;
    height: 60%;
    color: #22c55e; /* Vert succès */
}

.text-content {
    text-align: center;
}

.main-text {
    color: #374151; /* Gris sombre */
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0 0 0.35rem 0;
}

.sub-text {
    color: #6b7280; /* Gris */
    font-size: 0.95rem;
    margin: 0;
}

/* --- Pied de page (Footer) --- */
.footer-section {
    display: flex;
    justify-content: center;
    width: 100%;
}

/* Bouton façon "Outlined" (Bordure) */
.outline-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background-color: transparent;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 0.6rem 1.25rem;
    font-size: 0.95rem;
    font-weight: 500;
    color: #374151;
    cursor: pointer;
    transition: all 0.2s ease;
}

.outline-btn:hover {
    background-color: #f9fafb;
    border-color: #9ca3af;
    color: #111827;
}

.btn-icon {
    display: flex;
    align-items: center;
}
</style>
