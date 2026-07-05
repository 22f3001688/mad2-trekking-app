<template>
  <DashboardLayout>
    <div class="trekker-dashboard">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Trekker Operations</p>
          <h1 class="h3 mb-1">Welcome back, {{ dashboard.user_name || currentUser?.full_name || 'Trekker' }}!</h1>
          <p class="text-muted mb-0">Here’s a quick snapshot of your trekking activity.</p>
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

      <template v-else>
        <div class="row g-4 mb-4">
          <div class="col-12 col-md-6 col-xl-3">
            <div class="card shadow-sm border-0 h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <p class="text-muted small mb-1">Available Treks</p>
                    <h3 class="display-6 fw-semibold mb-0">{{ dashboard.available_open_treks }}</h3>
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
                    <p class="text-muted small mb-1">Active Bookings</p>
                    <h3 class="display-6 fw-semibold mb-0">{{ dashboard.active_bookings }}</h3>
                  </div>
                  <div class="rounded-circle bg-success-subtle text-success d-flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                    <i class="bi bi-calendar2-check fs-4"></i>
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
                    <p class="text-muted small mb-1">Upcoming Treks</p>
                    <h3 class="display-6 fw-semibold mb-0">{{ dashboard.upcoming_treks }}</h3>
                  </div>
                  <div class="rounded-circle bg-warning-subtle text-warning d-flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                    <i class="bi bi-clock-history fs-4"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body">
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-2 mb-3">
              <div>
                <h2 class="h5 mb-1">Upcoming Trek Bookings</h2>
                <p class="text-muted mb-0">Your next five upcoming bookings are listed below.</p>
              </div>
            </div>

            <div v-if="upcomingBookings.length === 0" class="text-center py-5 text-muted">
              No upcoming bookings found.
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle mb-0">
                <thead>
                  <tr>
                    <th scope="col">Trek Name</th>
                    <th scope="col">Location</th>
                    <th scope="col">Start Date</th>
                    <th scope="col">End Date</th>
                    <th scope="col">Booking Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="booking in upcomingBookings" :key="`${booking.trek_name}-${booking.start_date}`">
                    <td class="fw-semibold">{{ booking.trek_name }}</td>
                    <td>{{ booking.location }}</td>
                    <td>{{ formatDate(booking.start_date) }}</td>
                    <td>{{ formatDate(booking.end_date) }}</td>
                    <td>
                      <span class="badge text-capitalize" :class="bookingStatusBadgeClass(booking.booking_status)">
                        {{ booking.booking_status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </template>
    </div>
  </DashboardLayout>
</template>

<script>
import DashboardLayout from '../components/DashboardLayout.vue'
import http from '../services/http.js'
import authService from '../services/auth.js'

export default {
  name: 'Dashboard',
  components: { DashboardLayout },
  data() {
    return {
      currentUser: authService.getCurrentUser() || {},
      dashboard: {
        user_name: '',
        available_open_treks: 0,
        active_bookings: 0,
        completed_treks: 0,
        upcoming_treks: 0,
      },
      upcomingBookings: [],
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
        const response = await http.get('/trekker/dashboard')
        if (response.data?.success) {
          this.dashboard = {
            ...this.dashboard,
            ...response.data.data,
          }
          this.upcomingBookings = response.data.data?.upcoming_bookings || []
        } else {
          this.error = response.data?.message || 'Unable to load your dashboard.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load your dashboard.'
      } finally {
        this.loading = false
      }
    },
    formatDate(value) {
      if (!value) {
        return '—'
      }

      const date = new Date(value)
      if (Number.isNaN(date.getTime())) {
        return value
      }

      return date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    },
    bookingStatusBadgeClass(status) {
      switch (status) {
        case 'booked':
          return 'bg-success-subtle text-success-emphasis'
        case 'cancelled':
          return 'bg-secondary-subtle text-secondary-emphasis'
        default:
          return 'bg-warning-subtle text-warning-emphasis'
      }
    },
  },
}
</script>

<style scoped>
.trekker-dashboard {
  width: 100%;
}
</style>
