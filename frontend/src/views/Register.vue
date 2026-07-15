<template>
  <div class="auth-page min-vh-100">
    <div class="row g-0 min-vh-100 align-items-stretch">
      <div class="col-12 col-lg-6 d-flex align-items-center justify-content-center text-panel">
        <div class="text-content px-4 px-md-5 py-5 w-100">
          <p class="eyebrow mb-2">Join TrekScape</p>
          <h4 class="mb-1">Register</h4>
          <small class="text-muted d-block mb-4">Create your TrekScape account</small>

          <form @submit.prevent="submitRegister" novalidate>
            <div class="mb-3">
              <label for="full_name" class="form-label">Full Name</label>
              <input
                type="text"
                id="full_name"
                v-model="form.full_name"
                class="form-control"
                :class="{ 'is-invalid': errors.full_name }"
                placeholder="Enter your full name"
              />
              <div class="invalid-feedback">{{ errors.full_name }}</div>
            </div>

            <div class="mb-3">
              <label for="email" class="form-label">Email address</label>
              <input
                type="email"
                id="email"
                v-model="form.email"
                class="form-control"
                :class="{ 'is-invalid': errors.email }"
                placeholder="Enter your email"
              />
              <div class="invalid-feedback">{{ errors.email }}</div>
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input
                type="password"
                id="password"
                v-model="form.password"
                class="form-control"
                :class="{ 'is-invalid': errors.password }"
                placeholder="Enter a password"
              />
              <div class="invalid-feedback">{{ errors.password }}</div>
            </div>

            <div class="mb-3">
              <label for="confirm_password" class="form-label">Confirm Password</label>
              <input
                type="password"
                id="confirm_password"
                v-model="form.confirm_password"
                class="form-control"
                :class="{ 'is-invalid': errors.confirm_password }"
                placeholder="Re-enter your password"
              />
              <div class="invalid-feedback">{{ errors.confirm_password }}</div>
            </div>

            <div class="mb-3">
              <label for="phone" class="form-label">Contact Number</label>
              <input
                type="tel"
                id="phone"
                v-model="form.phone"
                class="form-control"
                placeholder="Optional contact number"
              />
            </div>

            <div v-if="serverError" class="alert alert-danger mt-2">{{ serverError }}</div>
            <div v-if="serverMessage" class="alert alert-success mt-2">{{ serverMessage }}</div>

            <button type="submit" class="btn btn-primary w-100 btn-lg mt-2" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Register
            </button>
          </form>

          <div class="mt-4 text-center">
            <p class="mb-0 text-muted">Already have an account? <router-link to="/login">Login here</router-link></p>
          </div>
          <div class="text-center mt-3 text-muted small">
            Only users (Trekkers) may register themselves. Trekking Staff are created by admin.
          </div>
        </div>
      </div>
      <div class="col-12 col-lg-6 image-panel" aria-hidden="true"></div>
    </div>
  </div>
</template>

<script>
import authService from '../services/auth.js'

export default {
  name: 'Register',
  data() {
    return {
      form: {
        full_name: '',
        email: '',
        password: '',
        confirm_password: '',
        phone: '',
      },
      errors: {},
      serverError: '',
      serverMessage: '',
      loading: false,
    }
  },
  methods: {
    async submitRegister() {
      this.errors = {}
      this.serverError = ''
      this.serverMessage = ''

      if (!this.form.full_name) {
        this.errors.full_name = 'Full name is required.'
      }
      if (!this.form.email) {
        this.errors.email = 'Email is required.'
      }
      if (!this.form.password) {
        this.errors.password = 'Password is required.'
      }
      if (!this.form.confirm_password) {
        this.errors.confirm_password = 'Password confirmation is required.'
      }
      if (this.form.password && this.form.password.length < 8) {
        this.errors.password = 'Password must be at least 8 characters.'
      }
      if (this.form.password !== this.form.confirm_password) {
        this.errors.confirm_password = 'Passwords do not match.'
      }
      if (Object.keys(this.errors).length) {
        return
      }

      this.loading = true
      try {
        const response = await authService.register(this.form)
        if (response.data.success) {
          this.serverMessage = response.data.message
          this.form.password = ''
          this.form.confirm_password = ''
        }
      } catch (error) {
        const data = error.response?.data
        this.serverError = data?.message || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.auth-page {
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.text-panel {
  background: #ffffff;
}

.text-content {
  max-width: 440px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
  font-size: 0.85rem;
  color: #0d6efd;
}

.image-panel {
  min-height: 320px;
  background: url('/cartoon-style-character-traveling_23-2151129769.avif') no-repeat center center / cover;
}

@media (max-width: 991.98px) {
  .image-panel {
    order: -1;
    min-height: 240px;
  }

  .text-content {
    max-width: none;
  }
}
</style>