import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import StaffDashboard from '../views/StaffDashboard.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import authService from '../services/auth.js'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login, meta: { guest: true } },
  { path: '/register', name: 'Register', component: Register, meta: { guest: true } },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/staff/dashboard', name: 'StaffDashboard', component: StaffDashboard, meta: { requiresAuth: true, role: 'staff' } },
  { path: '/admin/dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authenticated = authService.isAuthenticated()
  const user = authService.getCurrentUser()

  if (to.meta.requiresAuth && !authenticated) {
    return next({ name: 'Login' })
  }

  if (to.meta.guest && authenticated) {
    if (user.role === 'admin') {
      return next({ name: 'AdminDashboard' })
    }
    if (user.role === 'staff') {
      return next({ name: 'StaffDashboard' })
    }
    return next({ name: 'Dashboard' })
  }

  if (to.meta.role && user?.role !== to.meta.role) {
    if (!authenticated) {
      return next({ name: 'Login' })
    }
    return next({ name: user.role === 'admin' ? 'AdminDashboard' : user.role === 'staff' ? 'StaffDashboard' : 'Dashboard' })
  }

  return next()
})

export default router
