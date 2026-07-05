<template>
  <DashboardLayout>
    <div class="trek-history-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Trekker Operations</p>
          <h1 class="h3 mb-1">Trekking History</h1>
          <p class="text-muted mb-0">Completed and cancelled bookings are listed here.</p>
        </div>
        <router-link class="btn btn-outline-secondary" :to="{ name: 'TrekkerMyBookings' }">
          <i class="bi bi-calendar2-check me-1"></i>
          Back to My Bookings
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status" aria-hidden="true"></div>
        <p class="text-muted mb-0">Loading history…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else-if="history.length === 0" class="card shadow-sm border-0">
        <div class="card-body text-center py-5">
          <div class="empty-icon rounded-circle bg-light text-muted d-inline-flex align-items-center justify-content-center mb-3">
            <i class="bi bi-clock-history fs-3"></i>
          </div>
          <h2 class="h5 mb-2">No history found</h2>
          <p class="text-muted mb-0">Completed and cancelled bookings will appear here.</p>
        </div>
      </div>

      <div v-else class="card shadow-sm border-0">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table align-middle mb-0">
              <thead>
                <tr>
                  <th scope="col">Trek Name</th>
                  <th scope="col">Location</th>
                  <th scope="col">Dates</th>
                  <th scope="col">Final Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="entry in history" :key="entry.id">
                  <td class="fw-semibold">{{ entry.trek_name }}</td>
                  <td>{{ entry.location }}</td>
                  <td>{{ formatDates(entry.start_date, entry.end_date) }}</td>
                  <td>
                    <span class="badge text-capitalize" :class="statusBadgeClass(entry.final_status)">{{ entry.final_status }}</span>
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
  name: 'TrekHistory',
  components: { DashboardLayout },
  data() {
    return {
      history: [],
      loading: true,
      error: '',
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
        const response = await http.get('/trekker/history')
        if (response.data?.success) {
          this.history = response.data.data || []
        } else {
          this.error = response.data?.message || 'Unable to load history.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load history.'
      } finally {
        this.loading = false
      }
    },
    formatDate(value) {
      if (!value) return '—'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
    },
    formatDates(startDate, endDate) {
      return `${this.formatDate(startDate)} - ${this.formatDate(endDate)}`
    },
    statusBadgeClass(status) {
      switch (status) {
        case 'completed': return 'bg-primary-subtle text-primary-emphasis'
        case 'cancelled': return 'bg-secondary-subtle text-secondary-emphasis'
        default: return 'bg-light text-dark'
      }
    },
  },
}
</script>

<style scoped>
.trek-history-page { width: 100%; }
.empty-icon { width: 64px; height: 64px; }
</style>
