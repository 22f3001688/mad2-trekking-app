<template>
  <DashboardLayout>
    <div class="admin-users-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Admin Operations</p>
          <h1 class="h3 mb-1">Platform Users</h1>
          <p class="text-muted mb-0">Summary of all users registered on TrekScape.</p>
        </div>
        <router-link class="btn btn-outline-secondary" :to="{ name: 'AdminDashboard' }">
          <i class="bi bi-arrow-left me-1"></i>
          Back to Dashboard
        </router-link>
      </div>

      <div class="card shadow-sm border-0 mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-end">
            <div class="col-12 col-md-6 col-lg-5">
              <label class="form-label small text-muted">Search</label>
              <input
                v-model.trim="filters.search"
                class="form-control"
                placeholder="Search by name, email, or phone"
                @input="fetchUsers"
              />
            </div>
            <div class="col-12 col-md-3 col-lg-3">
              <label class="form-label small text-muted">Role</label>
              <select v-model="filters.role" class="form-select" @change="fetchUsers">
                <option value="">All roles</option>
                <option value="admin">Admin</option>
                <option value="staff">Staff</option>
                <option value="trekker">Trekker</option>
              </select>
            </div>
            <div class="col-12 col-md-3 col-lg-3">
              <label class="form-label small text-muted">Status</label>
              <select v-model="filters.status" class="form-select" @change="fetchUsers">
                <option value="">All statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="blacklisted">Blacklisted</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted mb-0">Loading users…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        {{ error }}
      </div>

      <div v-else class="card shadow-sm border-0">
        <div class="card-body">
          <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
            <h2 class="h5 mb-0">Users Summary</h2>
            <span class="badge bg-primary-subtle text-primary-emphasis">{{ users.length }} users</span>
          </div>

          <div v-if="users.length === 0" class="text-center py-5 text-muted">
            No users found for the selected filters.
          </div>

          <div v-else class="table-responsive">
            <table class="table align-middle mb-0">
              <thead>
                <tr>
                  <th scope="col">Name</th>
                  <th scope="col">Email</th>
                  <th scope="col">Phone</th>
                  <th scope="col">Role</th>
                  <th scope="col">Account Status</th>
                  <th scope="col">Created</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td class="fw-semibold">{{ user.full_name }}</td>
                  <td>{{ user.email }}</td>
                  <td>{{ user.phone || '—' }}</td>
                  <td>
                    <span class="badge text-capitalize" :class="roleBadgeClass(user.role)">
                      {{ user.role }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="statusBadgeClass(user)">
                      {{ statusText(user) }}
                    </span>
                  </td>
                  <td>{{ formatDateTime(user.created_at) }}</td>
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
  name: 'AdminUsersSummary',
  components: { DashboardLayout },
  data() {
    return {
      loading: true,
      error: '',
      users: [],
      filters: {
        search: '',
        role: '',
        status: '',
      },
    }
  },
  mounted() {
    this.fetchUsers()
  },
  methods: {
    async fetchUsers() {
      this.loading = true
      this.error = ''

      try {
        const params = new URLSearchParams()
        if (this.filters.search) params.append('search', this.filters.search)
        if (this.filters.role) params.append('role', this.filters.role)
        if (this.filters.status) params.append('status', this.filters.status)

        const query = params.toString()
        const response = await http.get(`/admin/users${query ? `?${query}` : ''}`)

        if (response.data?.success) {
          this.users = response.data.data || []
        } else {
          this.error = response.data?.message || 'Unable to load users summary.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load users summary.'
      } finally {
        this.loading = false
      }
    },
    formatDateTime(value) {
      if (!value) return '—'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return date.toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    },
    statusText(user) {
      if (user.is_blacklisted) return 'Blacklisted'
      return user.is_active ? 'Active' : 'Inactive'
    },
    roleBadgeClass(role) {
      switch ((role || '').toLowerCase()) {
        case 'admin':
          return 'bg-danger-subtle text-danger-emphasis'
        case 'staff':
          return 'bg-info-subtle text-info-emphasis'
        case 'trekker':
          return 'bg-success-subtle text-success-emphasis'
        default:
          return 'bg-secondary-subtle text-secondary-emphasis'
      }
    },
    statusBadgeClass(user) {
      if (user.is_blacklisted) {
        return 'bg-dark-subtle text-dark-emphasis'
      }
      return user.is_active
        ? 'bg-success-subtle text-success-emphasis'
        : 'bg-secondary-subtle text-secondary-emphasis'
    },
  },
}
</script>

<style scoped>
.admin-users-page {
  width: 100%;
}
</style>
