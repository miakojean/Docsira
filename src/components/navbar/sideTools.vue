<template>
  <aside class="sidebar" :class="{ 'is-reduced': isReduced }">
    <!-- LOGO -->
    <div class="logo hidden-mobile">
        <!-- Icône affichée lorsque la sidebar est réduite -->

        <!-- Texte affiché lorsque la sidebar est ouverte -->
        <span class="logo-text" v-if="!isReduced">Paramètres</span>

        <!-- Bouton de bascule (toujours visible) -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.343 3.94c.09-.542.56-.94 1.11-.94h1.093c.55 0 1.02.398 1.11.94l.149.894c.07.424.384.764.78.93.398.164.855.142 1.205-.108l.737-.527a1.125 1.125 0 0 1 1.45.12l.773.774c.39.389.44 1.002.12 1.45l-.527.737c-.25.35-.272.806-.107 1.204.165.397.505.71.93.78l.893.15c.543.09.94.559.94 1.109v1.094c0 .55-.397 1.02-.94 1.11l-.894.149c-.424.07-.764.383-.929.78-.165.398-.143.854.107 1.204l.527.738c.32.447.269 1.06-.12 1.45l-.774.773a1.125 1.125 0 0 1-1.449.12l-.738-.527c-.35-.25-.806-.272-1.203-.107-.398.165-.71.505-.781.929l-.149.894c-.09.542-.56.94-1.11.94h-1.094c-.55 0-1.019-.398-1.11-.94l-.148-.894c-.071-.424-.384-.764-.781-.93-.398-.164-.854-.142-1.204.108l-.738.527c-.447.32-1.06.269-1.45-.12l-.773-.774a1.125 1.125 0 0 1-.12-1.45l.527-.737c.25-.35.272-.806.108-1.204-.165-.397-.506-.71-.93-.78l-.894-.15c-.542-.09-.94-.56-.94-1.109v-1.094c0-.55.398-1.02.94-1.11l.894-.149c.424-.07.765-.383.93-.78.165-.398.143-.854-.108-1.204l-.526-.738a1.125 1.125 0 0 1 .12-1.45l.773-.773a1.125 1.125 0 0 1 1.45-.12l.737.527c.35.25.807.272 1.204.107.397-.165.71-.505.78-.929l.15-.894Z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
        </svg>
    </div>

    <!-- NAVIGATION -->
    <nav class="nav-menu">
      <button
        class="nav-item"
        :class="{ active: route.path.includes('/Dashboard/index/ ') }"
        @click="router.push('/Dashboard')"
      >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.343 3.94c.09-.542.56-.94 1.11-.94h1.093c.55 0 1.02.398 1.11.94l.149.894c.07.424.384.764.78.93.398.164.855.142 1.205-.108l.737-.527a1.125 1.125 0 0 1 1.45.12l.773.774c.39.389.44 1.002.12 1.45l-.527.737c-.25.35-.272.806-.107 1.204.165.397.505.71.93.78l.893.15c.543.09.94.559.94 1.109v1.094c0 .55-.397 1.02-.94 1.11l-.894.149c-.424.07-.764.383-.929.78-.165.398-.143.854.107 1.204l.527.738c.32.447.269 1.06-.12 1.45l-.774.773a1.125 1.125 0 0 1-1.449.12l-.738-.527c-.35-.25-.806-.272-1.203-.107-.398.165-.71.505-.781.929l-.149.894c-.09.542-.56.94-1.11.94h-1.094c-.55 0-1.019-.398-1.11-.94l-.148-.894c-.071-.424-.384-.764-.781-.93-.398-.164-.854-.142-1.204.108l-.738.527c-.447.32-1.06.269-1.45-.12l-.773-.774a1.125 1.125 0 0 1-.12-1.45l.527-.737c.25-.35.272-.806.108-1.204-.165-.397-.506-.71-.93-.78l-.894-.15c-.542-.09-.94-.56-.94-1.109v-1.094c0-.55.398-1.02.94-1.11l.894-.149c.424-.07.765-.383.93-.78.165-.398.143-.854-.108-1.204l-.526-.738a1.125 1.125 0 0 1 .12-1.45l.773-.773a1.125 1.125 0 0 1 1.45-.12l.737.527c.35.25.807.272 1.204.107.397-.165.71-.505.78-.929l.15-.894Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
          </svg>
        <span class="nav-label" v-if="!isReduced">Information générales</span>
      </button>
    </nav>

    <!--
        <div class="logout">
            <button class="nav-item" @click="goToAuth">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15M12 9l-3 3m0 0 3 3m-3-3h12.75" />
                    </svg>
                    <span class="nav-label" v-if="!isReduced">Déconnexion</span>
            </button>
        </div>
    -->
  </aside>
</template>

<script lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';


export default {
  name: 'Sidebar',
  setup() {
    const isReduced = ref(false);
    const router = useRouter();
    const route = useRoute();

    const toggleReduce = async() => {
      isReduced.value = !isReduced.value;
    };

    function goToAuth(){
      router.push('/login');
    }

    return {
      isReduced,
      router,
      route,
      toggleReduce,
      goToAuth
    };
  }
}
</script>

<style scoped>
.sidebar {
  --sb-bg: #f3f6f8;
  --sb-text: #515254;
  --sb-text-active: #ffffff;
  --sb-accent: #5452f4;
  --sb-border: rgba(255, 255, 255, 0.08);
  --sb-hover-bg: #000e2d44;
}

.sidebar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: calc(65px + env(safe-area-inset-bottom));
  background-color: var(--sb-bg);
  border-top: 1px solid var(--sb-border);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 100;
  box-shadow: 0 -4px 20px rgba(15, 23, 42, 0.1);
}

.nav-menu {
  display: flex;
  width: 100%;
  justify-content: flex-start;
  align-items: center;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  gap: 0.5rem;
  padding: 0 1rem;
  scrollbar-width: none;
}
.nav-menu::-webkit-scrollbar {
  display: none;
}

.nav-item {
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
  width: 100px;
  min-height: 50px;
  font-size: 0.5rem;
  font-weight: 600;
  transition: all 0.2s ease;
  text-decoration: none;
}
.icon {
  width: 24px;
  height: 24px;
  margin-bottom: 0.2rem;
  transition: transform 0.2s ease;
}
.nav-item.active {
  color: var(--sb-accent);
}
.nav-item.active .icon {
  transform: translateY(-2px);
}
.nav-item:hover:not(.active) {
  color: var(--sb-text-active);
}

.hidden-mobile {
  display: none;
}
.logout span {
  color: #ef4444;
}
.logout .nav-item {
  color: #ef4444;
}

/* --- DESKTOP --- */
@media (min-width: 1024px) {
  .hidden-mobile {
    display: flex;
  }

  .sidebar {
    position: relative;
    bottom: auto;
    left: auto;
    width: 260px;
    height: 100vh;
    flex-direction: column;
    justify-content: flex-start;
    align-items: stretch;
    padding: 1rem 1rem;
    border-top: none;
    border-right: 1px solid var(--sb-border);
    box-shadow: none;
    gap: 1rem;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .sidebar.is-reduced {
    width: 88px;
    padding: 1.5rem 0.5rem;
  }

  .logo {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0.5rem;
  }

  .logo svg{
    color: var(--primary-color);
  }

  .sidebar.is-reduced .logo {
    justify-content: center;
    padding: 0;
    gap: 0.5rem;
  }
  .logo-text {
    font-weight: 700;
    font-size: 1.25rem;
    color: var(--primary-color);
    letter-spacing: -0.02em;
    margin: 1rem;
  }
  .logo-icon {
    width: 32px;
    height: 32px;
    color: var(--sb-text);
    flex-shrink: 0;
  }
  .toggle-icon {
    width: 28px;
    height: 28px;
    color: var(--primary-color);
    cursor: pointer;
    transition: color 0.2s ease;
  }

  .toggle-icon:hover {
    color: var(--primary-color);
  }

  .nav-menu {
    flex-direction: column;
    width: 100%;
    gap: 0.5rem;
  }

  .nav-item {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    gap: 1rem;
    padding: 0.5rem;
    border-radius: 8px;
    font-size: 0.8rem;
  }
  .nav-item:hover {
    background-color: var(--primary-color);
    color: #ffffff;
  }
  .nav-item.active {
    background-color: var(--primary-color);
    color: #ffffff;
  }
  .nav-item.active .icon {
    transform: none;
  }
  .sidebar.is-reduced .nav-item {
    justify-content: center;
    padding: 0.8rem 0;
  }
  .nav-label {
    white-space: nowrap;
    animation: fadeIn 0.2s ease forwards;
  }

  .logout {
    margin-top: auto;
    width: 100%;
    border-top: 1px solid var(--sb-border);
    padding-top: 1rem;
  }
  .logout .nav-item:hover {
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-5px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
