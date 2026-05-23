import { api } from './client.js'

/** Map FastAPI TokenResponse (snake_case) to app session shape. */
export function normalizeAuthResponse(data) {
  if (!data || typeof data !== 'object') {
    throw new Error('استجابة غير صالحة من الخادم')
  }

  const accessToken = data.access_token ?? data.accessToken ?? null
  const user = data.user ?? data.User ?? null

  if (!user || typeof user !== 'object') {
    throw new Error('استجابة غير صالحة: بيانات المستخدم مفقودة')
  }
  if (!accessToken) {
    throw new Error('استجابة غير صالحة: رمز الدخول مفقود')
  }

  const role = user.role ?? user.Role
  if (!role) {
    throw new Error('استجابة غير صالحة: نوع الحساب مفقود')
  }

  return {
    accessToken,
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
      role: String(role).toLowerCase(),
    },
  }
}

export async function loginApi({ email, password }) {
  try {
    const { data } = await api.post(
      '/auth/login',
      {
        email: String(email).trim().toLowerCase(),
        password,
      },
      { timeout: 30000 },
    )
    return normalizeAuthResponse(data)
  } catch (err) {
    if (import.meta.env.DEV) {
      console.error(
        '[loginApi]',
        err?.response?.status,
        err?.response?.data,
        'baseURL=',
        err?.config?.baseURL,
        'url=',
        err?.config?.url,
      )
    }
    throw err
  }
}

export async function registerApi({ name, email, password, role }) {
  const { data } = await api.post('/auth/register', {
    name: name.trim(),
    email: String(email).trim().toLowerCase(),
    password,
    role,
  })
  return normalizeAuthResponse(data)
}
