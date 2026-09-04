<template>
  <div class="tiptap-editor-container">
    <!-- Barre d'outils fixe en haut -->
    <div v-if="editor" class="toolbar">
      <!-- Groupe : Historique -->
      <button @click="editor.chain().focus().undo().run()" :disabled="!editor.can().chain().focus().undo().run()" class="toolbar-btn" title="Annuler">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3" /></svg>
      </button>
      <button @click="editor.chain().focus().redo().run()" :disabled="!editor.can().chain().focus().redo().run()" class="toolbar-btn" title="Refaire">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5"><path stroke-linecap="round" stroke-linejoin="round" d="M15 15l6-6m0 0l-6-6m6 6H9a6 6 0 000 12h3" /></svg>
      </button>

      <div class="divider"></div>

      <!-- Groupe : Titres -->
      <button @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }" class="toolbar-btn">H1</button>
      <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }" class="toolbar-btn">H2</button>
      <button @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }" class="toolbar-btn">H3</button>

      <div class="divider"></div>

      <!-- Groupe : Formatage de base -->
      <button @click="editor.chain().focus().toggleBold().run()" :disabled="!editor.can().chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }" class="toolbar-btn" title="Gras">
        <strong>G</strong>
      </button>
      <button @click="editor.chain().focus().toggleItalic().run()" :disabled="!editor.can().chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }" class="toolbar-btn" title="Italique">
        <em>I</em>
      </button>
      <button @click="editor.chain().focus().toggleStrike().run()" :disabled="!editor.can().chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }" class="toolbar-btn" title="Barré">
        <s>S</s>
      </button>

      <div class="divider"></div>

      <!-- Groupe : Listes et Citations -->
      <button @click="editor.chain().focus().toggleBulletList().run()" :class="{ 'is-active': editor.isActive('bulletList') }" class="toolbar-btn" title="Liste à puces">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zM3.75 12h.007v.008H3.75V12zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm-.375 5.25h.007v.008H3.75v-.008zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" /></svg>
      </button>
      <button @click="editor.chain().focus().toggleOrderedList().run()" :class="{ 'is-active': editor.isActive('orderedList') }" class="toolbar-btn" title="Liste numérotée">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zM3.75 12h.007v.008H3.75V12zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm-.375 5.25h.007v.008H3.75v-.008zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" /></svg>
      </button>
      <button @click="editor.chain().focus().toggleBlockquote().run()" :class="{ 'is-active': editor.isActive('blockquote') }" class="toolbar-btn" title="Citation">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 20.25c4.97 0 9-3.694 9-8.25s-4.03-8.25-9-8.25S3 7.444 3 12c0 2.104.859 4.023 2.273 5.48.432.447.74 1.04.586 1.641a4.483 4.483 0 01-.923 1.785A5.969 5.969 0 006 21c1.282 0 2.47-.402 3.445-1.087.81.22 1.668.337 2.555.337z" /></svg>
      </button>

      <div class="divider"></div>

      <!-- Groupe : Nettoyage -->
      <button @click="editor.chain().focus().clearNodes().unsetAllMarks().run()" class="toolbar-btn" title="Effacer le formatage">
        Effacer
      </button>
    </div>

    <!-- Zone de la "Page Word" -->
    <div class="page-container">
      <editor-content :editor="editor" class="editor-content-box" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Heading from '@tiptap/extension-heading'
import { onBeforeUnmount } from 'vue'

const editor = useEditor({
  content: `
    <h1>Titre de mon document</h1>
    <p>Commencez à rédiger votre contenu ici. Vous avez l'impression d'être dans Word !</p>
    <ul>
      <li>Élément 1</li>
      <li>Élément 2</li>
    </ul>
    <blockquote>Voici une belle citation pour illustrer Tiptap.</blockquote>
  `,
  extensions: [
    StarterKit,
    Heading.configure({
      levels: [1, 2, 3],
    }),
  ],
})

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy()
  }
})
</script>

<style scoped>
/* Conteneur principal (prend la hauteur de l'écran ou du parent) */
.tiptap-editor-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 800px; /* À adapter selon vos besoins */
  background-color: #f3f4f6; /* Fond gris pour faire ressortir la page blanche */
  border: 1px solid #d1d5db;
  border-radius: 8px;
  overflow: hidden;
}

/* Barre d'outils fixe en haut */
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  align-items: center;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid transparent;
  padding: 0.4rem;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 32px;
  min-height: 32px;
}

.toolbar-btn.size-5 { width: 20px; height: 20px; }

.toolbar-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.toolbar-btn.is-active {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.divider {
  width: 1px;
  height: 20px;
  background-color: #d1d5db;
  margin: 0 0.5rem;
}

/* Zone contenant la page (avec scroll) */
.page-container {
  flex: 1;
  overflow-y: auto;
  padding: 4rem 1rem;
  display: flex;
  justify-content: center; /* Centre la page au milieu */
}

/* L'effet "Feuille A4 Word" */
.editor-content-box {
  width: 100%;
  max-width: 210mm; /* Largeur standard A4 */
  min-height: 297mm; /* Hauteur standard A4 */
  background-color: #ffffff;
  padding: 2.5rem 3rem; /* Marges intérieures comme un vrai document */
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  cursor: text;
}

/* Retirer la bordure bleue par défaut au focus */
.editor-content-box :deep(.tiptap) {
  outline: none;
  min-height: 100%;
}

/* Styliser le texte à l'intérieur de l'éditeur */
.editor-content-box :deep(.tiptap p) {
  margin-top: 0;
  margin-bottom: 1rem;
  line-height: 1.6;
  color: #374151;
}

.editor-content-box :deep(.tiptap h1) { font-size: 2rem; margin-bottom: 1rem; }
.editor-content-box :deep(.tiptap h2) { font-size: 1.5rem; margin-bottom: 0.75rem; }
.editor-content-box :deep(.tiptap h3) { font-size: 1.25rem; margin-bottom: 0.5rem; }

.editor-content-box :deep(.tiptap ul),
.editor-content-box :deep(.tiptap ol) {
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

.editor-content-box :deep(.tiptap blockquote) {
  border-left: 4px solid #d1d5db;
  padding-left: 1rem;
  margin-left: 0;
  font-style: italic;
  color: #6b7280;
}
</style>
