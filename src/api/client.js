import axios from 'axios'
import { getSession, clearSession } from '../utils/session.js'

const AUTH_PATHS = ['/auth/login', '/auth/register']

function isAuthRequest(url = '') {
  return AUTH_PATHS.some((p) => url.includes(p))
}

/** Dev uses Vite proxy (/api) unless VITE_API_DIRECT=true (avoids CORS). */
export function getApiBaseUrl() {
  const envUrl = (import.meta.env.VITE_API_URL || '').trim().replace(/\/$/, '')
  if (import.meta.env.DEV && import.meta.env.VITE_API_DIRECT !== 'true') {
    return '/api'
  }
  if (!envUrl) return '/api'
  if (envUrl.endsWith('/api')) return envUrl
  return `${envUrl}/api`
}

export const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  timeout: 120000,
})

api.interceptors.request.use((config) => {
  if (isAuthRequest(config.url)) {
    return config
  }
  const session = getSession()
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const url = err.config?.url || ''
    if (err.response?.status === 401 && !isAuthRequest(url)) {
      clearSession()
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)

export function getErrorMessage(err, fallback = 'حدث خطأ غير متوقع') {
  if (!err.response) {
    if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
      return 'تعذر الاتصال بالخادم. تأكد أن FastAPI يعمل على http://127.0.0.1:8000'
    }
    return err.message || fallback
  }
  const detail = err.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((d) => d.msg || d).join('، ')
  return fallback
}
