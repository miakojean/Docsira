<template>
  <div class="main-layout">
    <!-- Sidebar -->
    <sidebar />

    <!-- Contenu principal -->
    <main class="main-content">
        <navbar/>
        <mySpaceSection class="dashboard-section" />
    </main>
  </div>
</template>

<script>
import navbar from '../../components/navbar/navbar.vue'
import sidebar from '../../components/navbar/sidebar.vue'
import mySpaceSection from '../../components/sections/dashboard-section/mySpaceSection.vue'

export default {
    components: {
        mySpaceSection,
        sidebar,
        navbar,
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

/* La section du dashboard prend tout l'espace vertical disponible */
.dashboard-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap:1rem;
}

@media (min-width: 1024px) {
  .main-layout {
    flex-direction: row;
  }
}
</style>
