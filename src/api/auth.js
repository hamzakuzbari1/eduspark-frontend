import { api } from './client.js'

/** Map FastAPI TokenResponse (snake_case) to app session shape. */
export function normalizeAuthResponse(data) {
  if (!data?.user) {
    throw new Error('استجابة غير صالحة من الخادم')
  }
  return {
    accessToken: data.access_token ?? data.accessToken ?? null,
    user: data.user,
  }
}

export async function loginApi({ email, password }) {
  const { data } = await api.post('/auth/login', {
    email: String(email).trim().toLowerCase(),
    password,
  })
  return normalizeAuthResponse(data)
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
