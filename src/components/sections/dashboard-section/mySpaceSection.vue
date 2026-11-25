<template>
  <div class="main-section gap-2">
    <headerNav
      title="Mon espace"
      :showToolsButton="true"
      placeholder="Rechercher un dossier..."
      @handleEvent="openCreateModal"
      v-model="searchQuery"
    >
      <template #actions>
        <button
          type="button"
          class="open-disk-btn"
          :disabled="store.isMutating"
          @click="handlePickFolder"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="btn-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 0 0-1.883 2.542l.857 6a2.25 2.25 0 0 0 2.227 1.932H19.05a2.25 2.25 0 0 0 2.227-1.932l.857-6a2.25 2.25 0 0 0-1.883-2.542m-16.5 0V6A2.25 2.25 0 0 1 6 3.75h3.879a1.5 1.5 0 0 1 1.06.44l2.122 2.12a1.5 1.5 0 0 0 1.06.44H18A2.25 2.25 0 0 1 20.25 9v.776" />
          </svg>
          <span>Ouvrir un dossier</span>
        </button>
      </template>
    </headerNav>

    <div v-if="store.errorMessage" class="error-banner">
      <span>{{ store.errorMessage }}</span>
      <button type="button" class="error-close" @click="store.clearError">×</button>
    </div>

    <div v-if="store.pinnedFolders.length > 0" class="content-container">
      <div class="workspace-view-container flex-1 flex flex-col gap-3">
        <div v-if="filteredFolders.length > 0" class="flex-1 flex flex-col justify-between gap-4">
          <div class="dossiers-grid">
            <div
              v-for="(folderPath, idx) in paginatedFolders"
              :key="folderPath"
              class="folder-card"
              :class="{ 'folder-card--active': activeMenuIndex === idx }"
              :title="folderPath"
              @click="openFolder(folderPath)"
            >
              <!-- Bouton 3 points -->
              <button
                type="button"
                class="card__menu-trigger"
                aria-label="Actions du dossier"
                @click.stop="toggleMenu(idx, folderPath, $event)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="menu-dots-svg">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
                </svg>
              </button>

              <!-- Visuel dossier identique au Workspace -->
              <div class="folder-visual">
                <div class="folder-back"></div>
                <div class="folder-front">
                  <svg class="folder-front__svg" viewBox="0 0 210 125" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="localFolderFrontGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#ecbd04" />
                        <stop offset="100%" stop-color="#bf9903" />
                      </linearGradient>
                    </defs>
                    <path
                      d="M 0,18 A 16,16 0 0,1 16,2 L 76,2 C 94,2 100,20 118,20 L 194,20 A 16,16 0 0,1 210,36 L 210,109 A 16,16 0 0,1 194,125 L 16,125 A 16,16 0 0,1 0,109 Z"
                      fill="url(#localFolderFrontGrad)"
                      stroke="rgba(255, 255, 255, 0.16)"
                      stroke-width="1.5"
                    />
                  </svg>
                </div>
              </div>

              <!-- Infos sous le dossier -->
              <div class="folder-info">
                <p class="folder-title">{{ extractBaseName(folderPath) }}</p>
                <span class="folder-sub" :title="folderPath">{{ extractParentDisplay(folderPath) }}</span>
              </div>
            </div>
          </div>

          <Pagination
            v-model="currentPage"
            :totalItems="filteredFolders.length"
            :pageSize="pageSize"
            :hideOnSinglePage="true"
          />
        </div>

        <div v-else class="flex-1 w-full flex justify-center items-center">
          <emptyCards
            title="Mon espace"
            mainText="Aucun dossier ne correspond à votre recherche."
            subtitle="Vérifiez l'orthographe ou ouvrez un autre dossier."
            :showAddButton="false"
          />
        </div>
      </div>
    </div>

    <div v-else-if="!store.isPinnedLoaded" class="h-full w-full flex justify-center items-center">
      <LogoLoader size="lg" label="Chargement de Mon espace..." />
    </div>

    <div v-else class="h-full w-full flex justify-center items-center">
      <emptyCards
        title="Mon espace"
        mainText="Aucun dossier dans votre espace local."
        subtitle="Créez un dossier ou ouvrez un répertoire depuis votre ordinateur."
        btnLabel="Nouveau dossier"
        @add="openCreateModal"
      />
    </div>

    <!-- Modale création dossier -->
    <renameDocModale
      :isOpen="isCreateModalOpen"
      title="Nouveau dossier"
      label="Nom du dossier"
      placeholder="Ex : Modèles de contrats"
      :isLoading="store.isMutating"
      :errorMessage="store.errorMessage"
      @close="closeCreateModal"
      @rename="confirmCreateFolder"
    />

    <!-- Modale envoi vers Workspace -->
    <sendToWorkspaceModale
      v-if="authStore.canEdit"
      :isOpen="isSendModalOpen"
      :sourceName="sendSourceName"
      :sourcePath="sendSourcePath"
      :isDirectory="true"
      @close="isSendModalOpen = false"
    />

    <!-- Menu contextuel adaptatif téléporté -->
    <Teleport to="body">
      <div
        v-if="activeMenuFolderPath"
        ref="menuRef"
        class="dropbox"
        :style="menuStyle"
        @click.stop
      >
        <ul>
          <li @click="runMenuAction('open', activeMenuFolderPath)">Ouvrir</li>
          <li @click="runMenuAction('system', activeMenuFolderPath)">Ouvrir dans l'explorateur</li>
          <li v-if="authStore.canEdit" @click="runMenuAction('send', activeMenuFolderPath)">Envoyer vers le Workspace</li>
          <li class="danger" @click="runMenuAction('unpin', activeMenuFolderPath)">Retirer de Mon espace</li>
        </ul>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import headerNav from '../../navbar/headerNav.vue';
import emptyCards from '../../cards/emptyCards.vue';
import renameDocModale from '../../modale/renameDocModale.vue';
import sendToWorkspaceModale from '../../modale/sendToWorkspaceModale.vue';
import LogoLoader from '../../tools/LogoLoader.vue';
import Pagination from '../../tools/Pagination.vue';
import {
  extractBaseName,
  extractParentPath,
  useLocalManagerStore,
} from '../../../stores/localManagerStore';
import { useAuthStore } from '../../../stores/authStore';

const router = useRouter();
const store = useLocalManagerStore();
const authStore = useAuthStore();

const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = 12;
const isCreateModalOpen = ref(false);
const activeMenuIndex = ref<number | null>(null);
const activeMenuFolderPath = ref<string | null>(null);
const menuRef = ref<HTMLDivElement | null>(null);
const menuStyle = ref<Record<string, string>>({});

const isSendModalOpen = ref(false);
const sendSourcePath = ref('');
const sendSourceName = ref('');

const filteredFolders = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return store.pinnedFolders;
  return store.pinnedFolders.filter((folderPath) => {
    const name = extractBaseName(folderPath).toLowerCase();
    return name.includes(q) || folderPath.toLowerCase().includes(q);
  });
});

watch(searchQuery, () => {
  currentPage.value = 1;
});

watch(currentPage, () => {
  closeMenu();
});

const paginatedFolders = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return filteredFolders.value.slice(start, start + pageSize);
});

function extractParentDisplay(fullPath: string): string {
  return extractParentPath(fullPath) || fullPath;
}

function closeMenu() {
  activeMenuIndex.value = null;
  activeMenuFolderPath.value = null;
}

function openFolder(folderPath: string) {
  closeMenu();
  store.currentRootPath = folderPath;
  router.push(`/dashboard/mySpace/${encodeURIComponent(folderPath)}`);
}

async function handlePickFolder() {
  const added = await store.pickAndPinFolder();
  if (added) {
    openFolder(added);
  }
}

async function toggleMenu(idx: number, folderPath: string, event: MouseEvent) {
  if (activeMenuIndex.value === idx) {
    closeMenu();
    return;
  }

  const anchor = event.currentTarget as HTMLElement | null;
  const rect = anchor?.getBoundingClientRect();
  activeMenuIndex.value = idx;
  activeMenuFolderPath.value = folderPath;

  if (!rect) return;
  await nextTick();

  const menuRect = menuRef.value?.getBoundingClientRect();
  const menuWidth = menuRect?.width || 210;
  const menuHeight = menuRect?.height || 170;
  const pad = 12;

  let left = rect.right + 8;
  if (left + menuWidth > window.innerWidth - pad) {
    left = rect.left - menuWidth - 8;
  }
  if (left < pad) {
    left = rect.right - menuWidth;
  }
  left = Math.max(pad, Math.min(left, window.innerWidth - menuWidth - pad));

  let top = rect.top;
  if (top + menuHeight > window.innerHeight - pad) {
    top = rect.bottom - menuHeight;
  }
  top = Math.max(pad, Math.min(top, window.innerHeight - menuHeight - pad));

  menuStyle.value = {
    top: `${Math.round(top)}px`,
    left: `${Math.round(left)}px`,
  };
}

function runMenuAction(action: 'open' | 'system' | 'send' | 'unpin', folderPath: string) {
  closeMenu();
  if (action === 'open') {
    openFolder(folderPath);
    return;
  }
  if (action === 'system') {
    void store.openWithSystem(folderPath);
    return;
  }
  if (action === 'send') {
    if (!authStore.canEdit) return;
    sendSourcePath.value = folderPath;
    sendSourceName.value = extractBaseName(folderPath);
    isSendModalOpen.value = true;
    return;
  }
  if (action === 'unpin') {
    void store.unpinFolder(folderPath);
  }
}

function openCreateModal() {
  store.clearError();
  isCreateModalOpen.value = true;
}

function closeCreateModal() {
  isCreateModalOpen.value = false;
  store.clearError();
}

async function confirmCreateFolder(name: string) {
  const createdPath = await store.createRootFolder(name);
  if (createdPath) {
    isCreateModalOpen.value = false;
  }
}

function onWindowClick() {
  if (activeMenuIndex.value !== null) {
    closeMenu();
  }
}

function onWindowKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && activeMenuIndex.value !== null) {
    closeMenu();
  }
}

onMounted(async () => {
  window.addEventListener('click', onWindowClick);
  window.addEventListener('scroll', closeMenu, true);
  window.addEventListener('resize', closeMenu);
  window.addEventListener('keydown', onWindowKeydown);
  await store.loadPinnedFolders();
});

onUnmounted(() => {
  window.removeEventListener('click', onWindowClick);
  window.removeEventListener('scroll', closeMenu, true);
  window.removeEventListener('resize', closeMenu);
  window.removeEventListener('keydown', onWindowKeydown);
});
</script>

<style scoped>
.main-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.open-disk-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.5rem 0.9rem;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #374151;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.open-disk-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
  color: #111827;
}

.open-disk-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-icon {
  width: 17px;
  height: 17px;
}

.error-banner {
  margin: 0.5rem 0.5rem 0;
  padding: 0.7rem 1rem;
  border-radius: 10px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  font-size: 0.86rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.error-close {
  background: none;
  border: none;
  color: #dc2626;
  font-size: 1.2rem;
  cursor: pointer;
  line-height: 1;
}

.content-container {
  padding: 0.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.workspace-view-container {
  width: 100%;
}

.dossiers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1.25rem 0.75rem;
  width: 100%;
  padding-bottom: 2rem;
}

.folder-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
  cursor: pointer;
  width: fit-content;
  margin: 0 auto;
  padding: 0.75rem 0.75rem 0.65rem;
  border-radius: 12px;
  background: transparent;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.2s ease;
}

.folder-card:hover {
  background-color: #ffffff97;
  transform: translateY(-2px);
}

.folder-card--active {
  z-index: 45;
  background-color: #ffffff97;
}

.folder-visual {
  position: relative;
  width: 135px;
  height: 125px;
  user-select: none;
  transform: scale(0.85);
  transform-origin: top center;
  margin-bottom: -1.36rem;
}

.folder-back {
  position: absolute;
  top: 8px;
  left: 4px;
  right: 8px;
  bottom: 6px;
  background: #bf9903;
  border-radius: 16px;
  z-index: 1;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

.folder-front {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 122px;
  z-index: 3;
  filter: drop-shadow(0 8px 14px rgba(0, 0, 0, 0.16));
}

.folder-front__svg {
  width: 100%;
  height: 100%;
  display: block;
}

.folder-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  width: 135px;
  min-width: 0;
}

.folder-title {
  margin: 0;
  max-width: 100%;
  font-size: 0.85rem;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-sub {
  max-width: 100%;
  color: #6b7280;
  font-size: 0.74rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card__menu-trigger {
  position: absolute;
  top: 0.55rem;
  right: 0.55rem;
  z-index: 6;
  width: 30px;
  height: 30px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  color: #475569;
  padding: 0;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.folder-card:hover .card__menu-trigger,
.folder-card--active .card__menu-trigger {
  opacity: 1;
}

.card__menu-trigger:hover {
  color: #0f172a;
}

.menu-dots-svg {
  width: 18px;
  height: 18px;
}

.dropbox {
  position: fixed;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  border: 1px solid #f3f4f6;
  min-width: 205px;
  z-index: 9999;
  padding: 0.35rem;
}

.dropbox ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.dropbox li {
  padding: 0.55rem 0.75rem;
  font-size: 0.84rem;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.dropbox li:hover {
  background-color: #f3f4f6;
  color: var(--primary-color, #005792);
}

.dropbox li.danger {
  color: #dc2626;
}

.dropbox li.danger:hover {
  background-color: #fef2f2;
}
</style>
