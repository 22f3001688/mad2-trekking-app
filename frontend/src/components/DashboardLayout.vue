<template>
  <div class="admin-shell min-vh-100 bg-light">
    <div class="container-fluid">
      <div class="row">
        <aside class="col-lg-3 col-xl-2 border-end bg-white min-vh-100 p-0">
          <div class="p-4 border-bottom">
            <div class="d-flex align-items-center gap-2">
              <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width: 42px; height: 42px;">
                <i class="bi bi-compass"></i>
              </div>
              <div>
                <h2 class="h6 mb-0">TrekScape</h2>
                <p class="small text-muted mb-0">Admin Panel</p>
              </div>
            </div>
          </div>

          <nav class="p-3">
            <ul class="list-unstyled d-grid gap-2">
              <li v-for="item in navItems" :key="item.label">
                <button
                  v-if="item.action"
                  class="btn w-100 text-start d-flex align-items-center gap-2"
                  :class="item.variant === 'danger' ? 'btn-outline-danger' : 'btn-outline-secondary'"
                  @click="handleAction(item)"
                >
                  <i :class="item.icon"></i>
                  <span>{{ item.label }}</span>
                </button>
                <router-link
                  v-else
                  class="btn w-100 text-start d-flex align-items-center gap-2"
                  :class="isActive(item.routeName) ? 'btn-primary' : 'btn-outline-secondary'"
                  :to="item.routeName ? { name: item.routeName } : '#'
"
                >
                  <i :class="item.icon"></i>
                  <span>{{ item.label }}</span>
                </router-link>
              </li>
            </ul>
          </nav>
        </aside>

        <main class="col-lg-9 col-xl-10 p-4 p-lg-5">
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
  data() {
    const currentUser = authService.getCurrentUser() || {}
    const role = currentUser.role

    return {
      navItems:
        role === 'staff'
          ? [
              { label: 'Dashboard', routeName: 'StaffDashboard', icon: 'bi bi-speedometer2' },
              { label: 'Assigned Treks', routeName: 'StaffMyTreks', icon: 'bi bi-map' },
              { label: 'Participants', routeName: 'StaffTrekParticipants', icon: 'bi bi-people', disabled: true },
              { label: 'Logout', action: 'logout', icon: 'bi bi-box-arrow-right', variant: 'danger' },
            ]
          : role === 'trekker'
            ? [
                { label: 'Dashboard', routeName: 'Dashboard', icon: 'bi bi-speedometer2' },
                { label: 'Browse Treks', routeName: 'TrekkerBrowseTreks', icon: 'bi bi-map' },
                { label: 'My Bookings', routeName: 'TrekkerMyBookings', icon: 'bi bi-calendar2-check' },
                { label: 'History', routeName: 'TrekHistory', icon: 'bi bi-clock-history' },
                { label: 'Profile', routeName: 'Profile', icon: 'bi bi-person' },
                { label: 'Logout', action: 'logout', icon: 'bi bi-box-arrow-right', variant: 'danger' },
              ]
            : [
                { label: 'Dashboard', routeName: 'AdminDashboard', icon: 'bi bi-speedometer2' },
                { label: 'Treks', routeName: 'AdminTrekIndex', icon: 'bi bi-map' },
                { label: 'Staff', routeName: 'AdminStaffManagement', icon: 'bi bi-people' },
                { label: 'Users', icon: 'bi bi-person-lines-fill', disabled: true },
                { label: 'Bookings', icon: 'bi bi-calendar2-check', disabled: true },
                { label: 'Reports', icon: 'bi bi-bar-chart', disabled: true },
                { label: 'Logout', action: 'logout', icon: 'bi bi-box-arrow-right', variant: 'danger' },
              ],
    }
  },
  methods: {
    isActive(routeName) {
      return this.$route.name === routeName
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
