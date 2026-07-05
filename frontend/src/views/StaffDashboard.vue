<template>
  <DashboardLayout>
    <div class="staff-dashboard">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Staff Operations</p>
          <h1 class="h3 mb-1">Welcome back, {{ dashboard.staff_name || currentUser?.full_name || 'Staff' }}!</h1>
          <p class="text-muted mb-0">Here’s a quick overview of your assigned trekking responsibilities.</p>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted mb-0">Loading your dashboard…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else class="row g-4">
        <div class="col-12 col-md-6 col-xl-3">
          <div class="card shadow-sm border-0 h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <p class="text-muted small mb-1">Assigned Treks</p>
                  <h3 class="display-6 fw-semibold mb-0">{{ dashboard.assigned_treks }}</h3>
                </div>
                <div class="rounded-circle bg-primary-subtle text-primary d-flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                  <i class="bi bi-map fs-4"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-6 col-xl-3">
          <div class="card shadow-sm border-0 h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <p class="text-muted small mb-1">Open Treks</p>
                  <h3 class="display-6 fw-semibold mb-0">{{ dashboard.open_treks }}</h3>
                </div>
                <div class="rounded-circle bg-success-subtle text-success d-flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                  <i class="bi bi-unlock fs-4"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-6 col-xl-3">
          <div class="card shadow-sm border-0 h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <p class="text-muted small mb-1">Completed Treks</p>
                  <h3 class="display-6 fw-semibold mb-0">{{ dashboard.completed_treks }}</h3>
                </div>
                <div class="rounded-circle bg-info-subtle text-info d-flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                  <i class="bi bi-check-circle fs-4"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-6 col-xl-3">
          <div class="card shadow-sm border-0 h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <p class="text-muted small mb-1">Total Registered Trekkers</p>
                  <h3 class="display-6 fw-semibold mb-0">{{ dashboard.total_registered_trekkers }}</h3>
                </div>
                <div class="rounded-circle bg-warning-subtle text-warning d-flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                  <i class="bi bi-people fs-4"></i>
                </div>
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
import http from '../services/http.js'
import authService from '../services/auth.js'

export default {
  name: 'StaffDashboard',
  components: { DashboardLayout },
  data() {
    return {
      currentUser: authService.getCurrentUser() || {},
      dashboard: {
        staff_name: '',
        assigned_treks: 0,
        open_treks: 0,
        completed_treks: 0,
        total_registered_trekkers: 0,
      },
      loading: true,
      error: '',
    }
  },
  mounted() {
    this.fetchDashboard()
  },
  methods: {
    async fetchDashboard() {
      this.loading = true
      this.error = ''

      try {
        const response = await http.get('/staff/dashboard')
        if (response.data?.success) {
          this.dashboard = {
            ...this.dashboard,
            ...response.data.data,
          }
        } else {
          this.error = response.data?.message || 'Unable to load dashboard.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load dashboard.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.staff-dashboard {
  width: 100%;
}
</style>
