<template>
    <Teleport to="body">
        <transition name="modal-fade" :duration="300">
            <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
                
                <div class="modal-card" role="dialog">
                    
                    <!-- Top Bar -->
                    <div class="modal-top-bar">
                        <h3 class="preview-title">Détails du document</h3>
                        <button class="close-btn" @click="closeModal" aria-label="Fermer la modale">
                            &times;
                        </button>
                    </div>

                    <!-- Fichier Info (Icône, Nom, Taille) -->
                    <div class="file-identity">
                        <div class="icon-wrapper flex items-center justify-center">
                            <!-- 1. PDF -->
                            <svg v-if="fileKind === 'pdf'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-pdf">
                                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                                <path d="M5 12v-7a2 2 0 0 1 2 -2h7l5 5v4" />
                                <path d="M5 18h1.5a1.5 1.5 0 0 0 0 -3h-1.5v6" />
                                <path d="M17 18h2" />
                                <path d="M20 15h-3v6" />
                                <path d="M11 15v6h1a2 2 0 0 0 2 -2v-2a2 2 0 0 0 -2 -2h-1" />
                            </svg>

                            <!-- 2. WORD -->
                            <svg v-else-if="fileKind === 'word'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-word">
                                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                                <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
                                <path d="M9 12l1.5 6l1.5 -4l1.5 4l1.5 -6" />
                            </svg>

                            <!-- 3. EXCEL / CSV -->
                            <svg v-else-if="fileKind === 'excel'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-excel">
                                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                                <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
                                <path d="M10 12l4 6" />
                                <path d="M10 18l4 -6" />
                            </svg>

                            <!-- 4. IMAGE -->
                            <svg v-else-if="fileKind === 'image'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-image">
                                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                <path d="M15 8h.01" />
                                <path d="M3 6a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v12a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3v-12z" />
                                <path d="M3 16l5 -5c.928 -.893 2.072 -.893 3 0l5 5" />
                                <path d="M14 14l1 -1c.617 -.593 1.328 -.793 2.009 -.6" />
                            </svg>

                            <!-- 5. AUTRE -->
                            <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="icon icon-other">
                                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                                <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
                            </svg>
                        </div>
                        
                        <h2 class="file-name">{{ displayName }}</h2>
                        <span class="file-meta">{{ formattedSize }}</span>
                    </div>

                    <div class="divider"></div>

                    <!-- Métadonnées issues du document sélectionné -->
                    <div class="file-section">
                      <h4>Informations</h4>
                      <dl class="file-metadata">
                        <div><dt>Ajouté le</dt><dd>{{ uploadedAt }}</dd></div>
                        <div><dt>Type</dt><dd>{{ file.extension || 'Inconnu' }}</dd></div>
                        <div><dt>Version</dt><dd>v{{ file.version || 1 }}</dd></div>
                        <div v-if="folderName"><dt>Dossier</dt><dd>{{ folderName }}</dd></div>
                      </dl>
                    </div>

                    <div class="divider"></div>

                    <!-- Partagé avec -->
                    <div class="file-section">
                        <h4>Accès</h4>
                        <p class="description-text">Les accès sont gérés au niveau du cabinet, pas individuellement pour ce document.</p>
                    </div>

                    <div class="divider"></div>

                    <!-- Actions (Share, Edit, Delete) -->
                    <div class="file-actions">
                        <button class="action-btn" @click="$emit('share')">
                            <div class="action-icon bg-blue-light">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="20" height="20">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                                </svg>
                            </div>
                            <span>Collaborateurs</span>
                        </button>

                          <button class="action-btn" @click="$emit('download')">
                            <div class="action-icon bg-blue-light">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v12m0 0l4-4m-4 4l-4-4M5 17v3h14v-3" />
                                </svg>
                            </div>
                            <span>Télécharger</span>
                          </button>

                          <button class="action-btn" @click="$emit('edit')">
                            <div class="action-icon bg-blue-light">
                              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                              </svg>
                            </div>
                            <span>Renommer</span>
                        </button>

                        <button class="action-btn" @click="$emit('delete')">
                            <div class="action-icon bg-red-light">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="20" height="20">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </div>
                            <span>Supprimer</span>
                        </button>
                    </div>

                </div>
            </div>
        </transition>
    </Teleport>
</template>

<script lang="ts">
import { computed } from 'vue'

type FileKind =
  | 'pdf' | 'word' | 'excel' | 'image'
  | 'text' | 'video' | 'audio' | 'archive'
  | 'code' | 'other'

export default {
    props: {
        isOpen: {
            type: Boolean,
            default: true
        },
        file: {
            type: Object,
            default: () => ({})
        },
        folderName: {
            type: String,
            default: ''
        }
    },
    emits: ['close', 'share', 'download', 'edit', 'delete'],
    setup(props, { emit }) {

        const closeModal = () => {
            emit('close')
        }

        const KIND_BY_EXT: Record<string, FileKind> = {
            pdf: 'pdf',
            doc: 'word', docx: 'word', rtf: 'word', odt: 'word', pages: 'word',
            xls: 'excel', xlsx: 'excel', csv: 'excel', ods: 'excel', numbers: 'excel',
            png: 'image', jpg: 'image', jpeg: 'image', webp: 'image', gif: 'image', svg: 'image', bmp: 'image', ico: 'image',
            txt: 'text', md: 'text', log: 'text',
            mp4: 'video', mov: 'video', avi: 'video', mkv: 'video', webm: 'video',
            mp3: 'audio', wav: 'audio', ogg: 'audio', flac: 'audio', m4a: 'audio',
            zip: 'archive', rar: 'archive', '7z': 'archive', tar: 'archive', gz: 'archive',
            js: 'code', ts: 'code', vue: 'code', html: 'code', css: 'code', json: 'code', py: 'code', java: 'code', php: 'code', xml: 'code',
        }

        const fileKind = computed<FileKind>(() => {
            const raw = props.file?.extension
            if (typeof raw !== 'string') return 'other'

            const ext = raw.trim().replace(/^\./, '').toLowerCase()
            return KIND_BY_EXT[ext] ?? 'other'
        })

        const displayName = computed(() => props.file?.title || props.file?.file_name || 'Document sans nom')
        const formattedSize = computed(() => {
            const size = Number(props.file?.size)
            if (!Number.isFinite(size) || size <= 0) return 'Taille inconnue'
            if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} Ko`
            return `${(size / (1024 * 1024)).toFixed(1)} Mo`
        })
        const uploadedAt = computed(() => {
            if (!props.file?.uploaded_at) return 'Date inconnue'
            const date = new Date(props.file.uploaded_at)
            return Number.isNaN(date.getTime())
              ? 'Date inconnue'
              : date.toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' })
        })

        return {
            closeModal,
            fileKind,
            displayName,
            formattedSize,
            uploadedAt
        }
    }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: flex-end; /* Aligné sur la droite comme un panneau latéral */
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.42);
}

.modal-card {
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 400px; /* Réduit pour imiter le volet de droite */
  height: 100%;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.modal-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
}

.file-identity {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.5rem;
}

.icon-wrapper {
  background: #f9f8f8;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 0.5rem;
}

.icon-wrapper svg {
  width: 64px;
  height: 64px;
}

.file-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #222;
  margin: 0;
  line-height: 1.3;
}

.file-meta {
  font-size: 0.85rem;
  color: #888;
}

.divider {
  height: 1px;
  background-color: #eee;
  width: 100%;
}

.file-section h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.75rem;
}

.description-text {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.5;
}

.file-metadata {
  display: grid;
  gap: 0.6rem;
  margin: 0;
  font-size: 0.85rem;
}

.file-metadata > div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.file-metadata dt {
  color: #888;
}

.file-metadata dd {
  margin: 0;
  color: #444;
  text-align: right;
  overflow-wrap: anywhere;
}

.file-actions {
  display: flex;
  justify-content: space-around;
  margin-top: auto;
  padding-top: 1rem;
}

.action-btn {
  background: transparent;
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.bg-blue-light { background-color: #e3f2fd; color: #1e88e5; }
.bg-red-light { background-color: #ffebee; color: #e53935; }

.action-btn span {
  font-size: 0.8rem;
  font-weight: 500;
  color: #555;
}

/* Couleurs des icônes SVG */
.icon-pdf   { color: #e53935; }
.icon-word  { color: #1e88e5; }
.icon-excel { color: #43a047; }
.icon-image { color: #8e24aa; }
.icon-other { color: #757575; }
</style>