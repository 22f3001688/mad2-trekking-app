<template>
  <DashboardLayout>
    <div class="trek-create-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Admin Operations</p>
          <h1 class="h3 mb-1">Create Trek</h1>
          <p class="text-muted mb-0">Add a new trekking experience and let the platform manage availability automatically.</p>
        </div>
        <router-link class="btn btn-outline-secondary btn-sm" :to="{ name: 'AdminTrekIndex' }">
          <i class="bi bi-arrow-left me-1"></i>
          Back to Treks
        </router-link>
      </div>

      <div class="card shadow-sm border-0">
        <div class="card-body p-4 p-lg-5">
          <div v-if="serverError" class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            {{ serverError }}
          </div>

          <form class="needs-validation" novalidate @submit.prevent="submitForm">
            <div class="row g-4">
              <div class="col-md-6">
                <label class="form-label">Trek Name</label>
                <input v-model="form.trek_name" class="form-control" :class="{ 'is-invalid': validationErrors.trek_name }" required />
                <div class="invalid-feedback">{{ validationErrors.trek_name }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label">Location</label>
                <input v-model="form.location" class="form-control" :class="{ 'is-invalid': validationErrors.location }" required />
                <div class="invalid-feedback">{{ validationErrors.location }}</div>
              </div>

              <div class="col-12">
                <label class="form-label">Description</label>
                <textarea v-model="form.description" class="form-control" rows="3" :class="{ 'is-invalid': validationErrors.description }"></textarea>
                <div class="invalid-feedback">{{ validationErrors.description }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label">Difficulty</label>
                <select v-model="form.difficulty" class="form-select" :class="{ 'is-invalid': validationErrors.difficulty }" required>
                  <option value="">Select difficulty</option>
                  <option value="easy">Easy</option>
                  <option value="moderate">Moderate</option>
                  <option value="hard">Hard</option>
                </select>
                <div class="invalid-feedback">{{ validationErrors.difficulty }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label">Duration (days)</label>
                <input v-model.number="form.duration_days" type="number" min="1" class="form-control" :class="{ 'is-invalid': validationErrors.duration_days }" required />
                <div class="invalid-feedback">{{ validationErrors.duration_days }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label">Total Slots</label>
                <input v-model.number="form.total_slots" type="number" min="1" class="form-control" :class="{ 'is-invalid': validationErrors.total_slots }" required />
                <div class="invalid-feedback">{{ validationErrors.total_slots }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label">Start Date</label>
                <input v-model="form.start_date" type="date" class="form-control" :class="{ 'is-invalid': validationErrors.start_date }" required />
                <div class="invalid-feedback">{{ validationErrors.start_date }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label">End Date</label>
                <input v-model="form.end_date" type="date" class="form-control" :class="{ 'is-invalid': validationErrors.end_date }" required />
                <div class="invalid-feedback">{{ validationErrors.end_date }}</div>
              </div>
            </div>

            <div class="d-flex flex-column flex-sm-row gap-2 mt-4">
              <button class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
                Create Trek
              </button>
              <router-link class="btn btn-outline-secondary" :to="{ name: 'AdminTrekIndex' }">
                Cancel
              </router-link>
            </div>
          </form>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script>
import DashboardLayout from '../components/DashboardLayout.vue'
import http from '../services/http.js'

export default {
  name: 'AdminTrekCreate',
  components: { DashboardLayout },
  data() {
    return {
      submitting: false,
      serverError: '',
      validationErrors: {},
      form: {
        trek_name: '',
        location: '',
        description: '',
        difficulty: '',
        duration_days: 1,
        total_slots: 1,
        start_date: '',
        end_date: '',
      },
    }
  },
  methods: {
    async submitForm() {
      this.submitting = true
      this.serverError = ''
      this.validationErrors = {}

      try {
        const response = await http.post('/admin/treks', this.form)

        if (response.data?.success) {
          this.$router.push({ name: 'AdminTrekIndex' })
        } else {
          this.serverError = response.data?.message || 'Unable to create trek.'
        }
      } catch (err) {
        if (err.response?.status === 400 && err.response?.data?.message) {
          this.serverError = err.response.data.message
        } else {
          this.serverError = err.response?.data?.message || 'Unable to create trek.'
        }
      } finally {
        this.submitting = false
      }
    },
  },
}
</script>

<style scoped>
.trek-create-page {
  max-width: 900px;
}
</style>
