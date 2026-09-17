<template>
  <div class="collaborator-card pending-card">
    <!-- Options or status indicator -->
    <div class="status-badge">
      <span class="status-dot"></span>
      En attente
    </div>

    <!-- Avatar (Placeholder for pending) -->
    <div class="avatar-container">
      <div class="avatar-placeholder">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="avatar-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
        </svg>
      </div>
    </div>

    <!-- Info -->
    <div class="info-container">
      <h3 class="name">{{ email }}</h3>
      <p class="role">Invitation envoyée</p>
    </div>

    <!-- Divider -->
    <div class="divider"></div>

    <button class="resend-btn" @click="$emit('resend', email)">
        Renvoyer l'invitation
    </button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  email: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['resend']);
</script>

<style scoped>
/* Reset box-sizing */
.collaborator-card *,
.collaborator-card *::before,
.collaborator-card *::after {
  box-sizing: border-box;
  font-family: inherit;
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
  border: 1px dashed #d1d5db; /* Dashed border for pending */
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.collaborator-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
}

.status-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #f59e0b; /* Orange/amber for pending */
  background: #fffbeb;
  padding: 4px 8px;
  border-radius: 12px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #f59e0b;
}

/* Avatar */
.avatar-container {
  margin-top: 8px;
  margin-bottom: 16px;
}

.avatar-placeholder {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.avatar-icon {
  width: 28px;
  height: 28px;
}

/* Informations */
.info-container {
  text-align: center;
  margin-bottom: 16px;
}

.name {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0;
  word-break: break-all;
}

.role {
  font-size: 12px;
  color: #9ca3af;
  margin: 4px 0 0 0;
}

/* Ligne de séparation */
.divider {
  width: 100%;
  height: 1px;
  background-color: #f3f4f6;
  margin-bottom: 16px;
}

/* Bouton Renvoyer */
.resend-btn {
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #4b5563;
  font-size: 12px;
  font-weight: 500;
  padding: 6px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.resend-btn:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
  color: #111827;
}
</style>
