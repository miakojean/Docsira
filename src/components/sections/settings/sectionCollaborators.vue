<template>
  <div class="settings-section">
    <!-- Header -->
    <header class="section-header">
      <div class="header-left">
        <h1 class="page-title">Collaborateurs</h1>
      </div>
      
      <!-- Section droite avec Recherche et Bouton -->
      <div class="header-right">
        <!-- Barre de recherche -->
        <div class="search-bar">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input type="text" placeholder="Search" class="search-input" />
        </div>

        <!-- Bouton Ajouter -->
        <button class="add-btn" @click="toggleInviteModal">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="btn-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM4 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 0110.374 21c-2.331 0-4.512-.645-6.374-1.766z" />
          </svg>
          Ajouter un collaborateur
        </button>
      </div>
    </header>

    <!-- Grid -->
    <div class="cards-grid">
      <CollaboratorCard 
        v-for="(collab, index) in collaborators"
        :key="index"
        :name="collab.name" 
        :email="collab.email"
      />
    </div>

    <!-- Modale d'invitation -->
    <inviteModale 
      :isOpen="isInviteModalOpen" 
      :isLoading="authStore.isLoading"
      :backendError="authStore.message.errorMessage"
      @close="toggleInviteModal" 
      @invite="handleInvite" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import CollaboratorCard from '../../cards/CollaboratorCard.vue';
import inviteModale from '../../modale/inviteModale.vue';
import { useAuthStore } from '../../../stores/authStore';

const authStore = useAuthStore();
const isInviteModalOpen = ref(false);

const toggleInviteModal = () => {
  isInviteModalOpen.value = !isInviteModalOpen.value;
};

const handleInvite = async (email: string) => {
  const response = await authStore.addCollaborator(email);
  if (response) {
    toggleInviteModal();
  }
};

const collaborators = ref([
  { name: 'Mark Atkinson', email: 'atkinson@mail.com' },
  { name: 'Esther Howard', email: 'howard@mail.com' },
  { name: 'Anna Warren', email: 'warren@mail.com' },
  { name: 'Jacob Jones', email: 'jones@mail.com' },
  { name: 'Savannah Nguyen', email: 'nguyen@mail.com' },
  { name: 'Marta Jones', email: 'Marta.jones@mail.com' },
]);
</script>

<style scoped>
.settings-section {
  padding: 2rem;
  background-color: #fafbfc;
  min-height: 100vh;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center; /* Modifié pour centrer verticalement avec la barre de recherche */
  margin-bottom: 2rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem; /* Espace entre la recherche et le bouton */
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin: 0; /* Suppression du margin-bottom pour l'alignement */
}

/* --- Barre de recherche --- */
.search-bar {
  position: relative;
}

.search-input {
  background-color: #ffffff; /* Ajusté en blanc pour ressortir sur le fond gris */
  border: 1px solid #e5e7eb; /* Légère bordure */
  border-radius: 9999px;
  padding: 0.6rem 1rem 0.6rem 2.5rem;
  font-size: 0.875rem;
  outline: none;
  width: 250px;
  color: #374151;
  transition: border-color 0.2s ease;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-input:focus {
  border-color: #3b82f6;
}

.search-icon {
  position: absolute;
  left: 0.875rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.1rem;
  height: 1.1rem;
  color: #9ca3af;
}

/* --- Bouton Ajouter --- */
.add-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: var(--primary-color-dark); /* Bleu inspiré de votre maquette */
  color: #ffffff;
  border: none;
  border-radius: 20px; /* Bords arrondis */
  padding: 0.6rem 1.2rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(67, 132, 234, 0.2);
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.add-btn:hover {
  background-color: #3168c4;
}

.add-btn:active {
  transform: scale(0.98);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

/* --- Grid --- */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}
</style>