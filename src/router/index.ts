import { createWebHistory, createRouter, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { getStoredAuthToken, setUnauthorizedHandler } from '../services/api'

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'index', redirect: '/dashboard' },

  // Auth
  { path: '/login', component: () => import('../pages/auth/login.vue'), name: 'login', meta: { public: true } },
  { path: '/register', component: () => import('../pages/auth/registration.vue'), name: 'register', meta: { public: true } },
  { path: '/editor', component: () => import('../pages/editorPage.vue'), name: 'editor', meta: { requiresAuth: true } },
  { path: '/auth-code', component: () => import('../pages/auth/code.vue'), name: 'authCode', meta: { public: true } },

  // Dashboard
  { path: '/dashboard', component: () => import('../pages/dashboard/index.vue'), name: 'dashboard', meta: { requiresAuth: true } },
  { path: '/dashboard/affairs', component: () => import('../pages/dashboard/affairs.vue'), name: 'workspace', meta: { requiresAuth: true } },
  { path: '/dashboard/affairs/:id', component: () => import('../pages/dashboard/affairDetail.vue'), name: 'affairDetail', meta: { requiresAuth: true } },
  { path: '/dashboard/mySpace', component: () => import('../pages/dashboard/mySpace.vue'), name: 'mySpace', meta: { requiresAuth: true } },
  { path: '/dashboard/mySpace/:folderPath', component: () => import('../pages/dashboard/mySpaceFolder.vue'), name: 'mySpaceFolder', meta: { requiresAuth: true } },
  { path: '/dashboard/settings', component: () => import('../pages/dashboard/settings.vue'), name: 'settings', meta: { requiresAuth: true } },
  { path: '/dashboard/settings/collaborators', component: () => import('../pages/dashboard/settings/collaborators.vue'), name: 'collaborators', meta: { requiresAuth: true } },
  { path: '/dashboard/Customer', component: () => import('../pages/dashboard/customers/customers.vue'), name: 'customers', meta: { requiresAuth: true } },
  { path: '/dashboard/Customer/trash', component: () => import('../pages/dashboard/customers/trash.vue'), name: 'trash', meta: { requiresAuth: true } },
  { path: '/dashboard/archives', alias: ['/dashboard/Archives'], component: () => import('../pages/dashboard/archives.vue'), name: 'archives', meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

let isUnauthorizedHandlerBound = false

function ensureUnauthorizedHandler(authStore: ReturnType<typeof useAuthStore>) {
  if (isUnauthorizedHandlerBound) return
  isUnauthorizedHandlerBound = true
  setUnauthorizedHandler(() => {
    authStore.resetLocalAuthState()
    const current = router.currentRoute.value
    if (!current.meta?.public) {
      void router.replace({ path: '/login', query: { redirect: current.fullPath } })
    }
  })
}

router.beforeEach(async (to, from) => {
  try {
    const authStore = useAuthStore()
    ensureUnauthorizedHandler(authStore)

    if (to.path !== from.path) {
      authStore.clearMessages()
    }

    if (!authStore.isHydrated) {
      await authStore.hydrateSession()
    }

    const hasAuth = authStore.isAuthenticated || Boolean(await getStoredAuthToken())

    if (to.meta.requiresAuth && !hasAuth) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }

    if ((to.path === '/login' || to.path === '/register') && hasAuth) {
      return { path: '/dashboard' }
    }
  } catch {
    if (to.meta.requiresAuth) {
      return { path: '/login' }
    }
  }
})
