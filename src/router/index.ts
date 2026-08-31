import { createWebHistory, createRouter } from 'vue-router'

import index from '../pages/index.vue'
import Login from '../pages/login.vue'

const routes = [
  { path: '/', component: index },
  {path: '/login', component:Login}
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})