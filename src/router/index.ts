import { createWebHistory, createRouter } from 'vue-router'

import index from '../pages/index.vue'

const routes = [
  { path: '/', component: index },
  { path: '/login', component:()=> import('../pages/login.vue') },
  { path: '/register', component: () => import('../pages/auth/registration.vue'), name: 'register' },
  { path: '/editor', component: ()=> import ('../pages/editorPage.vue'), name: 'editor'}
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
