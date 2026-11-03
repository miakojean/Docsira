<template>
  <div class="pagination-container">
    <button 
      class="pagination-btn" 
      :disabled="currentPage === 1"
      @click="changePage(currentPage - 1)"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 15.75 3 12m0 0 3.75-3.75M3 12h18" />
      </svg>
    </button>

    <div class="pages-list">
      <button 
        v-for="page in totalPages" 
        :key="page"
        class="page-number"
        :class="{ active: currentPage === page }"
        @click="changePage(page)"
      >
        {{ page }}
      </button>
    </div>

    <button 
      class="pagination-btn" 
      :disabled="currentPage === totalPages"
      @click="changePage(currentPage + 1)"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M17.25 8.25 21 12m0 0-3.75 3.75M21 12H3" />
      </svg>
    </button>
  </div>
</template>

<script lang="ts">
import { computed } from 'vue'

export default {
  name: 'Paginator',
  props: {
    currentPage: {
      type: Number,
      required: true
    },
    totalCount: {
      type: Number,
      required: true
    },
    pageSize: {
      type: Number,
      default: 10
    }
  },
  emits: ['page-change'],
  setup(props, { emit }) {
    
    const totalPages = computed(() => {
      if (props.totalCount === 0) return 1;
      return Math.ceil(props.totalCount / props.pageSize);
    });

    const changePage = (page: number) => {
      if (page >= 1 && page <= totalPages.value && page !== props.currentPage) {
        emit('page-change', page);
        
        // Remonte tout en haut de l'écran en douceur
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
      }
    }

    return {
      totalPages,
      changePage
    }
  }
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin: 2rem 0;
  width: 100%;
}

.pagination-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 50px;
  height: 50px;
  font-size: 1.2rem;
  padding: 0.5rem 1rem;
  font-weight: 500;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #f7fafc;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #edf2f7;
}

.pages-list {
  display: flex;
  gap: 0.5rem;
}

.page-number {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  font-size: 0.95rem;
  font-weight: 500;
  border: 1px solid #e2e8f0;
  border-radius: 50%; /* Style rond */
  background-color: #ffffff;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-number:hover {
  background-color: var(--primary-color-dark);
  border-color: var(--primary-color-dark);
  color: #ffffff;
}

/* Style de la page active (s'accorde avec le style de ton filtre) */
.page-number.active {
  background-color: var(--primary-color-dark);
  color: #ffffff;
  border-color: var(--primary-color-dark);
}
</style>