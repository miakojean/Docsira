<template>
  <div class="research-wrapper">
    <div class="flex">
        <button class="research-btn" type="button" aria-label="Search" @click="$emit('handleEvent')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
        </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResearchBar',
  emits:['handleEvent']
}
</script>

<style scoped>
.research-wrapper {
  display: inline-flex;
}

.flex {
  display: flex;
  align-items: center;
}

/* ---------- Button ---------- */
.research-btn {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color-dark);
  padding: 0.5rem;
  color: #fff;
  border: none;
  border-radius: 20%;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.research-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgb(0 0 0 / 0.15);
}
</style>
