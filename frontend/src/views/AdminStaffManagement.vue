<template>
  <DashboardLayout>
    <div class="staff-management-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Admin Operations</p>
          <h1 class="h3 mb-1">Staff Management</h1>
          <p class="text-muted mb-0">Create, update, and deactivate trekking staff accounts.</p>
        </div>
        <div class="d-flex align-items-center gap-2">
          <router-link class="btn btn-outline-secondary btn-sm" :to="{ name: 'AdminDashboard' }">
            <i class="bi bi-arrow-left me-1"></i>
            Back to Dashboard
          </router-link>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-lg-4">
          <div class="card shadow-sm border-0 h-100">
            <div class="card-body">
              <h2 class="h5 mb-3">{{ editingStaff ? 'Edit Staff Member' : 'Add Staff Member' }}</h2>
              <form @submit.prevent="submitStaff">
                <div class="mb-3">
                  <label class="form-label">Full name</label>
                  <input v-model="form.full_name" class="form-control" required />
                </div>

                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input v-model="form.email" type="email" class="form-control" required />
                </div>

                <div class="mb-3">
                  <label class="form-label">Phone</label>
                  <input v-model="form.phone" class="form-control" />
                </div>

                <div class="mb-3" v-if="!editingStaff">
                  <label class="form-label">Temporary password</label>
                  <input v-model="form.password" type="password" class="form-control" required />
                </div>

                <div class="mb-3">
                  <label class="form-label">Experience years</label>
                  <input v-model="form.experience_years" type="number" min="0" class="form-control" />
                </div>

                <div class="mb-3">
                  <label class="form-label">Specialization</label>
                  <input v-model="form.specialization" class="form-control" />
                </div>

                <div class="mb-3">
                  <label class="form-label">Emergency contact</label>
                  <input v-model="form.emergency_contact" class="form-control" />
                </div>

                <div class="mb-3">
                  <label class="form-label">Status</label>
                  <select v-model="form.status" class="form-select">
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>

                <div class="d-flex gap-2">
                  <button class="btn btn-primary" :disabled="submitting">
                    <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    {{ editingStaff ? 'Save changes' : 'Create staff' }}
                  </button>
                  <button class="btn btn-outline-secondary" type="button" @click="resetForm">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <div class="col-lg-8">
          <div class="card shadow-sm border-0">
            <div class="card-body">
              <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-2 mb-3">
                <div>
                  <h2 class="h5 mb-1">Staff directory</h2>
                  <p class="text-muted small mb-0">Manage your active staff roster from one place.</p>
                </div>
                <span class="badge bg-primary-subtle text-primary-emphasis">{{ staffList.length }} members</span>
              </div>

              <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary mb-3" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="text-muted mb-0">Loading staff records…</p>
              </div>

              <div v-else-if="error" class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                {{ error }}
              </div>

              <div v-else-if="staffList.length === 0" class="text-center py-4 text-muted">
                No staff accounts have been created yet.
              </div>

              <div v-else class="table-responsive">
                <table class="table align-middle">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Specialization</th>
                      <th>Status</th>
                      <th class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="staff in staffList" :key="staff.id">
                      <td>
                        <div class="fw-semibold">{{ staff.full_name }}</div>
                        <div class="small text-muted">{{ staff.phone || 'No phone' }}</div>
                      </td>
                      <td>{{ staff.email }}</td>
                      <td>{{ staff.staff_profile?.specialization || '—' }}</td>
                      <td>
                        <span class="badge" :class="staff.is_active ? 'bg-success-subtle text-success-emphasis' : 'bg-secondary-subtle text-secondary-emphasis'">
                          {{ staff.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary me-2" @click="editStaff(staff)">
                          Edit
                        </button>
                        <button class="btn btn-sm btn-outline-danger" :disabled="!staff.is_active" @click="deactivateStaff(staff.id)">
                          Deactivate
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
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
  components: { DashboardLayout },
  name: 'AdminStaffManagement',
  data() {
    return {
      loading: true,
      submitting: false,
      error: '',
      staffList: [],
      editingStaff: null,
      form: this.createForm(),
    }
  },
  mounted() {
    this.fetchStaff()
  },
  methods: {
    createForm() {
      return {
        full_name: '',
        email: '',
        phone: '',
        password: '',
        experience_years: '',
        specialization: '',
        emergency_contact: '',
        status: 'active',
        is_active: true,
      }
    },
    resetForm() {
      this.editingStaff = null
      this.form = this.createForm()
      this.error = ''
    },
    editStaff(staff) {
      this.editingStaff = staff
      this.form = {
        full_name: staff.full_name || '',
        email: staff.email || '',
        phone: staff.phone || '',
        password: '',
        experience_years: staff.staff_profile?.experience_years ?? '',
        specialization: staff.staff_profile?.specialization || '',
        emergency_contact: staff.staff_profile?.emergency_contact || '',
        status: staff.staff_profile?.status || 'active',
        is_active: staff.is_active,
      }
      this.error = ''
    },
    async fetchStaff() {
      this.loading = true
      this.error = ''

      try {
        const response = await http.get('/admin/staff')
        if (response.data?.success) {
          this.staffList = response.data.data || []
        } else {
          this.error = response.data?.message || 'Unable to load staff members.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load staff members.'
      } finally {
        this.loading = false
      }
    },
    async submitStaff() {
      this.submitting = true
      this.error = ''

      const payload = {
        ...this.form,
        experience_years: this.form.experience_years === '' ? null : Number(this.form.experience_years),
      }

      try {
        let response
        if (this.editingStaff) {
          response = await http.put(`/admin/staff/${this.editingStaff.id}`, payload)
        } else {
          response = await http.post('/admin/staff', payload)
        }

        if (response.data?.success) {
          this.resetForm()
          await this.fetchStaff()
        } else {
          this.error = response.data?.message || 'Unable to save staff member.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to save staff member.'
      } finally {
        this.submitting = false
      }
    },
    async deactivateStaff(staffId) {
      this.error = ''
      try {
        const response = await http.delete(`/admin/staff/${staffId}`)
        if (response.data?.success) {
          await this.fetchStaff()
        } else {
          this.error = response.data?.message || 'Unable to deactivate staff member.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to deactivate staff member.'
      }
    },
  },
}
</script>

<style scoped>
.staff-management-page {
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}
</style>
