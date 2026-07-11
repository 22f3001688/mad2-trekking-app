<template>
  <DashboardLayout>
    <div class="trek-history-page">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
        <div>
          <p class="text-uppercase text-muted fw-semibold mb-1">Trekker Operations</p>
          <h1 class="h3 mb-1">Trekking History</h1>
          <p class="text-muted mb-0">Completed and cancelled bookings are listed here.</p>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button class="btn btn-primary" type="button" :disabled="exportInProgress" @click="startExport">
            <span v-if="exportInProgress" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
            Export History as CSV
          </button>
          <router-link class="btn btn-outline-secondary" :to="{ name: 'TrekkerMyBookings' }">
            <i class="bi bi-calendar2-check me-1"></i>
            Back to My Bookings
          </router-link>
        </div>
      </div>

      <div v-if="exportStatus" class="alert mt-0" :class="exportAlertClass()" role="alert">
        <div v-if="exportStatus === 'PENDING' || exportStatus === 'STARTED'" class="d-flex align-items-center gap-2">
          <div class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div>
          <span>Preparing your booking history export...</span>
        </div>
        <div v-else>
          <p class="mb-0">{{ exportMessage }}</p>
          <button v-if="exportStatus === 'SUCCESS'" type="button" class="btn btn-sm btn-light mt-3" :disabled="downloading" @click="downloadExport">
            <span v-if="downloading" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
            Download CSV
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status" aria-hidden="true"></div>
        <p class="text-muted mb-0">Loading history…</p>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else-if="history.length === 0" class="card shadow-sm border-0">
        <div class="card-body text-center py-5">
          <div class="empty-icon rounded-circle bg-light text-muted d-inline-flex align-items-center justify-content-center mb-3">
            <i class="bi bi-clock-history fs-3"></i>
          </div>
          <h2 class="h5 mb-2">No history found</h2>
          <p class="text-muted mb-0">Completed and cancelled bookings will appear here.</p>
        </div>
      </div>

      <div v-else class="card shadow-sm border-0">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table align-middle mb-0">
              <thead>
                <tr>
                  <th scope="col">Trek Name</th>
                  <th scope="col">Location</th>
                  <th scope="col">Dates</th>
                  <th scope="col">Final Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="entry in history" :key="entry.id">
                  <td class="fw-semibold">{{ entry.trek_name }}</td>
                  <td>{{ entry.location }}</td>
                  <td>{{ formatDates(entry.start_date, entry.end_date) }}</td>
                  <td>
                    <span class="badge text-capitalize" :class="statusBadgeClass(entry.final_status)">{{ entry.final_status }}</span>
                  </td>
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
  name: 'TrekHistory',
  components: { DashboardLayout },
  data() {
    return {
      history: [],
      loading: true,
      error: '',
      exportTaskId: '',
      exportStatus: '',
      exportMessage: '',
      exportFilename: '',
      exportInProgress: false,
      downloading: false,
      exportPollingTimer: null,
    }
  },
  mounted() {
    this.fetchHistory()
  },
  beforeUnmount() {
    this.clearExportPolling()
  },
  methods: {
    clearExportPolling() {
      if (this.exportPollingTimer) {
        clearTimeout(this.exportPollingTimer)
        this.exportPollingTimer = null
      }
    },
    scheduleExportStatusPoll() {
      this.clearExportPolling()
      if (!this.exportTaskId || !this.exportInProgress) {
        return
      }

      this.exportPollingTimer = window.setTimeout(() => {
        this.pollExportStatus()
      }, 2000)
    },
    async fetchHistory() {
      this.loading = true
      this.error = ''
      try {
        const response = await http.get('/trekker/history')
        if (response.data?.success) {
          this.history = response.data.data || []
        } else {
          this.error = response.data?.message || 'Unable to load history.'
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Unable to load history.'
      } finally {
        this.loading = false
      }
    },
    exportAlertClass() {
      switch (this.exportStatus) {
        case 'SUCCESS':
          return 'alert-success'
        case 'FAILURE':
          return 'alert-danger'
        default:
          return 'alert-info'
      }
    },
    async startExport() {
      if (this.exportInProgress) {
        return
      }

      this.clearExportPolling()
      this.error = ''
      this.exportTaskId = ''
      this.exportStatus = 'PENDING'
      this.exportMessage = 'Preparing your booking history export...'
      this.exportFilename = ''
      this.exportInProgress = true

      try {
        const response = await http.post('/trekker/history/export')
        if (response.data?.success) {
          this.exportTaskId = response.data.data?.task_id || ''
          this.exportStatus = response.data.data?.status || 'PENDING'
          this.exportMessage = response.data.message || 'Booking history export started'
          this.scheduleExportStatusPoll()
        } else {
          this.exportStatus = 'FAILURE'
          this.exportMessage = response.data?.message || 'Unable to start booking history export.'
          this.exportInProgress = false
        }
      } catch (err) {
        this.exportStatus = 'FAILURE'
        this.exportMessage = err.response?.data?.message || 'Unable to start booking history export.'
        this.exportInProgress = false
      }
    },
    async pollExportStatus() {
      if (!this.exportTaskId || !this.exportInProgress) {
        return
      }

      try {
        const response = await http.get(`/trekker/history/export/${this.exportTaskId}/status`)
        if (response.data?.success) {
          const status = response.data.data?.status || 'PENDING'
          this.exportStatus = status
          this.exportMessage = response.data.message || this.exportMessage

          if (status === 'SUCCESS') {
            this.exportFilename = response.data.data?.filename || ''
            this.exportInProgress = false
            this.clearExportPolling()
          } else if (status === 'FAILURE') {
            this.exportInProgress = false
            this.clearExportPolling()
          } else {
            this.scheduleExportStatusPoll()
          }
        } else {
          this.exportStatus = 'FAILURE'
          this.exportMessage = response.data?.message || 'Unable to check export status.'
          this.exportInProgress = false
          this.clearExportPolling()
        }
      } catch (err) {
        this.exportStatus = 'FAILURE'
        this.exportMessage = err.response?.data?.message || 'Unable to check export status.'
        this.exportInProgress = false
        this.clearExportPolling()
      }
    },
    resolveDownloadFilename(contentDisposition) {
      if (!contentDisposition) {
        return this.exportFilename || 'booking_history.csv'
      }

      const filenameMatch = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i.exec(contentDisposition)
      const rawFilename = filenameMatch?.[1] || filenameMatch?.[2]
      return rawFilename ? decodeURIComponent(rawFilename) : this.exportFilename || 'booking_history.csv'
    },
    async downloadExport() {
      if (!this.exportTaskId) {
        return
      }

      this.downloading = true
      try {
        const response = await http.get(`/trekker/history/export/${this.exportTaskId}/download`, {
          responseType: 'blob',
        })
        const blob = new Blob([response.data], {
          type: response.headers['content-type'] || 'text/csv',
        })
        const downloadUrl = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = this.resolveDownloadFilename(response.headers['content-disposition'])
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(downloadUrl)
      } catch (err) {
        this.error = 'Unable to download booking history export.'
      } finally {
        this.downloading = false
      }
    },
    formatDate(value) {
      if (!value) return '—'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
    },
    formatDates(startDate, endDate) {
      return `${this.formatDate(startDate)} - ${this.formatDate(endDate)}`
    },
    statusBadgeClass(status) {
      switch (status) {
        case 'completed': return 'bg-primary-subtle text-primary-emphasis'
        case 'cancelled': return 'bg-secondary-subtle text-secondary-emphasis'
        default: return 'bg-light text-dark'
      }
    },
  },
}
</script>

<style scoped>
.trek-history-page { width: 100%; }
.empty-icon { width: 64px; height: 64px; }
</style>
