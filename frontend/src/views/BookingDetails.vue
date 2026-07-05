<template>
  <DashboardLayout>
    <div class="booking-details-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Trekker Operations</p>
          <h1 class="h3 mb-1">Booking Details</h1>
          <p class="text-muted mb-0">Review the booking and trek information for this reservation.</p>
        </div>
        <router-link class="btn btn-outline-secondary" :to="{ name: 'TrekkerMyBookings' }">
          <i class="bi bi-arrow-left me-1"></i>
          Back to My Bookings
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status" aria-hidden="true"></div>
        <p class="text-muted mb-0">Loading booking details…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <template v-else>
        <div class="row g-4">
          <div class="col-12 col-lg-6">
            <div class="card shadow-sm border-0 h-100">
              <div class="card-body">
                <h2 class="h5 mb-3">Booking Information</h2>
                <div class="detail-item"><span>Booking ID</span><strong>{{ booking.booking.id }}</strong></div>
                <div class="detail-item"><span>Booking Date</span><strong>{{ formatDateTime(booking.booking.booking_date) }}</strong></div>
                <div class="detail-item"><span>Status</span><strong class="text-capitalize">{{ booking.booking.status }}</strong></div>
                <div class="detail-item"><span>Payment Status</span><strong class="text-capitalize">{{ booking.booking.payment_status }}</strong></div>
              </div>
            </div>
          </div>
          <div class="col-12 col-lg-6">
            <div class="card shadow-sm border-0 h-100">
              <div class="card-body">
                <h2 class="h5 mb-3">Trek Information</h2>
                <div class="detail-item"><span>Trek Name</span><strong>{{ booking.trek.trek_name }}</strong></div>
                <div class="detail-item"><span>Location</span><strong>{{ booking.trek.location }}</strong></div>
                <div class="detail-item"><span>Difficulty</span><strong class="text-capitalize">{{ booking.trek.difficulty }}</strong></div>
                <div class="detail-item"><span>Duration</span><strong>{{ booking.trek.duration_days }} days</strong></div>
                <div class="detail-item"><span>Start Date</span><strong>{{ formatDate(booking.trek.start_date) }}</strong></div>
                <div class="detail-item"><span>End Date</span><strong>{{ formatDate(booking.trek.end_date) }}</strong></div>
                <div class="detail-item"><span>Trek Status</span><strong class="text-capitalize">{{ booking.trek.status }}</strong></div>
              </div>
            </div>
          </div>
          <div class="col-12">
            <div class="card shadow-sm border-0">
              <div class="card-body">
                <h2 class="h5 mb-3">Assigned Staff Information</h2>
                <div v-if="booking.assigned_staff.full_name" class="row g-3">
                  <div class="col-12 col-md-4"><div class="detail-item"><span>Name</span><strong>{{ booking.assigned_staff.full_name }}</strong></div></div>
                  <div class="col-12 col-md-4"><div class="detail-item"><span>Email</span><strong>{{ booking.assigned_staff.email || '—' }}</strong></div></div>
                  <div class="col-12 col-md-4"><div class="detail-item"><span>Phone</span><strong>{{ booking.assigned_staff.phone || '—' }}</strong></div></div>
                </div>
                <div v-else class="text-muted">No staff assigned.</div>
              </div>
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

export default {
  name: 'BookingDetails',
  components: { DashboardLayout },
  data() {
    return {
      booking: {
        booking: {},
        trek: {},
        assigned_staff: {},
      },
      loading: true,
      error: '',
    }
  },
  mounted() {
    this.fetchBookingDetails()
  },
  methods: {
    async fetchBookingDetails() {
      this.loading = true
      this.error = ''
      try {
        const response = await http.get(`/trekker/bookings/${this.$route.params.bookingId}`)
        if (response.data?.success) {
          this.booking = response.data.data || this.booking
        } else {
          this.error = response.data?.message || 'Unable to load booking details.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load booking details.'
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
    formatDateTime(value) {
      if (!value) return '—'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return date.toLocaleString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    },
  },
}
</script>

<style scoped>
.booking-details-page { width: 100%; }
.detail-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--bs-border-color-translucent);
}
.detail-item:last-child { border-bottom: 0; }
.detail-item span { color: var(--bs-secondary-color); }
</style>
