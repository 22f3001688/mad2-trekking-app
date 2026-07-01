<template>
  <div class="container py-5">
    <div class="card shadow-sm">
      <div class="card-body">
        <h2 class="card-title">Staff Dashboard</h2>
        <p class="card-text">This is a protected Staff page placeholder.</p>
        <p class="text-muted">Signed in as {{ currentUser.full_name }}</p>
        <button class="btn btn-outline-secondary" @click="logout">Logout</button>
      </div>
    </div>
  </div>
</template>

<script>
import authService from '../services/auth.js'

export default {
  name: 'StaffDashboard',
  data() {
    return {
      currentUser: authService.getCurrentUser() || {},
    }
  },
  methods: {
    logout() {
      authService.logout()
      this.$router.push('/login')
    },
  },
}
</script>
