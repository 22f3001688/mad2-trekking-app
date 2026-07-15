<template>
  <DashboardLayout>
    <div class="trek-list-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Admin Operations</p>
          <h1 class="h3 mb-1">Trek Management</h1>
          <p class="text-muted mb-0">Browse and manage trekking experiences from one place.</p>
        </div>
        <router-link class="btn btn-primary" :to="{ name: 'AdminTrekCreate' }">
          <i class="bi bi-plus-lg me-1"></i>
          Create Trek
        </router-link>
      </div>

      <div class="card shadow-sm border-0">
        <div class="card-body">
          <div class="row g-3 mb-4">
            <div class="col-12 col-md-4">
              <label class="form-label small text-muted">Search</label>
              <input v-model="filters.search" class="form-control" placeholder="Search by name or location" @input="fetchTreks" />
            </div>
            <div class="col-12 col-md-4">
              <label class="form-label small text-muted">Difficulty</label>
              <select v-model="filters.difficulty" class="form-select" @change="fetchTreks">
                <option value="">All difficulties</option>
                <option value="easy">Easy</option>
                <option value="moderate">Moderate</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            <div class="col-12 col-md-4">
              <label class="form-label small text-muted">Status</label>
              <select v-model="filters.status" class="form-select" @change="fetchTreks">
                <option value="">All statuses</option>
                <option value="pending">Pending</option>
                <option value="open">Open</option>
                <option value="closed">Closed</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>

          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary mb-3" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-muted mb-0">Loading treks…</p>
          </div>

          <div v-else-if="treks.length === 0" class="text-center py-5 text-muted">
            No treks found.
          </div>

          <div v-else class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Trek Name</th>
                  <th>Location</th>
                  <th>Difficulty</th>
                  <th>Duration</th>
                  <th>Slots</th>
                  <th>Status</th>
                  <th>Assigned Staff</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th class="text-end">Actions</th>
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
                  <td>
                    <span class="badge text-capitalize" :class="statusBadgeClass(trek.status)">{{ trek.status }}</span>
                  </td>
                  <td>{{ trek.assigned_staff_name || '—' }}</td>
                  <td>{{ trek.start_date }}</td>
                  <td>{{ trek.end_date }}</td>
                  <td class="text-end">
                    <div class="btn-group btn-group-sm" role="group">
                      <button class="btn btn-outline-secondary" type="button" @click="openViewModal(trek)">
                        View
                      </button>
                      <router-link class="btn btn-outline-primary" :to="{ name: 'AdminTrekEdit', params: { id: trek.id } }">
                        Edit
                      </router-link>
                      <button
                        class="btn btn-outline-danger"
                        type="button"
                        disabled
                        title="Delete trek is not available in this release"
                      >
                        Delete
                      </button>
                      <button class="btn btn-outline-info" type="button" @click="openAssignModal(trek)">
                        Assign Staff
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

    <div v-if="showViewModal && activeViewTrek" class="modal fade show d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Trek Details</h5>
            <button type="button" class="btn-close" @click="closeViewModal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12 col-md-6"><div class="detail-item"><span>Name</span><strong>{{ activeViewTrek.trek_name }}</strong></div></div>
              <div class="col-12 col-md-6"><div class="detail-item"><span>Location</span><strong>{{ activeViewTrek.location }}</strong></div></div>
              <div class="col-12 col-md-6"><div class="detail-item"><span>Difficulty</span><strong class="text-capitalize">{{ activeViewTrek.difficulty }}</strong></div></div>
              <div class="col-12 col-md-6"><div class="detail-item"><span>Status</span><strong class="text-capitalize">{{ activeViewTrek.status }}</strong></div></div>
              <div class="col-12 col-md-6"><div class="detail-item"><span>Duration</span><strong>{{ activeViewTrek.duration_days }} days</strong></div></div>
              <div class="col-12 col-md-6"><div class="detail-item"><span>Slots</span><strong>{{ activeViewTrek.available_slots }}/{{ activeViewTrek.total_slots }}</strong></div></div>
              <div class="col-12 col-md-6"><div class="detail-item"><span>Start Date</span><strong>{{ activeViewTrek.start_date || '—' }}</strong></div></div>
              <div class="col-12 col-md-6"><div class="detail-item"><span>End Date</span><strong>{{ activeViewTrek.end_date || '—' }}</strong></div></div>
              <div class="col-12"><div class="detail-item"><span>Assigned Staff</span><strong>{{ activeViewTrek.assigned_staff_name || '—' }}</strong></div></div>
              <div class="col-12">
                <div class="border rounded-3 p-3 bg-body-tertiary">
                  <p class="small text-muted mb-1">Description</p>
                  <p class="mb-0">{{ activeViewTrek.description || 'No description available.' }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="closeViewModal">Close</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showViewModal" class="modal-backdrop fade show"></div>

    <div v-if="showAssignModal" class="modal fade show d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Assign Staff</h5>
            <button type="button" class="btn-close" @click="closeAssignModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="assignError" class="alert alert-danger" role="alert">
              {{ assignError }}
            </div>
            <div v-if="assignSuccess" class="alert alert-success" role="alert">
              {{ assignSuccess }}
            </div>
            <div v-if="assignLoading" class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else>
              <label class="form-label">Select active staff member</label>
              <select v-model="selectedStaffId" class="form-select">
                <option :value="null" disabled>Select staff</option>
                <option v-for="staff in availableStaff" :key="staff.id" :value="staff.id">
                  {{ staff.full_name }} ({{ staff.email }})
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="closeAssignModal">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="assignLoading || !selectedStaffId" @click="submitAssignment">
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showAssignModal" class="modal-backdrop fade show"></div>
  </DashboardLayout>
</template>

<script>
import DashboardLayout from '../components/DashboardLayout.vue'
import http from '../services/http.js'

export default {
  name: 'AdminTrekList',
  components: { DashboardLayout },
  data() {
    return {
      loading: true,
      treks: [],
      filters: {
        search: '',
        difficulty: '',
        status: '',
      },
      showAssignModal: false,
      showViewModal: false,
      assignLoading: false,
      assignError: '',
      assignSuccess: '',
      availableStaff: [],
      selectedStaffId: null,
      activeTrek: null,
      activeViewTrek: null,
    }
  },
  mounted() {
    this.fetchTreks()
  },
  methods: {
    async fetchTreks() {
      this.loading = true

      try {
        const params = new URLSearchParams()
        if (this.filters.search) params.append('search', this.filters.search)
        if (this.filters.difficulty) params.append('difficulty', this.filters.difficulty)
        if (this.filters.status) params.append('status', this.filters.status)

        const response = await http.get(`/admin/treks?${params.toString()}`)
        if (response.data?.success) {
          this.treks = response.data.data || []
        }
      } catch (err) {
        this.treks = []
      } finally {
        this.loading = false
      }
    },
    async openAssignModal(trek) {
      this.activeTrek = trek
      this.showAssignModal = true
      this.assignError = ''
      this.assignSuccess = ''
      this.selectedStaffId = null
      this.assignLoading = true

      try {
        const response = await http.get('/admin/staff/available')
        if (response.data?.success) {
          this.availableStaff = response.data.data || []
        } else {
          this.assignError = response.data?.message || 'Unable to load available staff.'
        }
      } catch (err) {
        this.assignError = err.response?.data?.message || 'Unable to load available staff.'
      } finally {
        this.assignLoading = false
      }
    },
    openViewModal(trek) {
      this.activeViewTrek = trek
      this.showViewModal = true
    },
    closeViewModal() {
      this.showViewModal = false
      this.activeViewTrek = null
    },
    closeAssignModal() {
      this.showAssignModal = false
      this.assignError = ''
      this.assignSuccess = ''
      this.availableStaff = []
      this.selectedStaffId = null
      this.activeTrek = null
    },
    async submitAssignment() {
      if (!this.activeTrek || !this.selectedStaffId) {
        return
      }

      this.assignError = ''
      this.assignSuccess = ''
      this.assignLoading = true

      try {
        const response = await http.put(`/admin/treks/${this.activeTrek.id}/assign-staff`, { staff_id: this.selectedStaffId })
        if (response.data?.success) {
          this.assignSuccess = 'Staff assigned successfully.'
          await this.fetchTreks()
          setTimeout(() => this.closeAssignModal(), 600)
        } else {
          this.assignError = response.data?.message || 'Unable to assign staff.'
        }
      } catch (err) {
        this.assignError = err.response?.data?.message || 'Unable to assign staff.'
      } finally {
        this.assignLoading = false
      }
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
.trek-list-page {
  width: 100%;
}

.detail-item {
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 0.75rem;
  padding: 0.75rem;
  background: var(--bs-tertiary-bg);
}

.detail-item span {
  display: block;
  color: var(--bs-secondary-color);
  font-size: 0.8rem;
  margin-bottom: 0.2rem;
}
</style>
