import { createWebHistory, createRouter } from 'vue-router'

import index from '../pages/index.vue'

const routes = [
  { path: '/', component: index, name:'index', redirect:'/dashboard'},
  { path: '/login', component:()=> import('../pages/login.vue') },
  { path: '/register', component: () => import('../pages/auth/registration.vue'), name: 'register' },
  { path: '/editor', component: ()=> import ('../pages/editorPage.vue'), name: 'editor'},

  // Dashboard
  { path: '/dashboard', component: () => import('../pages/dashboard/index.vue'), name: 'dashboard' },
  { path: '/dashboard/mySpace', component: () => import('../pages/dashboard/mySpace.vue'), name:'mySpace'}
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
