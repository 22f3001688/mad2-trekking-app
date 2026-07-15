<template>
  <div class="admin-shell min-vh-100">
    <div class="container-fluid">
      <div class="row">
        <aside class="col-lg-3 col-xl-2 border-end bg-white min-vh-100 p-0 sidebar-shell">
          <div class="p-4 border-bottom sidebar-brand-wrap">
            <div class="d-flex align-items-center gap-2">
              <div class="rounded-circle brand-icon text-white d-flex align-items-center justify-content-center">
                <img src="/trek.webp" alt="TrekScape" class="brand-image" />
              </div>
              <div>
                <h2 class="h5 mb-0 fw-semibold">TrekScape</h2>
                <p class="small text-muted mb-0">{{ panelLabel }}</p>
              </div>
            </div>
          </div>

          <nav class="p-3">
            <ul class="list-unstyled d-grid gap-2">
              <li v-for="item in navItems" :key="item.label">
                <button
                  v-if="item.action || item.disabled"
                  class="btn w-100 text-start d-flex align-items-center gap-2"
                  :class="navButtonClass(item)"
                  :disabled="item.disabled"
                  @click="handleAction(item)"
                >
                  <i :class="item.icon" class="nav-icon"></i>
                  <span class="d-flex align-items-center gap-2">
                    {{ item.label }}
                    <span v-if="item.disabled" class="badge text-bg-light">Not Available</span>
                  </span>
                </button>
                <router-link
                  v-else
                  class="btn w-100 text-start d-flex align-items-center gap-2"
                  :class="isActive(item) ? 'btn-primary' : 'btn-outline-secondary'"
                  :to="{ name: item.routeName }"
                >
                  <i :class="item.icon" class="nav-icon"></i>
                  <span>{{ item.label }}</span>
                </router-link>
              </li>
            </ul>
          </nav>
        </aside>

        <main class="col-lg-9 col-xl-10 p-4 p-lg-5 content-shell">
          <slot />
        </main>
      </div>
    </div>
  </div>
</template>

<script>
import authService from '../services/auth.js'

export default {
  name: 'DashboardLayout',
  computed: {
    panelLabel() {
      const role = authService.getCurrentUser()?.role
      if (role === 'admin') return 'Admin Panel'
      if (role === 'staff') return 'Staff Panel'
      return 'Trekker Panel'
    },
  },
  data() {
    const currentUser = authService.getCurrentUser() || {}
    const role = currentUser.role

    return {
      navItems:
        role === 'staff'
          ? [
              { label: 'Dashboard', routeName: 'StaffDashboard', icon: 'bi bi-speedometer2' },
              { label: 'Assigned Treks', routeName: 'StaffMyTreks', icon: 'bi bi-map', matchNames: ['StaffMyTreks', 'StaffTrekParticipants'] },
              { label: 'Logout', action: 'logout', icon: 'bi bi-box-arrow-right', variant: 'danger' },
            ]
          : role === 'trekker'
            ? [
                { label: 'Dashboard', routeName: 'Dashboard', icon: 'bi bi-speedometer2' },
                { label: 'Browse Treks', routeName: 'TrekkerBrowseTreks', icon: 'bi bi-map' },
                { label: 'My Bookings', routeName: 'TrekkerMyBookings', icon: 'bi bi-calendar2-check' },
                { label: 'Trekking History', routeName: 'TrekHistory', icon: 'bi bi-clock-history' },
                { label: 'Profile', routeName: 'Profile', icon: 'bi bi-person' },
                { label: 'Logout', action: 'logout', icon: 'bi bi-box-arrow-right', variant: 'danger' },
              ]
            : [
                { label: 'Dashboard', routeName: 'AdminDashboard', icon: 'bi bi-speedometer2' },
                { label: 'Treks', routeName: 'AdminTrekIndex', icon: 'bi bi-map', matchNames: ['AdminTrekIndex', 'AdminTrekCreate', 'AdminTrekEdit'] },
                { label: 'Create Trek', routeName: 'AdminTrekCreate', icon: 'bi bi-plus-square' },
                { label: 'Staff', routeName: 'AdminStaffManagement', icon: 'bi bi-people' },
                { label: 'Bookings', routeName: 'AdminBookingHistory', icon: 'bi bi-calendar2-check' },
                { label: 'Users', routeName: 'AdminUsersSummary', icon: 'bi bi-person-lines-fill' },
                { label: 'Reports', icon: 'bi bi-bar-chart', disabled: true },
                { label: 'Logout', action: 'logout', icon: 'bi bi-box-arrow-right', variant: 'danger' },
              ],
    }
  },
  methods: {
    isActive(item) {
      if (Array.isArray(item.matchNames) && item.matchNames.length) {
        return item.matchNames.includes(this.$route.name)
      }
      return this.$route.name === item.routeName
    },
    navButtonClass(item) {
      if (item.variant === 'danger') {
        return 'btn-outline-danger'
      }
      if (item.disabled) {
        return 'btn-outline-secondary disabled-nav-btn'
      }
      return 'btn-outline-secondary'
    },
    handleAction(item) {
      if (item.action === 'logout') {
        authService.logout()
        this.$router.push({ name: 'Login' })
      }
    },
  },
}
</script>

<style scoped>
.admin-shell {
  background:
    radial-gradient(700px 260px at 0% 0%, rgba(207, 226, 255, 0.42), rgba(207, 226, 255, 0) 65%),
    linear-gradient(180deg, #f7f9fc 0%, #ffffff 100%);
}

.sidebar-shell {
  backdrop-filter: blur(4px);
}

.sidebar-brand-wrap {
  background: linear-gradient(180deg, #ffffff 0%, #fbfcfe 100%);
}

.brand-icon {
  width: 46px;
  height: 46px;
  overflow: hidden;
  border: 2px solid rgba(13, 110, 253, 0.22);
  box-shadow: 0 0.55rem 1rem rgba(13, 110, 253, 0.18);
  background: #ffffff;
}

.brand-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.nav-icon {
  width: 1.1rem;
  text-align: center;
}

.btn {
  padding: 0.72rem 0.95rem;
  border-radius: 0.85rem;
  font-weight: 500;
}

.btn-outline-secondary {
  border-color: #d3dce9;
  color: #4f6176;
  background-color: #ffffff;
}

.btn-outline-secondary:hover {
  background-color: #f2f6fc;
  border-color: #b9c8df;
  color: #2f4057;
}

.btn-primary {
  box-shadow: 0 0.55rem 1rem rgba(13, 110, 253, 0.24);
}

.content-shell {
  position: relative;
}

.disabled-nav-btn {
  opacity: 0.75;
  cursor: not-allowed;
}
</style>
