<template>
  <div class="auth-page min-vh-100">
    <div class="row g-0 min-vh-100 align-items-stretch">
      <div class="col-12 col-lg-6 d-flex align-items-center justify-content-center text-panel">
        <div class="text-content px-4 px-md-5 py-5 w-100">
          <p class="eyebrow mb-2">Welcome Back</p>
          <h4 class="mb-1">Login</h4>
          <small class="text-muted d-block mb-4">Access your TrekScape account</small>

          <form @submit.prevent="submitLogin" novalidate>
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
                placeholder="Enter your password"
              />
              <div class="invalid-feedback">{{ errors.password }}</div>
            </div>

            <div v-if="serverError" class="alert alert-danger mt-2">{{ serverError }}</div>

            <button type="submit" class="btn btn-primary w-100 btn-lg mt-2" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Login
            </button>
          </form>

          <div class="mt-4 text-center">
            <p class="mb-0 text-muted">Don't have an account? <router-link to="/register">Register as Trekker</router-link></p>
          </div>
          <div class="text-center mt-3 text-muted small">
            Only users (Trekkers) may register themselves. Trekking staff are created by admin.
          </div>
        </div>
      </div>
      <div class="col-12 col-lg-6 image-panel" aria-hidden="true"></div>
    </div>
  </div>
</template>

<script>
import authService from '../services/auth.js'
import { getDashboardRouteForRole } from '../router'

export default {
  name: 'Login',
  data() {
    return {
      form: {
        email: '',
        password: '',
      },
      errors: {},
      serverError: '',
      loading: false,
    }
  },
  methods: {
    async submitLogin() {
      this.errors = {}
      this.serverError = ''

      if (!this.form.email) {
        this.errors.email = 'Email is required.'
      }
      if (!this.form.password) {
        this.errors.password = 'Password is required.'
      }
      if (Object.keys(this.errors).length) {
        return
      }

      this.loading = true
      try {
        const response = await authService.login(this.form)
        if (response.data.success) {
          this.$router.push(getDashboardRouteForRole(response.data.user?.role))
        }
      } catch (error) {
        const data = error.response?.data
        this.serverError = data?.message || 'Login failed. Please try again.'
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