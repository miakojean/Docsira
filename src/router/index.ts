import { createWebHistory, createRouter, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'index', redirect: '/dashboard' },
  { path: '/login', component: () => import('../pages/auth/login.vue') },
  { path: '/register', component: () => import('../pages/auth/registration.vue'), name: 'register' },
  { path: '/editor', component: () => import('../pages/editorPage.vue'), name: 'editor' },

  // Dashboard
  { path: '/dashboard', component: () => import('../pages/dashboard/index.vue'), name: 'dashboard' },
  { path: '/dashboard/mySpace', component: () => import('../pages/dashboard/mySpace.vue'), name: 'mySpace' },
  { path: '/dashboard/mySpace/:folderPath', component: () => import('../pages/dashboard/mySpaceFolder.vue') },
  { path: '/dashboard/settings', component: () => import('../pages/dashboard/settings.vue'), name: 'settings' },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
