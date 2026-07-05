<template>
  <DashboardLayout>
    <div class="profile-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Trekker Operations</p>
          <h1 class="h3 mb-1">Profile</h1>
          <p class="text-muted mb-0">Update your name and phone number.</p>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status" aria-hidden="true"></div>
        <p class="text-muted mb-0">Loading profile…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

      <div v-else class="row justify-content-center">
        <div class="col-12 col-lg-8">
          <div class="card shadow-sm border-0">
            <div class="card-body p-4 p-md-5">
              <form @submit.prevent="saveProfile">
                <div class="row g-3">
                  <div class="col-12">
                    <label class="form-label">Full Name</label>
                    <input v-model.trim="form.full_name" type="text" class="form-control" :class="{ 'is-invalid': validationErrors.full_name }" />
                    <div class="invalid-feedback">{{ validationErrors.full_name }}</div>
                  </div>
                  <div class="col-12 col-md-6">
                    <label class="form-label">Email</label>
                    <input :value="profile.email" type="email" class="form-control" disabled />
                  </div>
                  <div class="col-12 col-md-6">
                    <label class="form-label">Role</label>
                    <input :value="profile.role" type="text" class="form-control text-capitalize" disabled />
                  </div>
                  <div class="col-12">
                    <label class="form-label">Phone Number</label>
                    <input v-model.trim="form.phone" type="text" class="form-control" :class="{ 'is-invalid': validationErrors.phone }" />
                    <div class="invalid-feedback">{{ validationErrors.phone }}</div>
                  </div>
                </div>

                <div v-if="successMessage" class="alert alert-success mt-4 mb-0">{{ successMessage }}</div>
                <div v-if="serverError" class="alert alert-danger mt-4 mb-0">{{ serverError }}</div>

                <div class="d-flex justify-content-end gap-2 mt-4">
                  <router-link class="btn btn-outline-secondary" :to="{ name: 'Dashboard' }">Cancel</router-link>
                  <button type="submit" class="btn btn-primary" :disabled="saving">
                    <span v-if="saving" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
                    Save Changes
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script>
import DashboardLayout from '../components/DashboardLayout.vue'
import authService from '../services/auth.js'
import http from '../services/http.js'

export default {
  name: 'Profile',
  components: { DashboardLayout },
  data() {
    return {
      loading: true,
      saving: false,
      error: '',
      serverError: '',
      successMessage: '',
      profile: {
        id: null,
        full_name: '',
        email: '',
        phone: '',
        role: '',
      },
      form: {
        full_name: '',
        phone: '',
      },
      validationErrors: {
        full_name: '',
        phone: '',
      },
    }
  },
  mounted() {
    this.fetchProfile()
  },
  methods: {
    async fetchProfile() {
      this.loading = true
      this.error = ''
      try {
        const response = await http.get('/trekker/profile')
        if (response.data?.success) {
          this.profile = response.data.data || this.profile
          this.form.full_name = this.profile.full_name || ''
          this.form.phone = this.profile.phone || ''
        } else {
          this.error = response.data?.message || 'Unable to load profile.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load profile.'
      } finally {
        this.loading = false
      }
    },
    clearValidationErrors() {
      this.validationErrors.full_name = ''
      this.validationErrors.phone = ''
      this.serverError = ''
    },
    validateForm() {
      this.clearValidationErrors()
      let valid = true
      if (!this.form.full_name) {
        this.validationErrors.full_name = 'Full name is required.'
        valid = false
      }
      if (this.form.phone && this.form.phone.length > 20) {
        this.validationErrors.phone = 'Phone number must be 20 characters or less.'
        valid = false
      }
      return valid
    },
    async saveProfile() {
      if (!this.validateForm()) {
        return
      }

      this.saving = true
      this.successMessage = ''
      this.serverError = ''

      try {
        const response = await http.put('/trekker/profile', {
          full_name: this.form.full_name,
          phone: this.form.phone,
        })

        if (response.data?.success) {
          this.profile = response.data.data || this.profile
          this.form.full_name = this.profile.full_name || ''
          this.form.phone = this.profile.phone || ''
          localStorage.setItem('trekscape_user_name', this.profile.full_name || '')
          const currentUser = authService.getCurrentUser()
          if (currentUser) {
            currentUser.full_name = this.profile.full_name || ''
          }
          this.successMessage = response.data.message || 'Profile updated successfully.'
        } else {
          this.serverError = response.data?.message || 'Unable to update profile.'
        }
      } catch (err) {
        this.serverError = err.response?.data?.message || 'Unable to update profile.'
      } finally {
        this.saving = false
      }
    },
  },
}
</script>

<style scoped>
.profile-page { width: 100%; }
</style>
