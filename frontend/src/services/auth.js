import http from './http.js'

const storageKeys = {
  token: 'trekscape_token',
  userId: 'trekscape_user_id',
  role: 'trekscape_user_role',
  fullName: 'trekscape_user_name',
}

function saveUserData(user, token) {
  localStorage.setItem(storageKeys.token, token)
  localStorage.setItem(storageKeys.userId, String(user.id))
  localStorage.setItem(storageKeys.role, user.role)
  localStorage.setItem(storageKeys.fullName, user.full_name)
}

function clearUserData() {
  localStorage.removeItem(storageKeys.token)
  localStorage.removeItem(storageKeys.userId)
  localStorage.removeItem(storageKeys.role)
  localStorage.removeItem(storageKeys.fullName)
}

export default {
  login(payload) {
    return http.post('/auth/login', payload).then((response) => {
      if (response.data.success && response.data.access_token && response.data.user) {
        saveUserData(response.data.user, response.data.access_token)
      }
      return response
    })
  },
  register(payload) {
    return http.post('/auth/register', payload)
  },
  logout() {
    clearUserData()
  },
  getCurrentUser() {
    const id = localStorage.getItem(storageKeys.userId)
    const role = localStorage.getItem(storageKeys.role)
    const full_name = localStorage.getItem(storageKeys.fullName)
    const token = localStorage.getItem(storageKeys.token)
    if (!id || !token) {
      return null
    }
    return { id, role, full_name, token }
  },
  isAuthenticated() {
    return !!localStorage.getItem(storageKeys.token)
  },
}
