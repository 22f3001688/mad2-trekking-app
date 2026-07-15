<template>
  <div class="auth-page min-vh-100">
    <div class="row g-0 min-vh-100 align-items-stretch">
      <div class="col-12 col-lg-6 d-flex align-items-center justify-content-center text-panel">
        <div class="text-content px-4 px-md-5 py-5">
          <p class="eyebrow mb-2">Adventure Awaits</p>
          <h1 class="display-5 fw-bold mb-3">Welcome to TrekScape</h1>
          <p class="lead text-muted mb-4">Your adventure portal for treks, ticketing, and guides.</p>
          <div class="d-grid gap-3 d-sm-flex">
            <router-link class="btn btn-primary btn-lg" to="/login">Login</router-link>
            <router-link class="btn btn-outline-primary btn-lg" to="/register">Register</router-link>
          </div>
        </div>
      </div>
      <div class="col-12 col-lg-6 image-panel" aria-hidden="true"></div>
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

.text-panel {
  background: #ffffff;
}

.text-content {
  max-width: 520px;
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
    min-height: 260px;
  }

  .text-content {
    max-width: none;
    text-align: center;
  }

  .text-content .d-sm-flex {
    justify-content: center;
  }
}
</style>
