import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AppLayout from '@/components/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'introduction',
          component: () => import('../views/IntroductionView.vue')
        },
        {
          path: '/mapping',
          name: 'mapping',
          component: () => import('../views/MappingView.vue')
        },
        {
          path: '/config',
          name: 'config',
          component: () => import('../views/ConfigView.vue')
        },
        {
          path: '/admin',
          name: 'admin',
          component: () => import('../views/AdminView.vue'),
          meta: { requiresAdmin: true }
        }
      ]
    }
  ],
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // Initialize auth on first load
  if (!userStore.currentUser) {
    userStore.initializeAuth()
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  
  if (requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if (requiresGuest && userStore.isAuthenticated) {
    next('/')
  } else if (requiresAdmin && !userStore.isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router
