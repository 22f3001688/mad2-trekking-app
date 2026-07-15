<template>
  <DashboardLayout>
    <div class="dashboard-layout">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Admin Control Center</p>
          <h1 class="h3 mb-1">Admin Dashboard</h1>
          <p class="text-muted mb-0">Monitor key trekking activity and platform engagement.</p>
        </div>
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-primary-subtle text-primary-emphasis px-3 py-2">
            <i class="bi bi-shield-lock me-1"></i>
            Admin
          </span>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted mb-0">Loading dashboard statistics…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        {{ error }}
      </div>

      <div v-else class="row g-4">
        <div v-for="card in cards" :key="card.key" class="col-12 col-sm-6 col-xl-4">
          <div class="card shadow-sm border-0 h-100 stat-card">
            <div class="card-body d-flex align-items-start justify-content-between">
              <div>
                <p class="text-muted mb-2 small fw-semibold text-uppercase">{{ card.label }}</p>
                <h2 class="h3 mb-0">{{ card.value }}</h2>
              </div>
              <div class="stat-icon">
                <i :class="card.icon"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script>
import DashboardLayout from '../components/DashboardLayout.vue'
import authService from '../services/auth.js'
import http from '../services/http.js'

export default {
  components: { DashboardLayout },
  name: 'AdminDashboard',
  data() {
    return {
      currentUser: authService.getCurrentUser() || {},
      loading: true,
      error: '',
      stats: {
        total_treks: 0,
        total_users: 0,
        total_staff: 0,
        total_bookings: 0,
        open_treks: 0,
        completed_treks: 0,
      },
    }
  },
  computed: {
    cards() {
      return [
        { key: 'total_treks', label: 'Total Treks', value: this.stats.total_treks, icon: 'bi bi-map' },
        { key: 'total_users', label: 'Total Users', value: this.stats.total_users, icon: 'bi bi-people' },
        { key: 'total_staff', label: 'Total Staff', value: this.stats.total_staff, icon: 'bi bi-person-badge' },
        { key: 'total_bookings', label: 'Total Bookings', value: this.stats.total_bookings, icon: 'bi bi-calendar2-check' },
        { key: 'open_treks', label: 'Open Treks', value: this.stats.open_treks, icon: 'bi bi-compass' },
        { key: 'completed_treks', label: 'Completed Treks', value: this.stats.completed_treks, icon: 'bi bi-check2-circle' },
      ]
    },
  },
  mounted() {
    this.fetchDashboardStats()
  },
  methods: {
    async fetchDashboardStats() {
      this.loading = true
      this.error = ''

      try {
        const response = await http.get('/admin/dashboard')
        if (response.data?.success) {
          this.stats = {
            ...this.stats,
            ...response.data.data,
          }
        } else {
          this.error = response.data?.message || 'Unable to load dashboard statistics.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load dashboard statistics.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.dashboard-layout {
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.stat-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(15, 23, 42, 0.1) !important;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
  font-size: 1.2rem;
}
</style>
