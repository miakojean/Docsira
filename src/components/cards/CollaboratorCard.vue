<template>
  <div class="collaborator-card">
    <!-- More options (3 dots) -->
    <button class="more-btn">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="more-icon">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 110-1.5.75.75 0 010 1.5zM12 12.75a.75.75 0 110-1.5.75.75 0 010 1.5zM12 18.75a.75.75 0 110-1.5.75.75 0 010 1.5z" />
      </svg>
    </button>

    <!-- Avatar -->
    <div class="avatar-container">
      <img 
        :src="avatarUrl || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(name) + '&background=random'" 
        :alt="name" 
        class="avatar-img"
      />
    </div>

    <!-- Info -->
    <div class="info-container">
      <h3 class="name">{{ name }}</h3>
      <p class="role">{{ email }}</p>
    </div>

    <!-- Divider -->
    <div class="divider"></div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  avatarUrl: {
    type: String,
    default: '',
  },
  email: {
    type: String,
    required: true,
  },
});
</script>

<style scoped>
/* Reset box-sizing pour le composant */
.collaborator-card *,
.collaborator-card *::before,
.collaborator-card *::after {
  box-sizing: border-box;
  font-family: inherit; /* Utilise la police globale de votre projet Vue */
}

.collaborator-card {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 100%;
  max-width: 280px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #f9fafb;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.collaborator-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
}

/* Bouton d'options */
.more-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.more-btn:hover {
  color: #4b5563;
}

.more-icon {
  width: 20px;
  height: 20px;
}

/* Avatar */
.avatar-container {
  margin-top: 8px;
  margin-bottom: 16px;
}

.avatar-img {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Informations (Nom, Rôle) */
.info-container {
  text-align: center;
  margin-bottom: 20px;
}

.name {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.role {
  font-size: 13px;
  color: #6b7280;
  margin: 4px 0 0 0;
  font-weight: 500;
}

/* Ligne de séparation */
.divider {
  width: 100%;
  height: 1px;
  background-color: #f3f4f6;
  margin-bottom: 20px;
}

/* Statistiques */
.stats-container {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 0 8px;
}

.stat-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
}

.stat-label {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 500;
  margin-top: 4px;
}
</style>