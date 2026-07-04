import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import StaffDashboard from '../views/StaffDashboard.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import AdminStaffManagement from '../views/AdminStaffManagement.vue'
import AdminTrekCreate from '../views/AdminTrekCreate.vue'
import AdminTrekEdit from '../views/AdminTrekEdit.vue'
import AdminTrekList from '../views/AdminTrekList.vue'
import authService from '../services/auth.js'

export function getDashboardRouteForRole(role) {
  if (role === 'admin') {
    return { name: 'AdminDashboard' }
  }
  if (role === 'staff') {
    return { name: 'StaffDashboard' }
  }
  return { name: 'Dashboard' }
}

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login, meta: { guest: true } },
  { path: '/register', name: 'Register', component: Register, meta: { guest: true } },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/staff/dashboard', name: 'StaffDashboard', component: StaffDashboard, meta: { requiresAuth: true, role: 'staff' } },
  { path: '/admin/dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/treks', name: 'AdminTrekIndex', component: AdminTrekList, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/treks/new', name: 'AdminTrekCreate', component: AdminTrekCreate, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/treks/:id/edit', name: 'AdminTrekEdit', component: AdminTrekEdit, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/treks/view', name: 'AdminTrekView', component: AdminTrekList, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/treks/delete', name: 'AdminTrekDelete', component: AdminTrekList, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/treks/assign', name: 'AdminTrekAssign', component: AdminTrekList, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/staff', name: 'AdminStaffManagement', component: AdminStaffManagement, meta: { requiresAuth: true, role: 'admin' } },
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
    return next(getDashboardRouteForRole(user?.role))
  }

  if (to.meta.role && user?.role !== to.meta.role) {
    if (!authenticated) {
      return next({ name: 'Login' })
    }
    return next(getDashboardRouteForRole(user?.role))
  }

  return next()
})

export default router
