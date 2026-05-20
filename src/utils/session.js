const SESSION_KEY = 'eduspark_session'
const PROFILE_KEY = 'eduspark_student_profile'
const LEGACY_SESSION_KEY = 'edumind_session'
const LEGACY_PROFILE_KEY = 'edumind_student_profile'

function migrateLegacyKey(legacyKey, newKey) {
  const legacy = localStorage.getItem(legacyKey)
  if (legacy && !localStorage.getItem(newKey)) {
    localStorage.setItem(newKey, legacy)
    localStorage.removeItem(legacyKey)
  }
}

export function getSession() {
  migrateLegacyKey(LEGACY_SESSION_KEY, SESSION_KEY)
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function setSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY)
  localStorage.removeItem(LEGACY_SESSION_KEY)
}

export function getStudentProfilePrefs() {
  migrateLegacyKey(LEGACY_PROFILE_KEY, PROFILE_KEY)
  try {
    const raw = localStorage.getItem(PROFILE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function setStudentProfilePrefs(prefs) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(prefs))
}

export function isApiMode() {
  return import.meta.env.VITE_USE_MOCK !== 'true'
}
