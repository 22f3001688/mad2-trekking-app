<template>
  <DashboardLayout>
    <div class="admin-booking-history-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Admin Operations</p>
          <h1 class="h3 mb-1">Booking History</h1>
          <p class="text-muted mb-0">Review completed and cancelled bookings across all trekkers.</p>
        </div>
        <router-link class="btn btn-outline-secondary" :to="{ name: 'AdminDashboard' }">
          <i class="bi bi-arrow-left me-1"></i>
          Back to Dashboard
        </router-link>
      </div>

      <div class="card shadow-sm border-0 mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-end">
            <div class="col-12 col-md-8">
              <label class="form-label small text-muted">Search</label>
              <input v-model.trim="filters.search" class="form-control" placeholder="Search trek, trekker, or email" @input="fetchHistory" />
            </div>
            <div class="col-12 col-md-4">
              <label class="form-label small text-muted">Status</label>
              <select v-model="filters.status" class="form-select" @change="fetchHistory">
                <option value="historical">Completed and Cancelled</option>
                <option value="completed">Completed only</option>
                <option value="cancelled">Cancelled only</option>
                <option value="booked">Booked only</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status" aria-hidden="true"></div>
        <p class="text-muted mb-0">Loading booking history…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else-if="history.length === 0" class="card shadow-sm border-0">
        <div class="card-body text-center py-5 text-muted">
          No booking history found.
        </div>
      </div>

      <div v-else class="card shadow-sm border-0">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table align-middle mb-0">
              <thead>
                <tr>
                  <th scope="col">Booking ID</th>
                  <th scope="col">Trekker</th>
                  <th scope="col">Trek</th>
                  <th scope="col">Location</th>
                  <th scope="col">Booking Date</th>
                  <th scope="col">Booking Status</th>
                  <th scope="col">Trek Status</th>
                  <th scope="col">Payment Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="entry in history" :key="entry.booking_id">
                  <td class="fw-semibold">{{ entry.booking_id }}</td>
                  <td>
                    <div class="fw-semibold">{{ entry.user?.full_name || '—' }}</div>
                    <div class="small text-muted">{{ entry.user?.email || '—' }}</div>
                  </td>
                  <td>{{ entry.trek?.trek_name || '—' }}</td>
                  <td>{{ entry.trek?.location || '—' }}</td>
                  <td>{{ formatDateTime(entry.booking_date) }}</td>
                  <td>
                    <span class="badge text-capitalize" :class="bookingBadgeClass(entry.booking_status)">{{ entry.booking_status }}</span>
                  </td>
                  <td>
                    <span class="badge text-capitalize" :class="trekBadgeClass(entry.trek?.status)">{{ entry.trek?.status }}</span>
                  </td>
                  <td>
                    <span class="badge text-capitalize" :class="paymentBadgeClass(entry.payment_status)">{{ entry.payment_status }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script>
import DashboardLayout from '../components/DashboardLayout.vue'
import http from '../services/http.js'

export default {
  name: 'AdminBookingHistory',
  components: { DashboardLayout },
  data() {
    return {
      loading: true,
      error: '',
      history: [],
      filters: {
        search: '',
        status: 'historical',
      },
    }
  },
  mounted() {
    this.fetchHistory()
  },
  methods: {
    async fetchHistory() {
      this.loading = true
      this.error = ''

      try {
        const params = new URLSearchParams()
        if (this.filters.search) params.append('search', this.filters.search)
        if (this.filters.status) params.append('status', this.filters.status)

        const response = await http.get(`/admin/bookings/history?${params.toString()}`)
        if (response.data?.success) {
          this.history = response.data.data || []
        } else {
          this.error = response.data?.message || 'Unable to load booking history.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load booking history.'
      } finally {
        this.loading = false
      }
    },
    formatDateTime(value) {
      if (!value) return '—'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return date.toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    },
    bookingBadgeClass(status) {
      switch ((status || '').toLowerCase()) {
        case 'completed':
          return 'bg-primary-subtle text-primary-emphasis'
        case 'cancelled':
          return 'bg-secondary-subtle text-secondary-emphasis'
        case 'booked':
          return 'bg-success-subtle text-success-emphasis'
        default:
          return 'bg-warning-subtle text-warning-emphasis'
      }
    },
    trekBadgeClass(status) {
      switch ((status || '').toLowerCase()) {
        case 'completed':
          return 'bg-primary-subtle text-primary-emphasis'
        case 'open':
          return 'bg-success-subtle text-success-emphasis'
        case 'closed':
          return 'bg-secondary-subtle text-secondary-emphasis'
        default:
          return 'bg-warning-subtle text-warning-emphasis'
      }
    },
    paymentBadgeClass(status) {
      switch ((status || '').toLowerCase()) {
        case 'not_applicable':
          return 'bg-light text-dark'
        case 'paid':
          return 'bg-success-subtle text-success-emphasis'
        case 'refunded':
          return 'bg-info-subtle text-info-emphasis'
        case 'failed':
          return 'bg-danger-subtle text-danger-emphasis'
        default:
          return 'bg-warning-subtle text-warning-emphasis'
      }
    },
  },
}
</script>

<style scoped>
.admin-booking-history-page {
  width: 100%;
}
</style>
