<template>
  <div class="main-container">
    <textEditor />
  </div>
</template>

<script>
import textEditor from '../components/tools/textEditor.vue';

  export default {
    name: 'App',
    components: {
      textEditor,
    },
  }
</script>
