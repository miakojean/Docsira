<template>
  <div class="main-layout">
    <sidebar />
    <main class="main-content">
      <div class="page">
        <!-- En-tête -->
        <header class="page-header">
          <button type="button" class="back-btn" aria-label="Retour aux dossiers" @click="goBack">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
            </svg>
          </button>

          <div class="header-info">
            <div class="header-line">
              <h1 class="page-title">{{ dossier?.title || 'Dossier' }}</h1>
              <span v-if="dossier" class="badge" :class="dossier.statut.toLowerCase()">
                {{ statutLabels[dossier.statut] || dossier.statut }}
              </span>
            </div>
            <p v-if="dossier" class="page-subtitle">
              {{ dossier.reference_affair }}
              <template v-if="dossier.client"> · {{ dossier.client.nom_complet }}</template>
              <span class="meta-dot">·</span>
              <span class="meta-docs">{{ documents.length }} document(s)</span>
            </p>
          </div>

          <!-- Actions de l'en-tête -->
          <div class="header-actions">
            <!-- Contrôles du Canvas -->
            <div class="canvas-controls" v-if="documents.length > 0">
              <button type="button" class="ctrl-btn" title="Réaligner automatiquement" @click="autoLayout">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z" />
                </svg>
                <span>Réaligner</span>
              </button>
              <button type="button" class="ctrl-btn icon-only" title="Zoom arrière" @click="zoomOut">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14" />
                </svg>
              </button>
              <span class="zoom-value" @click="resetZoom" title="Réinitialiser le zoom">{{ Math.round(zoomLevel * 100) }}%</span>
              <button type="button" class="ctrl-btn icon-only" title="Zoom avant" @click="zoomIn">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
              </button>
            </div>

            <!-- Bouton Nouvelle version pour le document sélectionné -->
            <button
              v-if="selectedDoc"
              type="button"
              class="btn btn-version-header"
              :disabled="docStore.isUploading"
              :title="`Déposer la version v${selectedDoc.version + 1} de &quot;${selectedDoc.title}&quot;`"
              @click="pickNewVersion(selectedDoc)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
              <span>Nouvelle version (v{{ selectedDoc.version + 1 }})</span>
            </button>

            <!-- Bouton Ajouter des documents -->
            <button
              v-if="documents.length > 0"
              type="button"
              class="btn btn-primary"
              :disabled="docStore.isUploading"
              @click="pickFromDisk"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              {{ docStore.isUploading ? 'Import...' : 'Ajouter un document' }}
            </button>
          </div>
        </header>

        <!-- Inputs fichiers masqués pour sélection résiliente et universelle -->
        <input
          ref="diskFileInputRef"
          type="file"
          multiple
          class="hidden-file-input"
          @change="onDiskFileInputChange"
        />
        <input
          ref="versionFileInputRef"
          type="file"
          class="hidden-file-input"
          @change="onVersionFileInputChange"
        />

        <p v-if="notFound" class="state-text">Dossier introuvable.</p>

        <template v-else>
          <p v-if="docStore.errorMessage" class="error-banner">{{ docStore.errorMessage }}</p>

          <div v-if="docStore.isLoading && documents.length === 0" class="state-text">
            <div class="spinner"></div>
            Chargement de l'espace des documents...
          </div>

          <!-- Dossier vide : inviter à parcourir le disque -->
          <div
            v-else-if="documents.length === 0"
            class="empty-zone"
            :class="{ dragging: isDragging }"
          >
            <div class="empty-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.3" stroke="currentColor" class="size-10">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
              </svg>
            </div>
            <p class="empty-title">Espace vide — Aucun document dans ce dossier</p>
            <p class="empty-text">
              Glissez-déposez vos fichiers ici ou parcourez votre disque dur.<br />
              Chaque ajout ou mise à jour dessinera automatiquement l'arbre d'évolution.
            </p>
            <button type="button" class="btn btn-primary" :disabled="docStore.isUploading" @click="pickFromDisk">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
              </svg>
              {{ docStore.isUploading ? 'Import en cours...' : 'Parcourir mon disque dur' }}
            </button>
          </div>

          <!-- Espace interactif des documents (Canvas avec nœuds et liaisons) -->
          <div
            v-else
            ref="viewportRef"
            class="evolution-canvas-viewport"
            :class="{ dragging: isDragging, panning: isPanning }"
            @mousedown="onViewportMouseDown"
            @wheel.prevent="onViewportWheel"
          >
            <!-- Légende interactive en haut à gauche -->
            <div class="canvas-legend">
              <div class="legend-item">
                <span class="legend-line added"></span>
                <span class="legend-label">Ajout au dossier</span>
              </div>
              <div class="legend-item">
                <span class="legend-line updated"></span>
                <span class="legend-label">Nouvelle version</span>
              </div>
              <span class="legend-hint">· Glissez les icônes pour réorganiser</span>
            </div>

            <!-- Espace infini transformable (pan / zoom) -->
            <div
              class="evolution-canvas"
              :style="{
                transform: `translate(${panX}px, ${panY}px) scale(${zoomLevel})`,
              }"
            >
              <!-- Calque SVG des liaisons -->
              <svg class="connections-layer" :style="{ width: `${canvasBounds.width}px`, height: `${canvasBounds.height}px` }">
                <defs>
                  <!-- Marqueur flèche pour les ajouts -->
                  <marker
                    id="arrow-added"
                    viewBox="0 0 10 10"
                    refX="9"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#3b82f6" />
                  </marker>

                  <!-- Marqueur flèche pour les mises à jour -->
                  <marker
                    id="arrow-updated"
                    viewBox="0 0 10 10"
                    refX="9"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981" />
                  </marker>
                </defs>

                <!-- Lignes de liaison -->
                <g v-for="link in computedLinks" :key="link.id" class="link-group" :class="[link.relation.toLowerCase(), { active: isLinkActive(link) }]">
                  <!-- Ligne visible avec flèche -->
                  <path
                    :d="link.path"
                    class="link-line"
                    :marker-end="link.relation === 'UPDATED' ? 'url(#arrow-updated)' : 'url(#arrow-added)'"
                  />
                  <!-- Label badge sur la liaison -->
                  <g class="link-badge-group" :transform="`translate(${link.mid.x}, ${link.mid.y})`">
                    <rect
                      x="-38"
                      y="-11"
                      width="76"
                      height="22"
                      rx="11"
                      class="link-badge-bg"
                    />
                    <text x="0" y="4" text-anchor="middle" class="link-badge-text">
                      {{ link.relation === 'UPDATED' ? `v${link.targetVersion}` : 'Ajout' }}
                    </text>
                  </g>
                </g>
              </svg>

              <!-- Nœuds de documents (Icône en grand + Nom juste en bas) -->
              <div
                v-for="doc in documents"
                :key="doc.id"
                class="document-node"
                :class="{
                  selected: selectedDocId === doc.id,
                  dragging: draggingDocId === doc.id,
                  'is-updated': doc.relation === 'UPDATED',
                }"
                :style="{
                  left: `${getNodePosition(doc).x}px`,
                  top: `${getNodePosition(doc).y}px`,
                }"
                @mousedown.stop="onNodeMouseDown($event, doc)"
                @click.stop="selectDoc(doc)"
                @dblclick.stop="openDocument(doc)"
              >
                <!-- Badge de version ou de relation -->
                <div class="node-badge" :class="doc.relation.toLowerCase()">
                  <span v-if="doc.relation === 'UPDATED'">v{{ doc.version }}</span>
                  <span v-else-if="doc.relation === 'ADDED'">+ Ajout</span>
                  <span v-else>Racine</span>
                </div>

                <!-- Icône du document -->
                <div class="node-icon-wrapper" :class="iconKind(doc.extension)">
                  <!-- PDF -->
                  <svg v-if="iconKind(doc.extension) === 'pdf'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                    <path d="M5.625 1.5c-1.036 0-1.875.84-1.875 1.875v17.25c0 1.035.84 1.875 1.875 1.875h12.75c1.035 0 1.875-.84 1.875-1.875V12.75A3.75 3.75 0 0 0 16.5 9h-1.875a1.875 1.875 0 0 1-1.875-1.875V5.25A3.75 3.75 0 0 0 9 1.5H5.625Z" />
                    <path d="M12.971 1.816A5.23 5.23 0 0 1 14.25 5.25v1.875c0 .207.168.375.375.375H16.5a5.23 5.23 0 0 1 3.434 1.279 9.768 9.768 0 0 0-6.963-6.963Z" />
                  </svg>
                  <!-- Image -->
                  <svg v-else-if="iconKind(doc.extension) === 'image'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                    <path fill-rule="evenodd" d="M1.5 6a2.25 2.25 0 0 1 2.25-2.25h16.5A2.25 2.25 0 0 1 22.5 6v12a2.25 2.25 0 0 1-2.25 2.25H3.75A2.25 2.25 0 0 1 1.5 18V6ZM3 16.06V18c0 .414.336.75.75.75h16.5A.75.75 0 0 0 21 18v-1.94l-2.69-2.689a1.5 1.5 0 0 0-2.12 0l-.88.879.97.97a.75.75 0 1 1-1.06 1.06l-5.16-5.159a1.5 1.5 0 0 0-2.12 0L3 16.061Zm10.125-7.81a1.125 1.125 0 1 1 2.25 0 1.125 1.125 0 0 1-2.25 0Z" clip-rule="evenodd" />
                  </svg>
                  <!-- Document texte/Word -->
                  <svg v-else-if="iconKind(doc.extension) === 'doc'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                    <path fill-rule="evenodd" d="M5.625 1.5H9a3.75 3.75 0 0 1 3.75 3.75v1.875c0 1.036.84 1.875 1.875 1.875H16.5a3.75 3.75 0 0 1 3.75 3.75v7.875c0 1.035-.84 1.875-1.875 1.875H5.625a1.875 1.875 0 0 1-1.875-1.875V3.375c0-1.036.84-1.875 1.875-1.875ZM9.75 14.25a.75.75 0 0 0 0 1.5H15a.75.75 0 0 0 0-1.5H9.75Zm0 3a.75.75 0 0 0 0 1.5h3.75a.75.75 0 0 0 0-1.5H9.75Z" clip-rule="evenodd" />
                    <path d="M14.25 5.25a5.23 5.23 0 0 0-1.279-3.434 9.768 9.768 0 0 1 6.963 6.963A5.23 5.23 0 0 0 16.5 7.5h-1.875a.375.375 0 0 1-.375-.375V5.25Z" />
                  </svg>
                  <!-- Tableur -->
                  <svg v-else-if="iconKind(doc.extension) === 'sheet'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                    <path fill-rule="evenodd" d="M3 6a3 3 0 0 1 3-3h12a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V6Zm3-1.5A1.5 1.5 0 0 0 4.5 6v2.25h15V6A1.5 1.5 0 0 0 18 4.5H6Zm15 5.25H4.5v3h15v-3Zm0 4.5H4.5V18A1.5 1.5 0 0 0 6 19.5h12a1.5 1.5 0 0 0 1.5-1.5v-1.75Z" clip-rule="evenodd" />
                  </svg>
                  <!-- Autre fichier -->
                  <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                    <path fill-rule="evenodd" d="M5.625 1.5H9a3.75 3.75 0 0 1 3.75 3.75v1.875c0 1.036.84 1.875 1.875 1.875H16.5a3.75 3.75 0 0 1 3.75 3.75v7.875c0 1.035-.84 1.875-1.875 1.875H5.625a1.875 1.875 0 0 1-1.875-1.875V3.375c0-1.036.84-1.875 1.875-1.875Z" clip-rule="evenodd" />
                  </svg>

                  <span class="ext-tag">{{ (doc.extension || 'FILE').toUpperCase() }}</span>
                </div>

                <!-- Nom du document juste en bas -->
                <div class="node-label">
                  <span class="node-title" :title="doc.title">{{ doc.title }}</span>
                  <span class="node-meta">{{ formatSize(doc.size) }} · {{ formatDate(doc.uploaded_at) }}</span>
                </div>

                <!-- Barre d'actions rapides (au hover ou sélection) -->
                <div class="node-toolbar" @mousedown.stop>
                  <button type="button" class="node-tool-btn primary" title="Ouvrir le document" @click.stop="openDocument(doc)">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-3-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                    </svg>
                  </button>
                  <button type="button" class="node-tool-btn success" title="Déposer une nouvelle version" @click.stop="pickNewVersion(doc)">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-3-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
                    </svg>
                  </button>
                  <button type="button" class="node-tool-btn" title="Télécharger" @click.stop="downloadDocument(doc)">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-3-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                    </svg>
                  </button>
                  <button type="button" class="node-tool-btn" title="Renommer" @click.stop="openRename(doc)">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-3-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125" />
                    </svg>
                  </button>
                  <button type="button" class="node-tool-btn danger" title="Supprimer" @click.stop="openDelete(doc)">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-3-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </main>

    <!-- Aperçu (images / PDF / text) -->
    <Teleport to="body">
      <div v-if="preview" class="overlay-modal" @click.self="closePreview">
        <div class="preview-card" role="dialog" aria-modal="true">
          <div class="preview-header">
            <span class="preview-title">{{ preview.title }}</span>
            <button type="button" class="close-btn" aria-label="Fermer" @click="closePreview">&times;</button>
          </div>
          <img v-if="preview.kind === 'image'" :src="preview.url" :alt="preview.title" class="preview-media" />
          <iframe v-else :src="preview.url" class="preview-media" :title="preview.title"></iframe>
        </div>
      </div>

      <!-- Renommer -->
      <div v-if="renaming" class="overlay-modal" @click.self="renaming = null">
        <form class="rename-card" @submit.prevent="confirmRename">
          <h3 class="rename-title">Renommer le document</h3>
          <input v-model="renameValue" type="text" class="text-input" maxlength="200" autofocus />
          <div class="rename-footer">
            <button type="button" class="btn" @click="renaming = null">Annuler</button>
            <button type="submit" class="btn btn-primary" :disabled="!renameValue.trim()">Enregistrer</button>
          </div>
        </form>
      </div>
    </Teleport>

    <!-- Modale de suppression -->
    <deleteModale
      :isOpen="isDeleteOpen"
      :isLoading="isDeleting"
      :isSuccess="isDeleteSuccess"
      :itemName="docToDelete?.title || 'ce document'"
      :isFolder="false"
      title="Supprimer le document"
      description="Êtes-vous sûr de vouloir supprimer définitivement ce document ?"
      subtext="La chaîne d'évolution sera automatiquement reliée pour préserver l'historique."
      @close="isDeleteOpen = false; isDeleteSuccess = false"
      @delete="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { open as openDialog, save as saveDialog } from '@tauri-apps/plugin-dialog';
import { readFile, writeFile } from '@tauri-apps/plugin-fs';
import { getCurrentWebview } from '@tauri-apps/api/webview';
import sidebar from '../../components/navbar/sidebar.vue';
import deleteModale from '../../components/modale/deleteModale.vue';
import { useClientDossierStore, type Dossier } from '../../stores/dossierStore';
import { useDocumentStore, type DossierDocument } from '../../stores/documentStore';

const NODE_WIDTH = 140;
const NODE_HEIGHT = 160;

const route = useRoute();
const router = useRouter();
const dossierStore = useClientDossierStore();
const docStore = useDocumentStore();

const affairId = computed(() => String(route.params.id));
const dossier = ref<Dossier | null>(null);
const notFound = ref(false);
const isDragging = ref(false);
const selectedDocId = ref<string | null>(null);

const documents = computed(() => docStore.documents);
const selectedDoc = computed(() =>
  selectedDocId.value ? documents.value.find((d) => d.id === selectedDocId.value) ?? null : null
);

// Positions locales pour le déplacement fluide (id -> { x, y })
const localPositions = ref<Record<string, { x: number; y: number }>>({});

// Pan & Zoom
const viewportRef = ref<HTMLElement | null>(null);
const panX = ref(40);
const panY = ref(40);
const zoomLevel = ref(1);
const isPanning = ref(false);
let startPanMouse = { x: 0, y: 0 };
let startPanCoords = { x: 0, y: 0 };

// Dragging de nœud
const draggingDocId = ref<string | null>(null);
let dragStartMouse = { x: 0, y: 0 };
let dragStartPos = { x: 0, y: 0 };

const statutLabels: Record<string, string> = {
  NOUVEAU: 'Nouveau',
  EN_COURS: 'En cours',
  EN_ATTENTE: 'En attente',
  BLOQUE: 'Bloqué',
  TERMINE: 'Terminé',
  CLOTURE: 'Clôturé',
  ANNULE: 'Annulé',
};

const mimeByExt: Record<string, string> = {
  pdf: 'application/pdf',
  png: 'image/png',
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  gif: 'image/gif',
  webp: 'image/webp',
  svg: 'image/svg+xml',
  txt: 'text/plain',
};

function extOf(name: string) {
  const i = name.lastIndexOf('.');
  return i === -1 ? '' : name.slice(i + 1).toLowerCase();
}

function iconKind(ext: string) {
  if (ext === 'pdf') return 'pdf';
  if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'].includes(ext)) return 'image';
  if (['doc', 'docx', 'odt', 'rtf', 'txt'].includes(ext)) return 'doc';
  if (['xls', 'xlsx', 'csv', 'ods'].includes(ext)) return 'sheet';
  return 'other';
}

function formatSize(bytes: number) {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} o`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} Ko`;
  return `${(bytes / 1024 / 1024).toFixed(1)} Mo`;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
}

function goBack() {
  router.push('/dashboard/affairs');
}

// ---------- Positions & Layout automatique ----------
function getNodePosition(doc: DossierDocument): { x: number; y: number } {
  if (localPositions.value[doc.id]) {
    return localPositions.value[doc.id];
  }
  if (doc.pos_x != null && doc.pos_y != null) {
    localPositions.value[doc.id] = { x: doc.pos_x, y: doc.pos_y };
    return localPositions.value[doc.id];
  }
  // Position temporaire avant auto-layout
  return { x: 60, y: 80 };
}

/** Calcule une disposition en arbre chronologique élégante de gauche à droite */
function autoLayout() {
  const docs = [...documents.value].sort(
    (a, b) => new Date(a.uploaded_at).getTime() - new Date(b.uploaded_at).getTime()
  );
  if (docs.length === 0) return;

  const docMap = new Map(docs.map((d) => [d.id, d]));
  const childrenMap = new Map<string, string[]>();
  const roots: string[] = [];

  for (const doc of docs) {
    if (doc.parent && docMap.has(doc.parent)) {
      const list = childrenMap.get(doc.parent) ?? [];
      list.push(doc.id);
      childrenMap.set(doc.parent, list);
    } else {
      roots.push(doc.id);
    }
  }

  const HORIZONTAL_GAP = 240;
  const VERTICAL_GAP = 180;
  const newPositions: Record<string, { x: number; y: number }> = {};
  let currentY = 80;

  function layoutSubtree(nodeId: string, depth: number): { top: number; bottom: number } {
    const children = childrenMap.get(nodeId) ?? [];
    const x = 80 + depth * HORIZONTAL_GAP;

    if (children.length === 0) {
      const y = currentY;
      currentY += VERTICAL_GAP;
      newPositions[nodeId] = { x, y };
      return { top: y, bottom: y };
    }

    const childSpans = children.map((cId) => layoutSubtree(cId, depth + 1));
    const firstTop = childSpans[0].top;
    const lastBottom = childSpans[childSpans.length - 1].bottom;
    const y = (firstTop + lastBottom) / 2;

    newPositions[nodeId] = { x, y };
    return { top: firstTop, bottom: lastBottom };
  }

  for (const rootId of roots) {
    layoutSubtree(rootId, 0);
    currentY += 40;
  }

  // Enregistrer les positions calculées
  localPositions.value = newPositions;
  for (const [id, pos] of Object.entries(newPositions)) {
    docStore.moveDocument(id, pos.x, pos.y);
  }
  resetZoom();
}

// Dimension du canevas pour couvrir tous les nœuds
const canvasBounds = computed(() => {
  let maxX = 1200;
  let maxY = 800;
  for (const doc of documents.value) {
    const pos = getNodePosition(doc);
    if (pos.x + 300 > maxX) maxX = pos.x + 300;
    if (pos.y + 300 > maxY) maxY = pos.y + 300;
  }
  return { width: maxX, height: maxY };
});

// ---------- Liaisons entre documents ----------
interface ComputedLink {
  id: string;
  sourceId: string;
  targetId: string;
  relation: string;
  targetVersion: number;
  path: string;
  mid: { x: number; y: number };
}

const computedLinks = computed<ComputedLink[]>(() => {
  const docMap = new Map(documents.value.map((d) => [d.id, d]));
  const links: ComputedLink[] = [];

  for (const target of documents.value) {
    if (!target.parent) continue;
    const source = docMap.get(target.parent);
    if (!source) continue;

    const sPos = getNodePosition(source);
    const tPos = getNodePosition(target);

    // Sortie à droite du nœud parent, entrée à gauche du nœud cible
    const sx = sPos.x + NODE_WIDTH;
    const sy = sPos.y + NODE_HEIGHT / 2 - 12;
    const tx = tPos.x;
    const ty = tPos.y + NODE_HEIGHT / 2 - 12;

    const dx = Math.abs(tx - sx);
    const cx1 = sx + Math.max(40, dx * 0.5);
    const cy1 = sy;
    const cx2 = tx - Math.max(40, dx * 0.5);
    const cy2 = ty;

    const path = `M ${sx} ${sy} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${tx} ${ty}`;
    const mid = {
      x: (sx + tx) / 2,
      y: (sy + ty) / 2,
    };

    links.push({
      id: `${source.id}->${target.id}`,
      sourceId: source.id,
      targetId: target.id,
      relation: target.relation,
      targetVersion: target.version,
      path,
      mid,
    });
  }

  return links;
});

function isLinkActive(link: ComputedLink) {
  return (
    selectedDocId.value === link.sourceId || selectedDocId.value === link.targetId
  );
}

function selectDoc(doc: DossierDocument) {
  selectedDocId.value = doc.id;
}

// ---------- Pan & Zoom ----------
function zoomIn() {
  zoomLevel.value = Math.min(2, Math.round((zoomLevel.value + 0.15) * 100) / 100);
}

function zoomOut() {
  zoomLevel.value = Math.max(0.4, Math.round((zoomLevel.value - 0.15) * 100) / 100);
}

function resetZoom() {
  zoomLevel.value = 1;
  panX.value = 40;
  panY.value = 40;
}

function onViewportWheel(e: WheelEvent) {
  const delta = e.deltaY < 0 ? 0.08 : -0.08;
  const newZoom = Math.min(2, Math.max(0.4, zoomLevel.value + delta));
  zoomLevel.value = Math.round(newZoom * 100) / 100;
}

function onViewportMouseDown(e: MouseEvent) {
  if (e.button !== 0) return;
  // Démarre le panoramique du canevas
  selectedDocId.value = null;
  isPanning.value = true;
  startPanMouse = { x: e.clientX, y: e.clientY };
  startPanCoords = { x: panX.value, y: panY.value };

  window.addEventListener('mousemove', onViewportMouseMove);
  window.addEventListener('mouseup', onViewportMouseUp);
}

function onViewportMouseMove(e: MouseEvent) {
  if (!isPanning.value) return;
  panX.value = startPanCoords.x + (e.clientX - startPanMouse.x);
  panY.value = startPanCoords.y + (e.clientY - startPanMouse.y);
}

function onViewportMouseUp() {
  isPanning.value = false;
  window.removeEventListener('mousemove', onViewportMouseMove);
  window.removeEventListener('mouseup', onViewportMouseUp);
}

// ---------- Déplacement d'un nœud (Drag & Drop) ----------
function onNodeMouseDown(e: MouseEvent, doc: DossierDocument) {
  if (e.button !== 0) return;
  selectedDocId.value = doc.id;
  draggingDocId.value = doc.id;
  dragStartMouse = { x: e.clientX, y: e.clientY };
  const currentPos = getNodePosition(doc);
  dragStartPos = { ...currentPos };

  window.addEventListener('mousemove', onNodeMouseMove);
  window.addEventListener('mouseup', onNodeMouseUp);
}

function onNodeMouseMove(e: MouseEvent) {
  if (!draggingDocId.value) return;
  const dx = (e.clientX - dragStartMouse.x) / zoomLevel.value;
  const dy = (e.clientY - dragStartMouse.y) / zoomLevel.value;

  localPositions.value[draggingDocId.value] = {
    x: Math.max(20, Math.round(dragStartPos.x + dx)),
    y: Math.max(20, Math.round(dragStartPos.y + dy)),
  };
}

function onNodeMouseUp() {
  if (!draggingDocId.value) return;
  const docId = draggingDocId.value;
  draggingDocId.value = null;
  window.removeEventListener('mousemove', onNodeMouseMove);
  window.removeEventListener('mouseup', onNodeMouseUp);

  const finalPos = localPositions.value[docId];
  if (finalPos) {
    docStore.moveDocument(docId, finalPos.x, finalPos.y);
  }
}

// ---------- Sélection et Import de fichiers ----------
const diskFileInputRef = ref<HTMLInputElement | null>(null);
const versionFileInputRef = ref<HTMLInputElement | null>(null);
const pendingVersionDoc = ref<DossierDocument | null>(null);

function promptVersionFileInput(doc: DossierDocument) {
  pendingVersionDoc.value = doc;
  if (versionFileInputRef.value) {
    versionFileInputRef.value.value = '';
    versionFileInputRef.value.click();
  }
}

async function onVersionFileInputChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  const targetDoc = pendingVersionDoc.value;
  pendingVersionDoc.value = null;
  target.value = '';
  if (!file || !targetDoc) return;
  await executeVersionUpload(targetDoc, file);
}

async function onDiskFileInputChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const files = Array.from(target.files ?? []);
  target.value = '';
  if (files.length === 0) return;
  if (await docStore.uploadDocuments(affairId.value, files)) {
    await refreshDossier();
    ensureAllNodesPositioned();
  }
}

async function importPaths(paths: string[]) {
  if (paths.length === 0) return;
  const files: File[] = [];
  for (const path of paths) {
    try {
      const bytes = await readFile(path);
      const name = path.split(/[\\/]/).pop() || 'document';
      files.push(new File([bytes], name, { type: mimeByExt[extOf(name)] || 'application/octet-stream' }));
    } catch (error) {
      console.error(`Lecture impossible : ${path}`, error);
    }
  }
  if (files.length === 0) {
    // Si la lecture directe des chemins a échoué (ex. permissions Tauri FS), fallback vers l'explorateur HTML
    if (diskFileInputRef.value) {
      diskFileInputRef.value.value = '';
      diskFileInputRef.value.click();
    }
    return;
  }
  if (await docStore.uploadDocuments(affairId.value, files)) {
    await refreshDossier();
    // Positionner les nouveaux documents juste à droite
    ensureAllNodesPositioned();
  }
}

async function pickFromDisk() {
  try {
    const selected = await openDialog({ multiple: true, directory: false, title: 'Choisir des documents' });
    if (!selected) return;
    const paths = Array.isArray(selected) ? selected : [selected];
    if (paths.length > 0) {
      await importPaths(paths);
    }
  } catch (error) {
    console.warn('openDialog indisponible, passage par sélecteur standard :', error);
    if (diskFileInputRef.value) {
      diskFileInputRef.value.value = '';
      diskFileInputRef.value.click();
    }
  }
}

// ---------- Déposer une nouvelle version ----------
async function executeVersionUpload(doc: DossierDocument, file: File) {
  const parentPos = getNodePosition(doc);
  // Trouver tous les enfants actuels pour éviter la superposition
  const existingChildren = documents.value.filter((d) => d.parent === doc.id);
  const offsetIndex = existingChildren.length;
  const newPos = {
    x: parentPos.x + 240,
    y: parentPos.y + (offsetIndex === 0 ? 0 : offsetIndex * 150),
  };

  const newDoc = await docStore.uploadNewVersion(doc.id, file, newPos.x, newPos.y);
  if (newDoc) {
    localPositions.value[newDoc.id] = newPos;
    selectedDocId.value = newDoc.id;
    await refreshDossier();
    await docStore.fetchDocuments(affairId.value);
    localPositions.value[newDoc.id] = newPos;
  }
}

async function pickNewVersion(doc: DossierDocument) {
  try {
    let file: File | null = null;
    let selectedPath: string | null = null;

    try {
      const selected = await openDialog({
        multiple: false,
        directory: false,
        title: `Mettre à jour la version de "${doc.title}"`,
      });
      if (selected) {
        selectedPath = Array.isArray(selected) ? selected[0] : selected;
      } else {
        // L'utilisateur a explicitement cliqué sur Annuler
        return;
      }
    } catch (dialogErr) {
      console.warn("openDialog non disponible, fallback vers l'input HTML :", dialogErr);
      promptVersionFileInput(doc);
      return;
    }

    if (selectedPath) {
      try {
        const bytes = await readFile(selectedPath);
        const name = selectedPath.split(/[\\/]/).pop() || doc.title;
        file = new File([bytes], name, { type: mimeByExt[extOf(name)] || 'application/octet-stream' });
      } catch (readErr) {
        console.warn("readFile n'a pas pu lire le fichier sélectionné, fallback vers l'input HTML :", readErr);
        promptVersionFileInput(doc);
        return;
      }
    }

    if (file) {
      await executeVersionUpload(doc, file);
    }
  } catch (error) {
    console.error('Erreur mise à jour version :', error);
    promptVersionFileInput(doc);
  }
}

function ensureAllNodesPositioned() {
  let hasMissing = false;
  for (const doc of documents.value) {
    if (!localPositions.value[doc.id] && (doc.pos_x == null || doc.pos_y == null)) {
      hasMissing = true;
      break;
    }
  }
  if (hasMissing) {
    autoLayout();
  }
}

// ---------- Ouvrir / Télécharger ----------
const preview = ref<{ url: string; title: string; kind: 'image' | 'pdf' } | null>(null);

async function typedBlob(doc: DossierDocument) {
  const blob = await docStore.fetchFileBlob(doc.id);
  if (!blob) return null;
  const type = mimeByExt[doc.extension];
  return type ? new Blob([blob], { type }) : blob;
}

async function openDocument(doc: DossierDocument) {
  const kind = iconKind(doc.extension);
  if (kind !== 'image' && doc.extension !== 'pdf') {
    return downloadDocument(doc);
  }
  const blob = await typedBlob(doc);
  if (!blob) {
    docStore.errorMessage = 'Impossible de charger le document';
    return;
  }
  closePreview();
  preview.value = {
    url: URL.createObjectURL(blob),
    title: doc.title,
    kind: kind === 'image' ? 'image' : 'pdf',
  };
}

function closePreview() {
  if (preview.value) URL.revokeObjectURL(preview.value.url);
  preview.value = null;
}

async function downloadDocument(doc: DossierDocument) {
  try {
    const target = await saveDialog({ defaultPath: doc.file_name || doc.title });
    if (!target) return;
    const blob = await docStore.fetchFileBlob(doc.id);
    if (!blob) {
      docStore.errorMessage = 'Impossible de télécharger le document';
      return;
    }
    await writeFile(target, new Uint8Array(await blob.arrayBuffer()));
  } catch (error) {
    console.error('Erreur téléchargement :', error);
    docStore.errorMessage = 'Enregistrement impossible sur le disque';
  }
}

// ---------- Renommer ----------
const renaming = ref<DossierDocument | null>(null);
const renameValue = ref('');

function openRename(doc: DossierDocument) {
  renaming.value = doc;
  renameValue.value = doc.title;
}

async function confirmRename() {
  if (!renaming.value || !renameValue.value.trim()) return;
  if (await docStore.renameDocument(renaming.value.id, renameValue.value.trim())) {
    renaming.value = null;
  }
}

// ---------- Supprimer ----------
const isDeleteOpen = ref(false);
const docToDelete = ref<DossierDocument | null>(null);
const isDeleting = ref(false);
const isDeleteSuccess = ref(false);

function openDelete(doc: DossierDocument) {
  docToDelete.value = doc;
  isDeleteSuccess.value = false;
  isDeleteOpen.value = true;
}

async function confirmDelete() {
  if (!docToDelete.value) return;
  isDeleting.value = true;
  const ok = await docStore.deleteDocument(docToDelete.value.id);
  isDeleting.value = false;
  if (ok) {
    isDeleteSuccess.value = true;
    await refreshDossier();
    setTimeout(() => {
      isDeleteOpen.value = false;
      isDeleteSuccess.value = false;
    }, 1200);
  }
}

// ---------- Chargement initial ----------
async function refreshDossier() {
  const fresh = await dossierStore.fetchDossier(affairId.value);
  if (fresh) {
    dossier.value = fresh;
    const idx = dossierStore.allDossiers.findIndex((d) => d.id === fresh.id);
    if (idx !== -1) dossierStore.allDossiers[idx] = fresh;
    if (fresh.client?.id && dossierStore.dossiersByClient[fresh.client.id]) {
      const clientIdx = dossierStore.dossiersByClient[fresh.client.id].findIndex((d) => d.id === fresh.id);
      if (clientIdx !== -1) {
        dossierStore.dossiersByClient[fresh.client.id][clientIdx] = fresh;
      }
    }
  }
}

let unlistenDrop: (() => void) | null = null;

onMounted(async () => {
  docStore.documents = [];
  docStore.errorMessage = '';
  const fresh = await dossierStore.fetchDossier(affairId.value);
  if (!fresh) {
    notFound.value = true;
    return;
  }
  dossier.value = fresh;
  await docStore.fetchDocuments(affairId.value);

  // Initialisation des positions
  for (const doc of documents.value) {
    if (doc.pos_x != null && doc.pos_y != null) {
      localPositions.value[doc.id] = { x: doc.pos_x, y: doc.pos_y };
    }
  }

  // Si aucun document n'a de position enregistrée, appliquer l'auto-layout
  const hasSavedPositions = documents.value.some((d) => d.pos_x != null && d.pos_y != null);
  if (!hasSavedPositions && documents.value.length > 0) {
    await nextTick();
    autoLayout();
  }

  // Drag & drop natif de fichiers vers le canevas
  try {
    unlistenDrop = await getCurrentWebview().onDragDropEvent((event) => {
      const payload = event.payload;
      if (payload.type === 'enter' || payload.type === 'over') isDragging.value = true;
      else if (payload.type === 'leave') isDragging.value = false;
      else if (payload.type === 'drop') {
        isDragging.value = false;
        importPaths(payload.paths);
      }
    });
  } catch (error) {
    console.error('Drag & drop indisponible :', error);
  }
});

onUnmounted(() => {
  unlistenDrop?.();
  closePreview();
  window.removeEventListener('mousemove', onViewportMouseMove);
  window.removeEventListener('mouseup', onViewportMouseUp);
  window.removeEventListener('mousemove', onNodeMouseMove);
  window.removeEventListener('mouseup', onNodeMouseUp);
});
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: #f8fafc;
}

.main-content {
  flex: 1;
  width: 100%;
  min-width: 0;
  min-height: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f1f5f9;
}

.page {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  height: 100%;
  box-sizing: border-box;
}

/* --- En-tête --- */
.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #ffffff;
  padding: 0.85rem 1.25rem;
  border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.back-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #475569;
  transition: all 0.2s;
}
.back-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.header-info {
  flex: 1;
  min-width: 0;
}
.header-line {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}
.page-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.02em;
}
.page-subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.82rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.meta-dot {
  color: #cbd5e1;
}
.meta-docs {
  color: #2563eb;
  font-weight: 600;
}

.badge {
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  background: #dbeafe;
  color: #1e40af;
}
.badge.en_cours {
  background: #dcfce7;
  color: #166534;
}
.badge.en_attente {
  background: #fef3c7;
  color: #92400e;
}
.badge.bloque,
.badge.annule {
  background: #fee2e2;
  color: #991b1b;
}
.badge.termine {
  background: #e0e7ff;
  color: #3730a3;
}
.badge.cloture {
  background: #f3f4f6;
  color: #4b5563;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* --- Contrôles Canvas --- */
.canvas-controls {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.2rem 0.35rem;
  gap: 0.25rem;
}

.ctrl-btn {
  background: transparent;
  border: none;
  border-radius: 6px;
  padding: 0.35rem 0.6rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: all 0.15s;
}
.ctrl-btn:hover {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.ctrl-btn.icon-only {
  padding: 0.35rem;
  width: 28px;
  height: 28px;
  justify-content: center;
}

.zoom-value {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  min-width: 40px;
  text-align: center;
  user-select: none;
  cursor: pointer;
}
.zoom-value:hover {
  color: #0f172a;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.55rem 1rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  border: none;
  background: #f1f5f9;
  color: #334155;
  transition: all 0.2s ease;
}
.btn:hover {
  background: #e2e8f0;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-primary {
  background: var(--primary-color, #2563eb);
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
}
.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-dark, #1d4ed8);
}

.state-text {
  text-align: center;
  color: #64748b;
  font-size: 0.95rem;
  padding: 4rem 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-banner {
  margin: 0;
  padding: 0.6rem 1rem;
  border-radius: 10px;
  background: #fef2f2;
  border: 1px solid #fee2e2;
  font-size: 0.85rem;
  color: #dc2626;
}

/* --- Zone vide --- */
.empty-zone {
  flex: 1;
  min-height: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  text-align: center;
  padding: 2.5rem;
  background: #ffffff;
  border-radius: 16px;
  border: 2px dashed #cbd5e1;
  transition: all 0.2s;
}
.empty-zone.dragging {
  border-color: #2563eb;
  background: #eff6ff;
}
.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.25rem;
}
.empty-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #1e293b;
}
.empty-text {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  color: #64748b;
  line-height: 1.5;
}

/* --- Viewport Canvas --- */
.evolution-canvas-viewport {
  flex: 1;
  position: relative;
  overflow: hidden;
  background-color: #f8fafc;
  background-image: radial-gradient(#cbd5e1 1.2px, transparent 1.2px);
  background-size: 24px 24px;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
  cursor: grab;
  user-select: none;
}
.evolution-canvas-viewport.panning {
  cursor: grabbing;
}
.evolution-canvas-viewport.dragging {
  border-color: #2563eb;
  background-color: #f0f7ff;
}

/* Légende */
.canvas-legend {
  position: absolute;
  top: 14px;
  left: 14px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.45rem 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  font-size: 0.75rem;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.legend-line {
  width: 18px;
  height: 3px;
  border-radius: 2px;
}
.legend-line.added {
  background: #3b82f6;
}
.legend-line.updated {
  background: #10b981;
}
.legend-label {
  font-weight: 600;
  color: #475569;
}
.legend-hint {
  color: #94a3b8;
  font-size: 0.72rem;
}

/* Espace transformable */
.evolution-canvas {
  position: absolute;
  top: 0;
  left: 0;
  transform-origin: 0 0;
  will-change: transform;
}

/* Calque SVG */
.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 1;
}

.link-group .link-line {
  fill: none;
  stroke: #94a3b8;
  stroke-width: 2.2;
  stroke-linecap: round;
  transition: stroke 0.2s, stroke-width 0.2s;
}
.link-group.added .link-line {
  stroke: #3b82f6;
}
.link-group.updated .link-line {
  stroke: #10b981;
}
.link-group.active .link-line {
  stroke-width: 3.5;
  filter: drop-shadow(0 2px 4px rgba(37, 99, 235, 0.3));
}

.link-badge-bg {
  fill: #ffffff;
  stroke: #e2e8f0;
  stroke-width: 1.5;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.06));
}
.link-group.added .link-badge-bg {
  stroke: #93c5fd;
}
.link-group.updated .link-badge-bg {
  stroke: #6ee7b7;
}
.link-badge-text {
  font-size: 10px;
  font-weight: 700;
  fill: #334155;
  letter-spacing: 0.02em;
}
.link-group.added .link-badge-text {
  fill: #1d4ed8;
}
.link-group.updated .link-badge-text {
  fill: #047857;
}

/* --- Nœud Document --- */
.document-node {
  position: absolute;
  width: 140px;
  height: 160px;
  background: #ffffff;
  border-radius: 16px;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
  padding: 0.75rem 0.6rem;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  text-align: center;
  cursor: grab;
  z-index: 5;
  transition: transform 0.15s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.document-node:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
  border-color: #94a3b8;
  z-index: 20;
}
.document-node.selected {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2), 0 8px 20px rgba(15, 23, 42, 0.12);
  z-index: 25;
}
.document-node.dragging {
  cursor: grabbing;
  transform: scale(1.05);
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.18);
  z-index: 30;
}

/* Badge du nœud */
.node-badge {
  position: absolute;
  top: -9px;
  right: -6px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #475569;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.12rem 0.5rem;
  border-radius: 999px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  white-space: nowrap;
}
.node-badge.updated {
  background: #ecfdf5;
  border-color: #a7f3d0;
  color: #047857;
}
.node-badge.added {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}

/* Icône du nœud */
.node-icon-wrapper {
  position: relative;
  width: 58px;
  height: 58px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 0.25rem;
  background: #f1f5f9;
  color: #475569;
  box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.6), 0 2px 6px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease;
}
.document-node:hover .node-icon-wrapper {
  transform: scale(1.08);
}

.node-icon-wrapper.pdf {
  background: #fee2e2;
  color: #dc2626;
}
.node-icon-wrapper.image {
  background: #ecfdf5;
  color: #059669;
}
.node-icon-wrapper.doc {
  background: #eff6ff;
  color: #2563eb;
}
.node-icon-wrapper.sheet {
  background: #fef3c7;
  color: #d97706;
}
.node-icon-wrapper.other {
  background: #f3e8ff;
  color: #7c3aed;
}

.node-icon {
  width: 32px;
  height: 32px;
}

.ext-tag {
  position: absolute;
  bottom: -4px;
  background: #ffffff;
  border: 1px solid currentColor;
  padding: 0 0.3rem;
  border-radius: 4px;
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.03em;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

/* Nom et métas juste en bas */
.node-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  width: 100%;
  margin-top: 0.35rem;
  min-width: 0;
}
.node-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #0f172a;
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 0.2rem;
  box-sizing: border-box;
}
.node-meta {
  font-size: 0.65rem;
  color: #94a3b8;
  font-weight: 500;
}

/* Barre d'outils du nœud */
.node-toolbar {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: rgba(248, 250, 252, 0.95);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.2rem 0.3rem;
  margin-top: 0.2rem;
  opacity: 0.25;
  transform: translateY(2px);
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.document-node:hover .node-toolbar,
.document-node.selected .node-toolbar {
  opacity: 1;
  transform: translateY(0);
}

.node-tool-btn {
  background: transparent;
  border: none;
  border-radius: 5px;
  padding: 0.25rem;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}
.node-tool-btn:hover {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}
.node-tool-btn.primary:hover {
  background: #eff6ff;
  color: #2563eb;
}
.node-tool-btn.success:hover {
  background: #ecfdf5;
  color: #059669;
}
.node-tool-btn.danger:hover {
  background: #fef2f2;
  color: #dc2626;
}

/* --- Modales --- */
.overlay-modal {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
}
.preview-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 1rem;
  width: 100%;
  max-width: 960px;
  height: 90vh;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}
.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.preview-title {
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.preview-media {
  flex: 1;
  min-height: 0;
  width: 100%;
  border: none;
  border-radius: 10px;
  object-fit: contain;
  background: #f8fafc;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
}
.close-btn:hover {
  color: #0f172a;
}

.rename-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 1.5rem;
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}
.rename-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a;
}
.rename-footer {
  display: flex;
  gap: 0.75rem;
}
.rename-footer .btn {
  flex: 1;
}
.text-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.7rem 0.9rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.9rem;
  outline: none;
  background: #f8fafc;
  color: #0f172a;
}
.text-input:focus {
  border-color: var(--primary-color, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
  background: #ffffff;
}

.hidden-file-input {
  display: none !important;
}

.btn-version-header {
  background: #ecfdf5;
  color: #047857;
  border: 1.5px solid #a7f3d0;
  box-shadow: 0 1px 3px rgba(4, 120, 87, 0.12);
  animation: pulse-version 2s infinite ease-in-out;
}
.btn-version-header:hover:not(:disabled) {
  background: #d1fae5;
  border-color: #6ee7b7;
  color: #065f46;
}
@keyframes pulse-version {
  0%, 100% {
    box-shadow: 0 1px 3px rgba(4, 120, 87, 0.12);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
  }
}

.document-node.is-updated {
  border-color: #a7f3d0;
}
.document-node.is-updated:hover {
  border-color: #34d399;
}
.document-node.is-updated.selected {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25), 0 8px 20px rgba(15, 23, 42, 0.12);
}

.size-3-5 {
  width: 0.875rem;
  height: 0.875rem;
}
.size-4 {
  width: 1rem;
  height: 1rem;
}
.size-10 {
  width: 2.5rem;
  height: 2.5rem;
}
</style>
