<template>
  <div class="auth-page d-flex align-items-center min-vh-100 py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-12 col-md-10 col-lg-8">
          <div class="card shadow-sm border-0">
            <div class="row g-0">
              <div class="col-lg-5 bg-light d-none d-lg-flex align-items-center justify-content-center p-4">
                <div class="text-center">
                  <h3 class="mb-3">TrekScape</h3>
                  <p class="text-muted">Welcome back. Please sign in to continue your trekking adventures.</p>
                </div>
              </div>
              <div class="col-lg-7 p-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <div>
                    <h4 class="mb-1">Login</h4>
                    <small class="text-muted">Access your TrekScape account</small>
                  </div>
                </div>

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

                  <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Login
                  </button>
                </form>

                <div class="mt-4 text-center">
                  <p class="mb-0 text-muted">Don't have an account? <router-link to="/register">Register as Trekker</router-link></p>
                </div>
              </div>
            </div>
          </div>
          <div class="text-center mt-3 text-muted small">
            Only users (Trekkers) may register themselves. Trekking staff are created by admin.
          </div>
        </div>
      </div>
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
.card {
  border-radius: 1rem;
}
</style>