import axios from 'axios'
import { getSession, clearSession } from '../utils/session.js'

const AUTH_PATHS = ['/auth/login', '/auth/register', 'auth/login', 'auth/register']

function isAuthRequest(url = '') {
  const path = String(url).replace(/\?.*$/, '')
  return AUTH_PATHS.some((p) => path === p || path.endsWith(p))
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
  const url = config.url || ''
  if (isAuthRequest(url)) {
    delete config.headers.Authorization
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

function formatValidationDetail(detail) {
  if (!Array.isArray(detail)) return null
  return detail
    .map((d) => {
      if (typeof d === 'string') return d
      if (d && typeof d === 'object') {
        const loc = Array.isArray(d.loc) ? d.loc.filter((x) => x !== 'body').join('.') : ''
        const msg = d.msg || d.message || JSON.stringify(d)
        return loc ? `${loc}: ${msg}` : msg
      }
      return String(d)
    })
    .join('، ')
}

export function getErrorMessage(err, fallback = 'حدث خطأ غير متوقع') {
  if (!err?.response) {
    if (err?.code === 'ERR_NETWORK' || err?.message === 'Network Error') {
      const base = getApiBaseUrl()
      return `تعذر الاتصال بالخادم (${base}). تأكد أن FastAPI يعمل على المنفذ 8000 وأن Vite proxy مفعّل.`
    }
    if (err?.code === 'ECONNABORTED' || String(err?.message || '').includes('timeout')) {
      return 'انتهت مهلة الاتصال بالخادم'
    }
    if (String(err?.message || '').includes('JSON')) {
      return 'استجابة غير صالحة من الخادم — تحقق من عنوان API ومسار /api'
    }
    return err?.message || fallback
  }

  const data = err.response?.data
  const detail = data?.detail ?? data?.message

  if (typeof detail === 'string' && detail.trim()) return detail

  const validation = formatValidationDetail(detail)
  if (validation) return validation

  if (typeof data === 'string' && data.trim()) return data

  if (import.meta.env.DEV) {
    console.error('[API error]', err.response.status, data, err.config?.baseURL, err.config?.url)
  }

  return fallback
}
