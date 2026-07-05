<template>
  <DashboardLayout>
    <div class="staff-my-treks-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Staff Operations</p>
          <h1 class="h3 mb-1">My Assigned Treks</h1>
          <p class="text-muted mb-0">Track the treks assigned to you and review their current status.</p>
        </div>
        <router-link class="btn btn-outline-primary" :to="{ name: 'StaffDashboard' }">
          <i class="bi bi-speedometer2 me-1"></i>
          Back to Dashboard
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted mb-0">Loading your assigned treks…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else-if="treks.length === 0" class="card shadow-sm border-0">
        <div class="card-body text-center py-5">
          <div class="empty-icon rounded-circle bg-light text-muted d-inline-flex align-items-center justify-content-center mb-3">
            <i class="bi bi-map fs-3"></i>
          </div>
          <h2 class="h5 mb-2">No treks assigned</h2>
          <p class="text-muted mb-0">You do not have any assigned treks at the moment.</p>
        </div>
      </div>

      <div v-else class="card shadow-sm border-0">
        <div class="card-body">
          <div v-if="successMessage" class="alert alert-success" role="alert">
            {{ successMessage }}
          </div>
          <div class="table-responsive">
            <table class="table align-middle mb-0">
              <thead>
                <tr>
                  <th scope="col">Trek Name</th>
                  <th scope="col">Location</th>
                  <th scope="col">Difficulty</th>
                  <th scope="col">Duration</th>
                  <th scope="col">Available/Total Slots</th>
                  <th scope="col">Registered Participants</th>
                  <th scope="col">Status</th>
                  <th scope="col">Start Date</th>
                  <th scope="col">End Date</th>
                  <th scope="col" class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trek in treks" :key="trek.id">
                  <td>
                    <div class="fw-semibold">{{ trek.trek_name }}</div>
                  </td>
                  <td>{{ trek.location }}</td>
                  <td>
                    <span class="badge bg-light text-dark text-capitalize">{{ trek.difficulty }}</span>
                  </td>
                  <td>{{ trek.duration_days }} days</td>
                  <td>{{ trek.available_slots }}/{{ trek.total_slots }}</td>
                  <td>{{ trek.registered_participants }}</td>
                  <td>
                    <span class="badge text-capitalize" :class="statusBadgeClass(trek.status)">
                      {{ trek.status }}
                    </span>
                  </td>
                  <td>{{ formatDate(trek.start_date) }}</td>
                  <td>{{ formatDate(trek.end_date) }}</td>
                  <td class="text-end">
                    <div class="btn-group btn-group-sm" role="group" aria-label="Trek actions">
                      <button class="btn btn-outline-secondary" type="button" :disabled="trek.status === 'completed'" @click="openCompleteModal(trek)">
                        Mark Completed
                      </button>
                      <router-link class="btn btn-outline-primary" :to="{ name: 'StaffTrekParticipants', params: { id: trek.id } }">
                        View Participants
                      </router-link>
                      <button class="btn btn-outline-info" type="button" @click="openSlotsModal(trek)">
                        Update Slots
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCompleteModal" class="modal fade show d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Mark Trek as Completed</h5>
            <button type="button" class="btn-close" @click="closeCompleteModal"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted mb-3">
              Are you sure you want to mark this trek as completed? This action will finalize the trek.
            </p>
            <div v-if="completeError" class="alert alert-danger" role="alert">
              {{ completeError }}
            </div>
            <p class="small text-muted mb-0">This will set the trek status to Completed and cannot be changed again.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="closeCompleteModal">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="completeSaving" @click="submitCompleteTrek">
              <span v-if="completeSaving" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showCompleteModal" class="modal-backdrop fade show"></div>

    <div v-if="showSlotsModal" class="modal fade show d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Update Trek Slots</h5>
            <button type="button" class="btn-close" @click="closeSlotsModal"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted mb-3">
              Update available slots for <strong>{{ activeTrekSlots?.trek_name }}</strong>.
            </p>
            <div class="row g-3 mb-3">
              <div class="col-12 col-md-6">
                <div class="border rounded-3 p-3 bg-light h-100">
                  <p class="text-muted small mb-1">Current Total Slots</p>
                  <div class="h5 mb-0">{{ activeTrekSlots?.total_slots ?? '—' }}</div>
                </div>
              </div>
              <div class="col-12 col-md-6">
                <div class="border rounded-3 p-3 bg-light h-100">
                  <p class="text-muted small mb-1">Current Available Slots</p>
                  <div class="h5 mb-0">{{ activeTrekSlots?.available_slots ?? '—' }}</div>
                </div>
              </div>
            </div>
            <div v-if="slotsError" class="alert alert-danger" role="alert">
              {{ slotsError }}
            </div>
            <label class="form-label">Available Slots</label>
            <input
              v-model="selectedAvailableSlots"
              type="number"
              min="0"
              :max="activeTrekSlots?.total_slots"
              class="form-control"
              :disabled="slotsSaving"
            />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="closeSlotsModal">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="slotsSaving || selectedAvailableSlots === ''" @click="submitSlotsUpdate">
              <span v-if="slotsSaving" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showSlotsModal" class="modal-backdrop fade show"></div>
  </DashboardLayout>
</template>

<script>
import DashboardLayout from '../components/DashboardLayout.vue'
import http from '../services/http.js'

export default {
  name: 'StaffMyTreks',
  components: { DashboardLayout },
  data() {
    return {
      loading: true,
      error: '',
      successMessage: '',
      treks: [],
      showCompleteModal: false,
      completeSaving: false,
      completeError: '',
      activeCompleteTrek: null,
      showSlotsModal: false,
      slotsSaving: false,
      slotsError: '',
      selectedAvailableSlots: '',
      activeTrekSlots: null,
    }
  },
  mounted() {
    this.fetchMyTreks()
  },
  methods: {
    async fetchMyTreks() {
      this.loading = true
      this.error = ''

      try {
        const response = await http.get('/staff/my-treks')
        if (response.data?.success) {
          this.treks = response.data.data || []
        } else {
          this.error = response.data?.message || 'Unable to load your assigned treks.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load your assigned treks.'
      } finally {
        this.loading = false
      }
    },
    openCompleteModal(trek) {
      this.activeCompleteTrek = trek
      this.completeError = ''
      this.showCompleteModal = true
    },
    openSlotsModal(trek) {
      this.activeTrekSlots = trek
      this.selectedAvailableSlots = trek.available_slots
      this.slotsError = ''
      this.showSlotsModal = true
    },
    closeCompleteModal() {
      this.showCompleteModal = false
      this.completeSaving = false
      this.completeError = ''
      this.activeCompleteTrek = null
    },
    closeSlotsModal() {
      this.showSlotsModal = false
      this.slotsSaving = false
      this.slotsError = ''
      this.selectedAvailableSlots = ''
      this.activeTrekSlots = null
    },
    async submitCompleteTrek() {
      if (!this.activeCompleteTrek) {
        return
      }

      this.completeSaving = true
      this.completeError = ''

      try {
        const response = await http.put(`/staff/treks/${this.activeCompleteTrek.id}/complete`)

        if (response.data?.success) {
          await this.fetchMyTreks()
          this.successMessage = response.data.message || 'Trek status updated successfully.'
          this.closeCompleteModal()
        } else {
          this.completeError = response.data?.message || 'Unable to update trek status.'
        }
      } catch (err) {
        this.completeError = err.response?.data?.message || 'Unable to update trek status.'
      } finally {
        this.completeSaving = false
      }
    },
    async submitSlotsUpdate() {
      if (!this.activeTrekSlots || this.selectedAvailableSlots === '') {
        return
      }

      this.slotsSaving = true
      this.slotsError = ''

      try {
        const response = await http.put(`/staff/treks/${this.activeTrekSlots.id}/slots`, {
          available_slots: Number(this.selectedAvailableSlots),
        })

        if (response.data?.success) {
          await this.fetchMyTreks()
          this.successMessage = response.data.message || 'Trek slots updated successfully.'
          this.closeSlotsModal()
        } else {
          this.slotsError = response.data?.message || 'Unable to update trek slots.'
        }
      } catch (err) {
        this.slotsError = err.response?.data?.message || 'Unable to update trek slots.'
      } finally {
        this.slotsSaving = false
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
  },
}
</script>

<style scoped>
.staff-my-treks-page {
  width: 100%;
}

.empty-icon {
  width: 64px;
  height: 64px;
}
</style>
