<template>
  <div class="auth-page d-flex align-items-center min-vh-100 py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-12 col-md-10 col-lg-8">
          <div class="card shadow-sm border-0 text-center p-5">
            <h1 class="mb-3">Welcome to TrekScape</h1>
            <p class="lead text-muted mb-4">Your adventure portal for treks, ticketing, and guides.</p>
            <div class="d-grid gap-3 d-sm-flex justify-content-sm-center">
              <router-link class="btn btn-primary btn-lg" to="/login">Login</router-link>
              <router-link class="btn btn-outline-primary btn-lg" to="/register">Register</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
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
