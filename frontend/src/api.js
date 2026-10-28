import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('sf_token')
  if (token) cfg.headers.Authorization = 'Bearer ' + token
  return cfg
})

api.interceptors.response.use(
  (r) => r,
  (e) => {
    if (e.response && e.response.status === 401) {
      localStorage.removeItem('sf_token')
      localStorage.removeItem('sf_user')
    }
    return Promise.reject(e)
  }
)

export function errorText(e) {
  const d = e && e.response && e.response.data
  if (d && d.message) return d.message
  return 'Something went wrong'
}

export default api
