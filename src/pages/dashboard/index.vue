<template>
  <div class="main-layout">
    <!-- Sidebar -->
    <sidebar />

    <!-- Contenu principal -->
    <main class="main-content">
      <dashboarSection class="dashboard-section" />
    </main>
  </div>
</template>

<script>
import navbar from '../../components/navbar/navbar.vue'
import dashboarSection from '../../components/sections/dashboard-section/dashboardSection.vue'
import sidebar from '../../components/navbar/sidebar.vue'
import footerSection from '../../components/layout/footerSection.vue';
import isConnected from '../../components/tools/isConnected.vue'

export default {
  components: {
    dashboarSection,
    sidebar,
    footerSection,
    isConnected
  }
}
</script>

<style scoped>
/* === LAYOUT PRINCIPAL === */
.main-layout {
  display: flex;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: #f9fafb;
}

/* === SIDEBAR === */
/* La sidebar est supposée avoir une largeur fixe (ex: 250px) et une hauteur 100% */
/* Si elle est responsive, on gère avec des classes supplémentaires */

/* === CONTENU PRINCIPAL === */
.main-content {
  flex: 1;
  width: 100%;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  overflow-x: hidden;
  background: #e9ebee;
}

/* La section du dashboard prend tout l'espace vertical restant */
.dashboard-section {
  flex: 1;
}

/* Option : si tu veux un comportement différent sur grand écran */
@media (min-width: 1024px) {
  .main-layout {
    flex-direction: row;
  }
}
</style>
