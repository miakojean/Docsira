import { createWebHistory, createRouter } from 'vue-router'

import index from '../pages/index.vue'
import Login from '../pages/login.vue'

const routes = [
  { path: '/', component: index },
  { path: '/login', component: Login },
  { path: '/register', component: ()=> import('../pages/auth/registration.vue'), name:'register'}
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
