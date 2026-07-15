<template>
  <DashboardLayout>
    <div class="trekker-bookings-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Trekker Operations</p>
          <h1 class="h3 mb-1">My Bookings</h1>
          <p class="text-muted mb-0">Review your bookings and track their current trek status.</p>
        </div>
        <router-link class="btn btn-outline-secondary" :to="{ name: 'TrekkerBrowseTreks' }">
          <i class="bi bi-map me-1"></i>
          Browse Treks
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status" aria-hidden="true"></div>
        <p class="text-muted mb-0">Loading your bookings…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <template v-else>
        <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
          {{ successMessage }}
          <button type="button" class="btn-close" aria-label="Close" @click="successMessage = ''"></button>
        </div>

        <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
          {{ errorMessage }}
          <button type="button" class="btn-close" aria-label="Close" @click="errorMessage = ''"></button>
        </div>

        <div v-if="bookings.length === 0" class="card shadow-sm border-0">
          <div class="card-body text-center py-5">
            <div class="empty-icon rounded-circle bg-light text-muted d-inline-flex align-items-center justify-content-center mb-3">
              <i class="bi bi-calendar2-check fs-3"></i>
            </div>
            <h2 class="h5 mb-2">No bookings found</h2>
            <p class="text-muted mb-0">You do not have any bookings yet.</p>
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
                    <th scope="col">Start Date</th>
                    <th scope="col">End Date</th>
                    <th scope="col">Booking Date</th>
                    <th scope="col">Booking Status</th>
                    <th scope="col">Trek Status</th>
                    <th scope="col">Payment Status</th>
                    <th scope="col" class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="booking in bookings" :key="booking.booking_id">
                    <td class="fw-semibold">{{ booking.trek_name }}</td>
                    <td>{{ booking.location }}</td>
                    <td>{{ formatDate(booking.start_date) }}</td>
                    <td>{{ formatDate(booking.end_date) }}</td>
                    <td>{{ formatDateTime(booking.booking_date) }}</td>
                    <td>
                      <span class="badge text-capitalize" :class="bookingBadgeClass(booking.booking_status)">
                        {{ booking.booking_status }}
                      </span>
                    </td>
                    <td>
                      <span class="badge text-capitalize" :class="trekBadgeClass(booking.trek_status)">
                        {{ booking.trek_status }}
                      </span>
                    </td>
                    <td>
                      <span class="badge text-capitalize" :class="paymentBadgeClass(booking.payment_status)">
                        {{ booking.payment_status }}
                      </span>
                    </td>
                    <td class="text-end">
                      <div class="btn-group btn-group-sm" role="group" aria-label="Booking actions">
                        <router-link class="btn btn-outline-secondary" :to="{ name: 'BookingDetails', params: { bookingId: booking.booking_id } }">
                          View Details
                        </router-link>
                        <button class="btn btn-outline-danger" type="button" :disabled="!canCancelBooking(booking)" @click="openCancelModal(booking)">
                          Cancel Booking
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </template>
    </div>

    <div v-if="showCancelModal && selectedBooking" class="modal fade show d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Cancel Booking</h5>
            <button type="button" class="btn-close" @click="closeCancelModal"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0">Do you want to cancel this booking?</p>
            <p class="text-muted small mb-0 mt-2">{{ selectedBooking.trek_name }}</p>
            <div v-if="cancelError" class="alert alert-danger mt-3 mb-0">{{ cancelError }}</div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="closeCancelModal">Close</button>
            <button type="button" class="btn btn-danger" :disabled="cancelling" @click="confirmCancelBooking">
              <span v-if="cancelling" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showCancelModal" class="modal-backdrop fade show"></div>
  </DashboardLayout>
</template>

<script>
import DashboardLayout from '../components/DashboardLayout.vue'
import http from '../services/http.js'

export default {
  name: 'TrekkerMyBookings',
  components: { DashboardLayout },
  data() {
    return {
      bookings: [],
      loading: true,
      error: '',
      successMessage: '',
      errorMessage: '',
      showCancelModal: false,
      selectedBooking: null,
      cancelling: false,
      cancelError: '',
    }
  },
  mounted() {
    this.fetchBookings()
  },
  methods: {
    async fetchBookings() {
      this.loading = true
      this.error = ''

      try {
        const response = await http.get('/trekker/bookings')
        if (response.data?.success) {
          this.bookings = response.data.data || []
        } else {
          this.error = response.data?.message || 'Unable to load your bookings.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load your bookings.'
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
    formatDateTime(value) {
      if (!value) {
        return '—'
      }

      const date = new Date(value)
      if (Number.isNaN(date.getTime())) {
        return value
      }

      return date.toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    },
    bookingBadgeClass(status) {
      switch (status) {
        case 'booked':
          return 'bg-success-subtle text-success-emphasis'
        case 'cancelled':
          return 'bg-secondary-subtle text-secondary-emphasis'
        case 'completed':
          return 'bg-primary-subtle text-primary-emphasis'
        default:
          return 'bg-warning-subtle text-warning-emphasis'
      }
    },
    trekBadgeClass(status) {
      switch (status) {
        case 'open':
          return 'bg-success-subtle text-success-emphasis'
        case 'closed':
          return 'bg-secondary-subtle text-secondary-emphasis'
        case 'completed':
          return 'bg-primary-subtle text-primary-emphasis'
        default:
          return 'bg-warning-subtle text-warning-emphasis'
      }
    },
    paymentBadgeClass(status) {
      switch (status) {
        case 'paid':
          return 'bg-success-subtle text-success-emphasis'
        case 'not_applicable':
          return 'bg-light text-dark'
        case 'refunded':
          return 'bg-info-subtle text-info-emphasis'
        case 'failed':
          return 'bg-danger-subtle text-danger-emphasis'
        default:
          return 'bg-warning-subtle text-warning-emphasis'
      }
    },
    canCancelBooking(booking) {
      return booking.booking_status === 'booked' && booking.trek_status === 'open' && new Date(booking.start_date) > new Date()
    },
    openCancelModal(booking) {
      if (!this.canCancelBooking(booking)) {
        return
      }

      this.selectedBooking = booking
      this.cancelError = ''
      this.showCancelModal = true
    },
    closeCancelModal() {
      this.showCancelModal = false
      this.selectedBooking = null
      this.cancelling = false
      this.cancelError = ''
    },
    async confirmCancelBooking() {
      if (!this.selectedBooking) {
        return
      }

      this.cancelling = true
      this.cancelError = ''

      try {
        const response = await http.put(`/trekker/bookings/${this.selectedBooking.booking_id}/cancel`)
        if (response.data?.success) {
          this.successMessage = response.data.message || 'Booking cancelled successfully.'
          await this.fetchBookings()
          this.closeCancelModal()
        } else {
          this.cancelError = response.data?.message || 'Unable to cancel booking.'
        }
      } catch (err) {
        this.cancelError = err.response?.data?.message || 'Unable to cancel booking.'
      } finally {
        this.cancelling = false
      }
    },
  },
}
</script>

<style scoped>
.trekker-bookings-page {
  width: 100%;
}

.empty-icon {
  width: 64px;
  height: 64px;
}
</style>