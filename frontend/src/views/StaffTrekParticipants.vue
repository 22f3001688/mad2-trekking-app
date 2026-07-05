<template>
  <DashboardLayout>
    <div class="staff-participants-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Staff Operations</p>
          <h1 class="h3 mb-1">Trek Participants</h1>
          <p class="text-muted mb-0">Review the trekkers booked on this assigned trek.</p>
        </div>
        <router-link class="btn btn-outline-primary" :to="{ name: 'StaffMyTreks' }">
          <i class="bi bi-arrow-left me-1"></i>
          Back to Assigned Treks
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted mb-0">Loading participants…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else class="card shadow-sm border-0">
        <div class="card-body">
          <div v-if="participants.length === 0" class="text-center py-5 text-muted">
            No participants found for this trek.
          </div>
          <div v-else class="table-responsive">
            <table class="table align-middle mb-0">
              <thead>
                <tr>
                  <th scope="col">Participant Name</th>
                  <th scope="col">Email</th>
                  <th scope="col">Phone</th>
                  <th scope="col">Booking Date</th>
                  <th scope="col">Booking Status</th>
                  <th scope="col">Payment Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="participant in participants" :key="`${participant.email}-${participant.booking_date}`">
                  <td class="fw-semibold">{{ participant.participant_name }}</td>
                  <td>{{ participant.email }}</td>
                  <td>{{ participant.phone || '—' }}</td>
                  <td>{{ formatDate(participant.booking_date) }}</td>
                  <td>
                    <span class="badge text-capitalize" :class="statusBadgeClass(participant.booking_status)">
                      {{ participant.booking_status }}
                    </span>
                  </td>
                  <td>
                    <span class="badge text-capitalize" :class="paymentBadgeClass(participant.payment_status)">
                      {{ participant.payment_status }}
                    </span>
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
  name: 'StaffTrekParticipants',
  components: { DashboardLayout },
  data() {
    return {
      loading: true,
      error: '',
      participants: [],
    }
  },
  mounted() {
    this.fetchParticipants()
  },
  methods: {
    async fetchParticipants() {
      this.loading = true
      this.error = ''

      try {
        const response = await http.get(`/staff/treks/${this.$route.params.id}/participants`)
        if (response.data?.success) {
          this.participants = response.data.data || []
        } else {
          this.error = response.data?.message || 'Unable to load trek participants.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load trek participants.'
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
    statusBadgeClass(status) {
      switch (status) {
        case 'booked':
          return 'bg-success-subtle text-success-emphasis'
        case 'cancelled':
          return 'bg-secondary-subtle text-secondary-emphasis'
        default:
          return 'bg-warning-subtle text-warning-emphasis'
      }
    },
    paymentBadgeClass(status) {
      switch (status) {
        case 'paid':
          return 'bg-success-subtle text-success-emphasis'
        case 'pending':
          return 'bg-warning-subtle text-warning-emphasis'
        case 'refunded':
          return 'bg-info-subtle text-info-emphasis'
        default:
          return 'bg-secondary-subtle text-secondary-emphasis'
      }
    },
  },
}
</script>

<style scoped>
.staff-participants-page {
  width: 100%;
}
</style>
