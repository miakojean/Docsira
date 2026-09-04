<template>
  <div class="tiptap-editor-container">
    <!-- Barre d'outils (Toolbar) : Ne s'affiche que si l'éditeur est prêt -->
    <div v-if="editor" class="toolbar">
      <button
        @click="editor.chain().focus().toggleBold().run()"
        :disabled="!editor.can().chain().focus().toggleBold().run()"
        :class="{ 'is-active': editor.isActive('bold') }"
        class="toolbar-btn"
      >
        Gras
      </button>

      <button
        @click="editor.chain().focus().toggleItalic().run()"
        :disabled="!editor.can().chain().focus().toggleItalic().run()"
        :class="{ 'is-active': editor.isActive('italic') }"
        class="toolbar-btn"
      >
        Italique
      </button>

      <button
        @click="editor.chain().focus().toggleStrike().run()"
        :disabled="!editor.can().chain().focus().toggleStrike().run()"
        :class="{ 'is-active': editor.isActive('strike') }"
        class="toolbar-btn"
      >
        Barré
      </button>

      <div class="divider"></div>

      <button
        @click="editor.chain().focus().clearNodes().run()"
        class="toolbar-btn"
      >
        Effacer le formatage
      </button>
    </div>

    <!-- Zone de saisie du texte -->
    <editor-content :editor="editor" class="editor-content-box" />
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { onBeforeUnmount } from 'vue'

// Initialisation de l'éditeur
const editor = useEditor({
  content: "<p>Je fais tourner Tiptap avec Vue.js ! 🎉</p>",
  extensions: [
    StarterKit,
  ],
})

// Bonne pratique : détruire l'instance de l'éditeur quand le composant est démonté
onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy()
  }
})
</script>

<style scoped>
/* Conteneur principal */
.tiptap-editor-container {
  border: 1px solid #d1d5db;
  border-radius: 12px;
  background-color: #ffffff;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

/* Barre d'outils */
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  align-items: center;
}

/* Boutons de la barre d'outils */
.toolbar-btn {
  background: transparent;
  border: 1px solid transparent;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toolbar-btn:hover:not(:disabled) {
  background-color: #e5e7eb;
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* État actif (quand le texte sélectionné est en gras, par exemple) */
.toolbar-btn.is-active {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.divider {
  width: 1px;
  height: 24px;
  background-color: #d1d5db;
  margin: 0 0.25rem;
}

/* Zone de l'éditeur de texte */
.editor-content-box {
  padding: 1.5rem;
  min-height: 200px;
  cursor: text;
}

/* Retirer la bordure bleue par défaut au clic (focus) sur l'éditeur */
.editor-content-box :deep(.tiptap) {
  outline: none;
}

/* Style de base pour le contenu généré par Tiptap (paragraphes, listes...) */
.editor-content-box :deep(.tiptap p) {
  margin-top: 0;
  margin-bottom: 1rem;
  line-height: 1.5;
  color: #1f2937;
}
</style>
