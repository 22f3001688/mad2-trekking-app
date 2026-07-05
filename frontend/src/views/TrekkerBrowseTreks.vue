<template>
  <DashboardLayout>
    <div v-if="showBookModal && selectedTrekForBooking" class="modal fade show d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Booking</h5>
            <button type="button" class="btn-close" @click="closeBookModal"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0">Do you want to book this trek?</p>
            <p class="text-muted small mb-0 mt-2">{{ selectedTrekForBooking.trek_name }}</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="closeBookModal">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="bookingSaving" @click="confirmBooking">
              <span v-if="bookingSaving" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showBookModal" class="modal-backdrop fade show"></div>

    <div class="trekker-browse-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Trekker Operations</p>
          <h1 class="h3 mb-1">Browse Open Treks</h1>
          <p class="text-muted mb-0">Explore treks that are open for booking and have available slots.</p>
        </div>
        <router-link class="btn btn-outline-secondary" :to="{ name: 'Dashboard' }">
          <i class="bi bi-speedometer2 me-1"></i>
          Back to Dashboard
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status" aria-hidden="true"></div>
        <p class="text-muted mb-0">Loading available treks…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <template v-else>
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-12 col-lg-4">
                <label class="form-label small text-muted">Search</label>
                <input v-model.trim="filters.q" class="form-control" placeholder="Search treks" @input="fetchTreks" />
              </div>
              <div class="col-12 col-md-6 col-lg-2">
                <label class="form-label small text-muted">Difficulty</label>
                <select v-model="filters.difficulty" class="form-select" @change="fetchTreks">
                  <option value="">All</option>
                  <option value="easy">Easy</option>
                  <option value="moderate">Moderate</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
              <div class="col-12 col-md-6 col-lg-2">
                <label class="form-label small text-muted">Location</label>
                <input v-model.trim="filters.location" class="form-control" placeholder="Filter location" @input="fetchTreks" />
              </div>
              <div class="col-12 col-md-6 col-lg-2">
                <label class="form-label small text-muted">Duration</label>
                <input v-model.trim="filters.duration" type="number" min="1" class="form-control" placeholder="Days" @input="fetchTreks" />
              </div>
              <div class="col-12 col-md-6 col-lg-2">
                <label class="form-label small text-muted">Sort By</label>
                <select v-model="filters.sort" class="form-select" @change="fetchTreks">
                  <option value="start_asc">Start Date: Soonest</option>
                  <option value="start_desc">Start Date: Latest</option>
                  <option value="duration_asc">Duration: Shortest</option>
                  <option value="duration_desc">Duration: Longest</option>
                  <option value="location_asc">Location: A-Z</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
          {{ successMessage }}
          <button type="button" class="btn-close" aria-label="Close" @click="successMessage = ''"></button>
        </div>

        <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
          {{ errorMessage }}
          <button type="button" class="btn-close" aria-label="Close" @click="errorMessage = ''"></button>
        </div>

        <div v-if="treks.length === 0" class="card shadow-sm border-0">
          <div class="card-body text-center py-5">
            <div class="empty-icon rounded-circle bg-light text-muted d-inline-flex align-items-center justify-content-center mb-3">
              <i class="bi bi-map fs-3"></i>
            </div>
            <h2 class="h5 mb-2">No open treks available</h2>
            <p class="text-muted mb-0">There are no treks that match the current availability rules.</p>
          </div>
        </div>

        <div v-else class="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">
          <div v-for="trek in treks" :key="trek.id" class="col">
            <div class="card shadow-sm border-0 h-100 trek-card">
              <div class="card-body d-flex flex-column">
                <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
                  <div>
                    <h2 class="h5 mb-1">{{ trek.trek_name }}</h2>
                    <p class="text-muted small mb-0">
                      <i class="bi bi-geo-alt me-1"></i>
                      {{ trek.location }}
                    </p>
                  </div>
                  <span class="badge text-capitalize" :class="difficultyBadgeClass(trek.difficulty)">
                    {{ trek.difficulty }}
                  </span>
                </div>

                <p class="text-muted flex-grow-1 mb-3 description-preview">
                  {{ previewDescription(trek.description) }}
                </p>

                <div class="row g-3 mb-3">
                  <div class="col-6">
                    <div class="meta-block h-100">
                      <span class="meta-label">Duration</span>
                      <div class="fw-semibold">{{ trek.duration_days }} days</div>
                    </div>
                  </div>
                  <div class="col-6">
                    <div class="meta-block h-100">
                      <span class="meta-label">Slots</span>
                      <div class="fw-semibold">{{ trek.available_slots }}/{{ trek.total_slots }}</div>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="meta-block h-100">
                      <span class="meta-label">Start Date</span>
                      <div class="fw-semibold">{{ formatDate(trek.start_date) }}</div>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="meta-block h-100">
                      <span class="meta-label">End Date</span>
                      <div class="fw-semibold">{{ formatDate(trek.end_date) }}</div>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="meta-block h-100">
                      <span class="meta-label">Assigned Staff</span>
                      <div class="fw-semibold">{{ trek.assigned_staff_name || '—' }}</div>
                    </div>
                  </div>
                </div>

                <div class="d-grid gap-2 d-sm-flex">
                  <button type="button" class="btn btn-outline-secondary flex-fill" @click="openDetails(trek)">
                    View Details
                  </button>
                  <button
                    type="button"
                    class="btn btn-primary flex-fill"
                    :disabled="isBookDisabled(trek)"
                    @click="handleBookTrek(trek)"
                  >
                    Book Trek
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <div v-if="showDetailsModal && selectedTrek" class="modal fade show d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title mb-1">{{ selectedTrek.trek_name }}</h5>
              <p class="text-muted small mb-0">{{ selectedTrek.location }}</p>
            </div>
            <button type="button" class="btn-close" @click="closeDetails"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3 mb-3">
              <div class="col-12 col-md-4">
                <div class="border rounded-3 p-3 bg-light h-100">
                  <p class="text-muted small mb-1">Difficulty</p>
                  <div class="fw-semibold text-capitalize">{{ selectedTrek.difficulty }}</div>
                </div>
              </div>
              <div class="col-12 col-md-4">
                <div class="border rounded-3 p-3 bg-light h-100">
                  <p class="text-muted small mb-1">Duration</p>
                  <div class="fw-semibold">{{ selectedTrek.duration_days }} days</div>
                </div>
              </div>
              <div class="col-12 col-md-4">
                <div class="border rounded-3 p-3 bg-light h-100">
                  <p class="text-muted small mb-1">Available Slots</p>
                  <div class="fw-semibold">{{ selectedTrek.available_slots }}/{{ selectedTrek.total_slots }}</div>
                </div>
              </div>
            </div>

            <div class="mb-3">
              <h6 class="text-uppercase text-muted small fw-semibold">Description</h6>
              <p class="mb-0">{{ selectedTrek.description || 'No description provided.' }}</p>
            </div>

            <div class="row g-3">
              <div class="col-12 col-md-6">
                <div class="border rounded-3 p-3 h-100">
                  <p class="text-muted small mb-1">Start Date</p>
                  <div class="fw-semibold">{{ formatDate(selectedTrek.start_date) }}</div>
                </div>
              </div>
              <div class="col-12 col-md-6">
                <div class="border rounded-3 p-3 h-100">
                  <p class="text-muted small mb-1">End Date</p>
                  <div class="fw-semibold">{{ formatDate(selectedTrek.end_date) }}</div>
                </div>
              </div>
              <div class="col-12">
                <div class="border rounded-3 p-3 h-100">
                  <p class="text-muted small mb-1">Assigned Staff</p>
                  <div class="fw-semibold">{{ selectedTrek.assigned_staff_name || '—' }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="closeDetails">Close</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showDetailsModal" class="modal-backdrop fade show"></div>
  </DashboardLayout>
</template>

<script>
import DashboardLayout from '../components/DashboardLayout.vue'
import http from '../services/http.js'

export default {
  name: 'TrekkerBrowseTreks',
  components: { DashboardLayout },
  data() {
    return {
      loading: true,
      error: '',
      treks: [],
      selectedTrek: null,
      showDetailsModal: false,
      showBookModal: false,
      selectedTrekForBooking: null,
      bookingSaving: false,
      successMessage: '',
      errorMessage: '',
      filters: {
        q: '',
        difficulty: '',
        location: '',
        duration: '',
        sort: 'start_asc',
      },
    }
  },
  mounted() {
    this.fetchTreks()
  },
  methods: {
    async fetchTreks() {
      this.loading = true
      this.error = ''

      try {
        const params = new URLSearchParams()
        if (this.filters.q) params.append('q', this.filters.q)
        if (this.filters.difficulty) params.append('difficulty', this.filters.difficulty)
        if (this.filters.location) params.append('location', this.filters.location)
        if (this.filters.duration) params.append('duration', this.filters.duration)
        if (this.filters.sort) params.append('sort', this.filters.sort)

        const query = params.toString()
        const response = await http.get(`/trekker/treks${query ? `?${query}` : ''}`)
        if (response.data?.success) {
          this.treks = response.data.data || []
        } else {
          this.error = response.data?.message || 'Unable to load available treks.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load available treks.'
      } finally {
        this.loading = false
      }
    },
    previewDescription(description) {
      if (!description) {
        return 'No description provided.'
      }

      const preview = description.trim()
      if (preview.length <= 140) {
        return preview
      }

      return `${preview.slice(0, 140).trimEnd()}...`
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
    difficultyBadgeClass(difficulty) {
      switch (difficulty) {
        case 'easy':
          return 'bg-success-subtle text-success-emphasis'
        case 'moderate':
          return 'bg-warning-subtle text-warning-emphasis'
        case 'hard':
          return 'bg-danger-subtle text-danger-emphasis'
        default:
          return 'bg-light text-dark'
      }
    },
    openDetails(trek) {
      this.selectedTrek = trek
      this.showDetailsModal = true
    },
    closeDetails() {
      this.showDetailsModal = false
      this.selectedTrek = null
    },
    isBookDisabled(trek) {
      return trek.available_slots <= 0 || trek.already_booked
    },
    handleBookTrek(trek) {
      if (this.isBookDisabled(trek)) {
        return
      }

      this.selectedTrekForBooking = trek
      this.errorMessage = ''
      this.showBookModal = true
    },
    closeBookModal() {
      this.showBookModal = false
      this.selectedTrekForBooking = null
      this.bookingSaving = false
    },
    async confirmBooking() {
      if (!this.selectedTrekForBooking) {
        return
      }

      this.bookingSaving = true
      this.errorMessage = ''

      try {
        const response = await http.post('/trekker/bookings', {
          trek_id: this.selectedTrekForBooking.id,
        })

        if (response.data?.success) {
          this.successMessage = response.data.message || 'Trek booked successfully'
          this.closeBookModal()
          await this.fetchTreks()
        } else {
          this.errorMessage = response.data?.message || 'Unable to book trek.'
        }
      } catch (err) {
        this.errorMessage = err.response?.data?.message || 'Unable to book trek.'
      } finally {
        this.bookingSaving = false
      }
    },
  },
}
</script>

<style scoped>
.trekker-browse-page {
  width: 100%;
}

.trek-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.trek-card:hover {
  transform: translateY(-2px);
}

.empty-icon {
  width: 64px;
  height: 64px;
}

.meta-block {
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 0.75rem;
  padding: 0.75rem;
  background: var(--bs-tertiary-bg);
}

.meta-label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--bs-secondary-color);
  margin-bottom: 0.25rem;
}

.description-preview {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>