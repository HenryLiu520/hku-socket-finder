import { defineStore } from 'pinia'
import api from '../api'

export const useAuth = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('sf_token') || '',
    user: JSON.parse(localStorage.getItem('sf_user') || 'null')
  }),
  getters: {
    signedIn: (s) => !!s.token,
    isMaintenance: (s) => !!s.user && s.user.role === 'MAINTENANCE'
  },
  actions: {
    async login(email, password) {
      const { data } = await api.post('/auth/login', { email, password })
      this.token = data.token
      this.user = { email: data.email, displayName: data.displayName, role: data.role }
      localStorage.setItem('sf_token', this.token)
      localStorage.setItem('sf_user', JSON.stringify(this.user))
      return data
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('sf_token')
      localStorage.removeItem('sf_user')
    }
  }
})
