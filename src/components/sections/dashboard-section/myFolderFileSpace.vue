<template>
  <div class="affair-detail-section">
    <!-- En-tête aligné sur affairDetailSection -->
    <header class="affair-header">
      <div class="header-left">
        <button
          type="button"
          class="back-btn"
          :title="store.parentPath ? 'Dossier parent' : 'Retour à Mon espace'"
          @click="goUp"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
          </svg>
        </button>

        <div class="header-info">
          <div class="header-title-row">
            <h3 class="page-title">{{ currentFolderName }}</h3>
          </div>
          <div class="page-subtitle-row">
            <span class="ref-text" :title="folderPath">{{ folderPath }}</span>
          </div>
        </div>
      </div>

      <div class="header-actions">
        <button
          type="button"
          class="back-btn"
          title="Actualiser"
          :disabled="store.isLoading"
          @click="store.refreshCurrentDirectory"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="header-action-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182" />
          </svg>
        </button>

        <button
          type="button"
          class="new-folder-btn"
          title="Ouvrir dans l'explorateur système"
          @click="store.openWithSystem(folderPath)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="header-action-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
          </svg>
          <span>Ouvrir</span>
        </button>

        <button
          type="button"
          class="new-folder-btn"
          :disabled="store.isMutating"
          title="Créer un nouveau sous-dossier"
          @click="openCreateSubfolder"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="header-action-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v6m3-3H9m4.06-7.19-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
          </svg>
          <span>Nouveau dossier</span>
        </button>

        <button
          type="button"
          class="add-btn"
          :disabled="store.isMutating"
          title="Ajouter des fichiers dans ce dossier"
          @click="store.importFilesToCurrentDir"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="header-action-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>Ajouter des fichiers</span>
        </button>
      </div>
    </header>

    <!-- Barre de navigation des dossiers (Fil d'Ariane + outils) -->
    <div class="folder-nav-bar">
      <div class="breadcrumbs">
        <button
          type="button"
          class="breadcrumb-item"
          @click="goToRootList"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
          </svg>
          <span>Mon espace</span>
        </button>

        <template v-for="(crumb, idx) in store.breadcrumbs" :key="crumb.path">
          <span class="breadcrumb-separator">/</span>
          <button
            type="button"
            class="breadcrumb-item"
            :class="{ active: idx === store.breadcrumbs.length - 1 }"
            :title="crumb.path"
            @click="navigateToFolder(crumb.path)"
          >
            {{ crumb.name }}
          </button>
        </template>
      </div>

      <div class="nav-tools">
        <BaseResearchInput
          v-model="searchQuery"
          placeholder="Filtrer..."
        />

        <div class="sort-wrap">
          <BaseSelectInput
            v-model="store.sortBy"
            :options="SORT_OPTIONS"
            inputId="myspace-folder-sort"
          />
        </div>

        <div class="view-toggle" role="group" aria-label="Mode d'affichage">
          <button
            type="button"
            class="view-btn"
            :class="{ 'is-active': store.viewMode === 'grid' }"
            title="Vue grille"
            aria-label="Vue grille"
            @click="store.setViewMode('grid')"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="view-svg">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z" />
            </svg>
          </button>

          <button
            type="button"
            class="view-btn"
            :class="{ 'is-active': store.viewMode === 'list' }"
            title="Vue liste"
            aria-label="Vue liste"
            @click="store.setViewMode('list')"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="view-svg">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0ZM3.75 12h.007v.008H3.75V12Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm-.375 5.25h.007v.008H3.75v-.008Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Bannière erreur -->
    <div v-if="store.errorMessage" class="error-banner">
      <span>{{ store.errorMessage }}</span>
      <button type="button" class="error-close" @click="store.clearError">×</button>
    </div>

    <!-- Espace de contenu -->
    <div class="files-workspace">
      <div v-if="store.isLoading" class="loading-state">
        <LogoLoader size="lg" />
        <p>Chargement du contenu du dossier...</p>
      </div>

      <div v-else-if="sortedEntries.length === 0" class="empty-state-wrapper">
        <div class="empty-state" @click="store.importFilesToCurrentDir">
          <div class="empty-icon-circle">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.3" stroke="currentColor" class="size-12 empty-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
          </div>
          <h3 class="empty-title">
            {{ searchQuery ? 'Aucun élément correspondant' : 'Ce dossier est vide' }}
          </h3>
          <p class="empty-text">
            {{ searchQuery ? 'Modifiez votre recherche pour afficher d’autres éléments.' : 'Ajoutez des fichiers depuis votre ordinateur ou créez des sous-dossiers.' }}
          </p>

          <div v-if="!searchQuery" class="empty-buttons-row" @click.stop>
            <button
              type="button"
              class="empty-cta-btn"
              :disabled="store.isMutating"
              @click="store.importFilesToCurrentDir"
            >
              <span>Ajouter des fichiers</span>
            </button>
            <button
              type="button"
              class="empty-secondary-btn"
              :disabled="store.isMutating"
              @click="openCreateSubfolder"
            >
              <span>Nouveau sous-dossier</span>
            </button>
          </div>
        </div>
      </div>

      <!-- VUE GRILLE (style affairDetailSection + folderCards / myfileCards) -->
      <div v-else-if="store.viewMode === 'grid'" class="files-content-area">
        <div class="file-list--grid">
          <!-- Sous-dossiers -->
          <div
            v-for="entry in paginatedDirectories"
            :key="entry.path"
            class="folder-card"
            :class="{ 'is-menu-open': activeMenuEntry?.path === entry.path }"
            @click="handleOpenEntry(entry)"
          >
            <div class="card-top-actions" @click.stop>
              <button
                type="button"
                class="kebab-btn"
                title="Options"
                @click="toggleEntryMenu(entry, $event)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
                </svg>
              </button>
            </div>

            <div class="folder-icon-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.2" stroke="currentColor" class="folder-card-svg">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
              </svg>
            </div>

            <div class="folder-card-footer">
              <h4 class="folder-card-name" :title="entry.name">{{ entry.name }}</h4>
              <span class="folder-card-sub">Dossier local</span>
            </div>
          </div>

          <!-- Fichiers (style myfileCards compact) -->
          <div
            v-for="entry in paginatedFiles"
            :key="entry.path"
            class="my-file-cards"
            :class="{ 'is-menu-open': activeMenuEntry?.path === entry.path }"
            @click="handleOpenEntry(entry)"
          >
            <div class="my-file-header" @click.stop>
              <button
                type="button"
                class="kebab-btn"
                title="Options"
                @click="toggleEntryMenu(entry, $event)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
                </svg>
              </button>
            </div>

            <div class="my-file-body">
              <div class="icon-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.4" stroke="currentColor" :class="getFileColorClass(entry)">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                </svg>
              </div>

              <div class="file-name">
                <span :title="entry.name">{{ entry.name }}</span>
              </div>
            </div>

            <div class="divider"></div>

            <div class="my-file-footer">
              <span class="file-size-text">{{ formatSize(entry.size) }}</span>
              <span class="file-ext-text">{{ formatType(entry) }}</span>
            </div>
          </div>
        </div>

        <Pagination
          v-model="currentPage"
          :totalItems="sortedEntries.length"
          :pageSize="pageSize"
          :hideOnSinglePage="true"
        />
      </div>

      <!-- VUE LISTE -->
      <div v-else class="files-content-area">
        <div class="table-wrap">
          <table class="entries-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th class="col-type">Type</th>
                <th class="col-size">Taille</th>
                <th class="col-date">Modifié</th>
                <th class="col-actions">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="entry in paginatedEntries"
                :key="entry.path"
                class="entry-row"
                @click="handleOpenEntry(entry)"
              >
                <td>
                  <div class="name-cell">
                    <svg
                      v-if="entry.isDirectory"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke-width="1.7"
                      stroke="currentColor"
                      class="entry-icon is-folder"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
                    </svg>
                    <svg
                      v-else
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke-width="1.7"
                      stroke="currentColor"
                      class="entry-icon"
                      :class="getFileColorClass(entry)"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                    </svg>
                    <span class="entry-name" :title="entry.name">{{ entry.name }}</span>
                  </div>
                </td>
                <td class="col-type muted-text">{{ formatType(entry) }}</td>
                <td class="col-size muted-text">{{ entry.isDirectory ? '—' : formatSize(entry.size) }}</td>
                <td class="col-date muted-text">{{ formatDate(entry.modifiedAt) }}</td>
                <td class="col-actions" @click.stop>
                  <div class="row-actions">
                    <button
                      v-if="authStore.canEdit"
                      type="button"
                      class="action-icon-btn"
                      title="Envoyer vers le Workspace"
                      aria-label="Envoyer vers le Workspace"
                      @click="openSendModal(entry)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="action-svg">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
                      </svg>
                    </button>

                    <button
                      v-if="!entry.isDirectory"
                      type="button"
                      class="action-icon-btn"
                      title="Ouvrir avec le système"
                      aria-label="Ouvrir avec l'application système"
                      @click="store.openWithSystem(entry.path)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="action-svg">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                      </svg>
                    </button>

                    <button
                      type="button"
                      class="action-icon-btn"
                      title="Renommer"
                      aria-label="Renommer"
                      @click="openRenameModal(entry)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="action-svg">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
                      </svg>
                    </button>

                    <button
                      type="button"
                      class="action-icon-btn is-danger"
                      title="Supprimer"
                      aria-label="Supprimer"
                      @click="openDeleteModal(entry)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="action-svg">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <Pagination
          v-model="currentPage"
          :totalItems="sortedEntries.length"
          :pageSize="pageSize"
          :hideOnSinglePage="true"
        />
      </div>
    </div>

    <!-- Aperçu intégré -->
    <filePreviewModale :preview="preview" @close="closePreview" />

    <!-- Menu contextuel adaptatif téléporté -->
    <Teleport to="body">
      <div
        v-if="activeMenuEntry"
        ref="menuRef"
        class="file-dropdown-menu"
        :style="menuStyle"
        @click.stop
      >
        <template v-if="activeMenuEntry.isDirectory">
          <button type="button" class="dropdown-row" @click="runEntryAction('open', activeMenuEntry)">Ouvrir</button>
          <button v-if="authStore.canEdit" type="button" class="dropdown-row" @click="runEntryAction('send', activeMenuEntry)">Envoyer vers le Workspace</button>
          <button type="button" class="dropdown-row" @click="runEntryAction('rename', activeMenuEntry)">Renommer</button>
          <button type="button" class="dropdown-row is-danger" @click="runEntryAction('delete', activeMenuEntry)">Supprimer</button>
        </template>
        <template v-else>
          <button type="button" class="dropdown-row" @click="runEntryAction('open', activeMenuEntry)">Visualiser / Ouvrir</button>
          <button type="button" class="dropdown-row" @click="runEntryAction('system', activeMenuEntry)">Application système</button>
          <button v-if="authStore.canEdit" type="button" class="dropdown-row" @click="runEntryAction('send', activeMenuEntry)">Envoyer vers le Workspace</button>
          <button type="button" class="dropdown-row" @click="runEntryAction('rename', activeMenuEntry)">Renommer</button>
          <button type="button" class="dropdown-row is-danger" @click="runEntryAction('delete', activeMenuEntry)">Supprimer</button>
        </template>
      </div>
    </Teleport>

    <!-- Modale Création / Renommage -->
    <renameDocModale
      :isOpen="isNameModalOpen"
      :title="nameModalTitle"
      :label="nameModalLabel"
      :placeholder="nameModalPlaceholder"
      :initialName="nameModalInitial"
      :isLoading="store.isMutating"
      :errorMessage="store.errorMessage"
      @close="closeNameModal"
      @rename="confirmNameModal"
    />

    <!-- Modale Envoi vers le Workspace -->
    <sendToWorkspaceModale
      v-if="authStore.canEdit"
      :isOpen="isSendModalOpen"
      :sourceName="sendTarget?.name || ''"
      :sourcePath="sendTarget?.path || ''"
      :isDirectory="sendTarget?.isDirectory ?? false"
      @close="isSendModalOpen = false"
    />

    <!-- Modale Confirmation suppression -->
    <deleteModale
      :isOpen="isDeleteModalOpen"
      :isLoading="store.isMutating"
      :isSuccess="false"
      :itemName="entryToDelete?.name || ''"
      :isFolder="entryToDelete?.isDirectory ?? false"
      :title="entryToDelete?.isDirectory ? 'Supprimer le dossier' : 'Supprimer le fichier'"
      description="Êtes-vous sûr de vouloir supprimer définitivement cet élément du disque ?"
      subtext="Cette suppression locale sur votre ordinateur est définitive et irréversible."
      @close="isDeleteModalOpen = false"
      @delete="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import mammoth from 'mammoth';
import BaseResearchInput from '../../BaseInput/BaseResearchInput.vue';
import BaseSelectInput from '../../BaseInput/BaseSelectInput.vue';
import filePreviewModale, { type PreviewData } from '../../modale/filePreviewModale.vue';
import renameDocModale from '../../modale/renameDocModale.vue';
import sendToWorkspaceModale from '../../modale/sendToWorkspaceModale.vue';
import deleteModale from '../../modale/deleteModale.vue';
import LogoLoader from '../../tools/LogoLoader.vue';
import Pagination from '../../tools/Pagination.vue';
import { DOCUMENT_MIME_BY_EXT } from '../../../helpers/documentFormats';
import {
  extractBaseName,
  useLocalManagerStore,
  type LocalEntry,
} from '../../../stores/localManagerStore';
import { useAuthStore } from '../../../stores/authStore';

const props = defineProps<{
  folderPath: string;
}>();

const router = useRouter();
const store = useLocalManagerStore();
const authStore = useAuthStore();

const searchQuery = ref('');
const preview = ref<PreviewData | null>(null);
const activeMenuEntry = ref<LocalEntry | null>(null);
const menuRef = ref<HTMLDivElement | null>(null);
const menuStyle = ref<Record<string, string>>({});

const isSendModalOpen = ref(false);
const sendTarget = ref<LocalEntry | null>(null);

const SORT_OPTIONS = [
  { label: 'Nom (A – Z)', value: 'name_asc' },
  { label: 'Nom (Z – A)', value: 'name_desc' },
  { label: 'Modifié récemment', value: 'date_desc' },
  { label: 'Taille décroissante', value: 'size_desc' },
];

const currentFolderName = computed(() => extractBaseName(props.folderPath) || 'Dossier local');

const filteredEntries = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return store.entries;
  return store.entries.filter((item) => item.name.toLowerCase().includes(q));
});

const sortedEntries = computed(() => {
  const list = [...filteredEntries.value];
  const sort = store.sortBy;

  list.sort((a, b) => {
    if (a.isDirectory !== b.isDirectory) {
      return a.isDirectory ? -1 : 1;
    }
    if (sort === 'name_desc') {
      return b.name.localeCompare(a.name, 'fr', { sensitivity: 'base' });
    }
    if (sort === 'date_desc') {
      return (b.modifiedAt ?? 0) - (a.modifiedAt ?? 0);
    }
    if (sort === 'size_desc') {
      return (b.size ?? -1) - (a.size ?? -1);
    }
    return a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' });
  });

  return list;
});

const currentPage = ref(1);
const pageSize = 16;

const paginatedEntries = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return sortedEntries.value.slice(start, start + pageSize);
});

const paginatedDirectories = computed(() => paginatedEntries.value.filter((e) => e.isDirectory));
const paginatedFiles = computed(() => paginatedEntries.value.filter((e) => !e.isDirectory));

watch([() => props.folderPath, searchQuery, () => store.sortBy], () => {
  currentPage.value = 1;
});

watch(currentPage, () => {
  closeMenu();
});

watch(
  () => props.folderPath,
  async (nextPath) => {
    closePreview();
    closeMenu();
    searchQuery.value = '';
    if (nextPath) {
      await store.openDirectory(nextPath);
    }
  },
  { immediate: true }
);

function closeMenu() {
  activeMenuEntry.value = null;
}

async function toggleEntryMenu(entry: LocalEntry, event: MouseEvent) {
  if (activeMenuEntry.value?.path === entry.path) {
    closeMenu();
    return;
  }

  const anchor = event.currentTarget as HTMLElement | null;
  const rect = anchor?.getBoundingClientRect();
  activeMenuEntry.value = entry;

  if (!rect) return;
  await nextTick();

  const menuRect = menuRef.value?.getBoundingClientRect();
  const menuWidth = menuRect?.width || 210;
  const menuHeight = menuRect?.height || (entry.isDirectory ? 175 : 215);
  const pad = 12;

  let left = rect.right - menuWidth;
  if (left < pad) {
    left = rect.left;
  }
  left = Math.max(pad, Math.min(left, window.innerWidth - menuWidth - pad));

  let top = rect.bottom + 6;
  if (top + menuHeight > window.innerHeight - pad) {
    top = rect.top - menuHeight - 6;
  }
  top = Math.max(pad, Math.min(top, window.innerHeight - menuHeight - pad));

  menuStyle.value = {
    top: `${Math.round(top)}px`,
    left: `${Math.round(left)}px`,
  };
}

function runEntryAction(
  action: 'open' | 'system' | 'send' | 'rename' | 'delete',
  entry: LocalEntry
) {
  closeMenu();
  if (action === 'open') {
    void handleOpenEntry(entry);
    return;
  }
  if (action === 'system') {
    void store.openWithSystem(entry.path);
    return;
  }
  if (action === 'send') {
    openSendModal(entry);
    return;
  }
  if (action === 'rename') {
    openRenameModal(entry);
    return;
  }
  if (action === 'delete') {
    openDeleteModal(entry);
  }
}

function openSendModal(entry: LocalEntry) {
  if (!authStore.canEdit) return;
  closeMenu();
  sendTarget.value = entry;
  isSendModalOpen.value = true;
}

function goToRootList() {
  router.push('/dashboard/mySpace');
}

function navigateToFolder(targetPath: string) {
  router.push(`/dashboard/mySpace/${encodeURIComponent(targetPath)}`);
}

function goUp() {
  if (store.parentPath) {
    navigateToFolder(store.parentPath);
    return;
  }
  goToRootList();
}

async function handleOpenEntry(entry: LocalEntry) {
  closeMenu();
  if (entry.isDirectory) {
    navigateToFolder(entry.path);
    return;
  }

  const ext = entry.extension.toLowerCase();
  const isImage = ['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg', 'bmp'].includes(ext);
  const isPdf = ext === 'pdf';
  const isDocx = ext === 'docx';

  if (!isImage && !isPdf && !isDocx) {
    await store.openWithSystem(entry.path);
    return;
  }

  closePreview();
  preview.value = {
    title: entry.name,
    kind: 'loading',
  };

  const bytes = await store.readLocalFileBytes(entry.path);
  if (!bytes) {
    closePreview();
    return;
  }

  if (isImage) {
    const mime = DOCUMENT_MIME_BY_EXT[ext] ?? `image/${ext === 'jpg' ? 'jpeg' : ext}`;
    const blob = new Blob([new Uint8Array(bytes)], { type: mime });
    preview.value = {
      title: entry.name,
      kind: 'image',
      url: URL.createObjectURL(blob),
    };
    return;
  }

  if (isPdf) {
    const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
    preview.value = {
      title: entry.name,
      kind: 'pdf',
      data: buffer,
    };
    return;
  }

  if (isDocx) {
    try {
      const arrayBuffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
      const result = await mammoth.convertToHtml({ arrayBuffer });
      preview.value = {
        title: entry.name,
        kind: 'docx',
        html: result.value,
      };
    } catch {
      closePreview();
      await store.openWithSystem(entry.path);
    }
  }
}

function closePreview() {
  if (preview.value?.url) {
    URL.revokeObjectURL(preview.value.url);
  }
  preview.value = null;
}

// Création sous-dossier / renommage
const isNameModalOpen = ref(false);
const nameModalMode = ref<'create_folder' | 'rename_entry'>('create_folder');
const entryToRename = ref<LocalEntry | null>(null);

const nameModalTitle = computed(() => {
  if (nameModalMode.value === 'create_folder') return 'Nouveau sous-dossier';
  return entryToRename.value?.isDirectory ? 'Renommer le dossier' : 'Renommer le fichier';
});

const nameModalLabel = computed(() => {
  if (nameModalMode.value === 'create_folder') return 'Nom du sous-dossier';
  return entryToRename.value?.isDirectory ? 'Nouveau nom du dossier' : 'Nouveau nom du fichier';
});

const nameModalPlaceholder = computed(() => {
  if (nameModalMode.value === 'create_folder') return 'Ex : Pièces justificatives';
  return entryToRename.value?.name || 'Nouveau nom';
});

const nameModalInitial = computed(() => {
  if (nameModalMode.value === 'rename_entry') return entryToRename.value?.name || '';
  return '';
});

function openCreateSubfolder() {
  store.clearError();
  nameModalMode.value = 'create_folder';
  entryToRename.value = null;
  isNameModalOpen.value = true;
}

function openRenameModal(entry: LocalEntry) {
  store.clearError();
  nameModalMode.value = 'rename_entry';
  entryToRename.value = entry;
  isNameModalOpen.value = true;
}

function closeNameModal() {
  isNameModalOpen.value = false;
  entryToRename.value = null;
  store.clearError();
}

async function confirmNameModal(newName: string) {
  if (nameModalMode.value === 'create_folder') {
    const ok = await store.createSubfolder(newName);
    if (ok) closeNameModal();
    return;
  }

  if (entryToRename.value) {
    const ok = await store.renameEntry(entryToRename.value, newName);
    if (ok) closeNameModal();
  }
}

// Suppression
const isDeleteModalOpen = ref(false);
const entryToDelete = ref<LocalEntry | null>(null);

function openDeleteModal(entry: LocalEntry) {
  store.clearError();
  entryToDelete.value = entry;
  isDeleteModalOpen.value = true;
}

async function confirmDelete() {
  if (!entryToDelete.value) return;
  const ok = await store.deleteEntry(entryToDelete.value);
  if (ok) {
    isDeleteModalOpen.value = false;
    entryToDelete.value = null;
  }
}

function formatType(entry: LocalEntry): string {
  if (entry.isDirectory) return 'Dossier';
  return entry.extension ? entry.extension.toUpperCase() : 'DOC';
}

function formatSize(bytes: number | null): string {
  if (bytes === null || bytes === undefined) return '—';
  if (bytes < 1024) return `${bytes} o`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} Ko`;
  return `${(kb / 1024).toFixed(1)} Mo`;
}

function formatDate(ts: number | null): string {
  if (!ts) return '—';
  return new Date(ts).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function getFileColorClass(entry: LocalEntry): string {
  const ext = entry.extension.toLowerCase();
  if (ext === 'pdf') return 'icon-pdf';
  if (['doc', 'docx', 'txt', 'rtf', 'odt'].includes(ext)) return 'icon-word';
  if (['xls', 'xlsx', 'csv', 'ods'].includes(ext)) return 'icon-excel';
  if (['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg', 'bmp'].includes(ext)) return 'icon-image';
  return 'icon-other';
}

function onWindowClick() {
  if (activeMenuEntry.value !== null) {
    closeMenu();
  }
}

function onWindowKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && activeMenuEntry.value !== null) {
    closeMenu();
  }
}

onMounted(() => {
  window.addEventListener('click', onWindowClick);
  window.addEventListener('scroll', closeMenu, true);
  window.addEventListener('resize', closeMenu);
  window.addEventListener('keydown', onWindowKeydown);
});

onUnmounted(() => {
  window.removeEventListener('click', onWindowClick);
  window.removeEventListener('scroll', closeMenu, true);
  window.removeEventListener('resize', closeMenu);
  window.removeEventListener('keydown', onWindowKeydown);
  closePreview();
});
</script>

<style scoped>
.affair-detail-section {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 0;
  min-width: 0;
  overflow: hidden;
  background: #f1f3f5;
}

/* === EN-TÊTE (identique à affairDetailSection) === */
.affair-header {
  padding: 1rem 1.5rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 0;
}

.back-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.back-btn:hover:not(:disabled) {
  background: #f3f4f6;
  color: #111827;
  border-color: #d1d5db;
}

.back-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.header-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.page-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 500;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.page-subtitle-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.2rem;
  min-width: 0;
}

.ref-text {
  font-weight: 500;
  color: #6b7280;
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 460px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-shrink: 0;
}

.new-folder-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  background: #ffffff;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.new-folder-btn:hover:not(:disabled) {
  background: #f9fafb;
  color: #111827;
  border-color: #9ca3af;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  background: var(--primary-color, #005792);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-btn:hover:not(:disabled) {
  background: var(--primary-color-dark, #005380);
}

.add-btn:disabled,
.new-folder-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.header-action-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* === BARRE FIL D'ARIANE + OUTILS === */
.folder-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  padding: 0.65rem 1.5rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  gap: 0.85rem;
  flex-shrink: 0;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
  min-width: 0;
}

.breadcrumb-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 0.85rem;
  font-weight: 500;
  padding: 0.3rem 0.6rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.breadcrumb-item:hover {
  background: #f3f4f6;
  color: #111827;
}

.breadcrumb-item.active {
  color: var(--primary-color, #005792);
  font-weight: 600;
  background: #eff6ff;
}

.breadcrumb-separator {
  color: #cbd5e1;
  font-size: 0.85rem;
  font-weight: 600;
}

.nav-tools {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.sort-wrap :deep(.select-input) {
  padding: 0.45rem 2.1rem 0.45rem 0.75rem;
  font-size: 0.84rem;
}

.view-toggle {
  display: inline-flex;
  border: 1px solid #e2e8f0;
  border-radius: 9px;
  background: #f8fafc;
  padding: 0.18rem;
  gap: 0.18rem;
}

.view-btn {
  width: 32px;
  height: 30px;
  border-radius: 7px;
  border: none;
  background: transparent;
  color: #64748b;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.view-btn:hover {
  color: #0f172a;
}

.view-btn.is-active {
  background: #ffffff;
  color: var(--primary-color, #005792);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
}

.view-svg {
  width: 17px;
  height: 17px;
}

/* === BANNIÈRE ERREUR === */
.error-banner {
  margin: 0.75rem 1.5rem 0;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.error-close {
  background: none;
  border: none;
  color: #dc2626;
  font-size: 1.25rem;
  cursor: pointer;
  line-height: 1;
}

/* === ESPACE DE CONTENU === */
.files-workspace {
  flex: 1;
  width: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: #64748b;
  font-size: 0.95rem;
}

.empty-state-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.empty-state {
  width: 100%;
  max-width: 540px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3.5rem 2rem;
  background: #ffffff;
  border: 2px dashed #cbd5e1;
  border-radius: 20px;
  text-align: center;
  gap: 0.9rem;
  cursor: pointer;
}

.empty-icon-circle {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: #eff6ff;
  color: var(--primary-color, #005792);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #1e293b;
}

.empty-text {
  margin: 0;
  font-size: 0.88rem;
  color: #64748b;
  max-width: 380px;
}

.empty-buttons-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.empty-cta-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.3rem;
  background: var(--primary-color, #005792);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.empty-secondary-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.3rem;
  background: #ffffff;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

/* === GRILLE === */
.files-content-area {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  scrollbar-width: thin;
  padding: 0.95rem 1.25rem 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
}

.file-list--grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(175px, 1fr));
  gap: 0.9rem;
  align-content: start;
}

/* Carte sous-dossier (style folderCards) */
.folder-card {
  width: 100%;
  max-width: 195px;
  height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 0.65rem;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  position: relative;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.folder-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px -3px rgba(37, 99, 235, 0.12);
  border-color: #2563eb;
}

.card-top-actions,
.my-file-header {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  position: relative;
}

.folder-icon-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.folder-card:hover .folder-icon-wrap {
  color: #2563eb;
}

.folder-card-svg {
  width: 56px;
  height: 56px;
}

.folder-card-footer {
  width: 100%;
  text-align: center;
  padding-bottom: 0.25rem;
}

.folder-card-name {
  margin: 0;
  color: #1f2937;
  font-size: 0.86rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-card-sub {
  display: block;
  margin-top: 0.15rem;
  font-size: 0.72rem;
  color: #6b7280;
}

/* Carte fichier (style myfileCards compact) */
.my-file-cards {
  width: 100%;
  max-width: 195px;
  height: 220px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 0.55rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.my-file-cards:hover {
  border-color: #2563eb;
  transform: translateY(-4px);
  box-shadow: 0 10px 20px -3px rgba(37, 99, 235, 0.12);
}

.my-file-cards.is-menu-open,
.folder-card.is-menu-open {
  z-index: 40;
}

.kebab-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: #f8fafc;
  color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.kebab-btn svg {
  width: 20px;
  height: 20px;
}

.kebab-btn:hover {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}

.file-dropdown-menu {
  position: fixed;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 12px 28px -5px rgba(15, 23, 42, 0.16), 0 8px 10px -6px rgba(15, 23, 42, 0.08);
  padding: 0.4rem;
  min-width: 205px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.dropdown-row {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #1f2937;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  white-space: nowrap;
}

.dropdown-row:hover {
  background: #f3f4f6;
  color: #111827;
}

.dropdown-row.is-danger {
  color: #dc2626;
}

.dropdown-row.is-danger:hover {
  background: #fef2f2;
}

.my-file-body {
  padding: 0 0.35rem;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.icon-wrapper {
  height: 62px;
  width: 56px;
  border: 1px solid #e5e7eb;
  border-radius: 9px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-wrapper svg {
  width: 28px;
  height: 28px;
}

.icon-pdf { color: #e53935; }
.icon-word { color: #1e88e5; }
.icon-excel { color: #43a047; }
.icon-image { color: #8e24aa; }
.icon-other { color: #757575; }

.file-name {
  width: 100%;
  min-width: 0;
  padding: 0 0.25rem;
  text-align: center;
}

.file-name span {
  font-size: 0.82rem;
  font-weight: 600;
  color: #1f2937;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow-wrap: anywhere;
  word-break: break-word;
  line-height: 1.25;
}

.divider {
  width: 100%;
  height: 1px;
  background-color: #f1f5f9;
}

.my-file-footer {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.15rem 0.35rem;
}

.file-size-text {
  font-size: 0.7rem;
  font-weight: 500;
  color: #94a3b8;
}

.file-ext-text {
  font-size: 0.7rem;
  font-weight: 700;
  color: #475569;
}

/* === VUE LISTE === */
.table-wrap {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.entries-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.entries-table th {
  text-align: left;
  font-size: 0.76rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  padding: 0.72rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #fafafa;
}

.entries-table td {
  padding: 0.7rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.88rem;
  color: #1e293b;
}

.entry-row {
  cursor: pointer;
}

.entry-row:hover {
  background: #f8fafc;
}

.entry-row:last-child td {
  border-bottom: none;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  min-width: 0;
}

.entry-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.entry-icon.is-folder {
  color: var(--primary-color, #005792);
}

.entry-name {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-type { width: 90px; }
.col-size { width: 105px; }
.col-date { width: 135px; }
.col-actions { width: 145px; text-align: right; }

.entries-table th.col-actions {
  text-align: right;
}

.muted-text {
  color: #64748b;
  font-size: 0.82rem;
}

.row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.2rem;
}

.action-icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 7px;
  border: none;
  background: transparent;
  color: #64748b;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.action-icon-btn:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.action-icon-btn.is-danger:hover {
  background: #fee2e2;
  color: #dc2626;
}

.action-svg {
  width: 16px;
  height: 16px;
}

.size-4 {
  width: 1rem;
  height: 1rem;
}

.size-12 {
  width: 3rem;
  height: 3rem;
}
</style>
