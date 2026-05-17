import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { getSession, setSession, clearSession } from '../utils/session.js'
import { ROUTES } from '../constants/app.js'

export function useAuth() {
  const router = useRouter()

  const session = computed(() => getSession())
  const isAuthenticated = computed(() => !!session.value)
  const user = computed(() => session.value)
  const role = computed(() => session.value?.role ?? null)

  function login({ email, name, role: userRole }) {
    setSession({
      email: email.trim(),
      name: name || email.split('@')[0],
      role: userRole,
      loggedInAt: new Date().toISOString(),
    })
    if (userRole === 'teacher') router.push(ROUTES.TEACHER_DASHBOARD)
    else router.push(ROUTES.STUDENT_DASHBOARD)
  }

  function register({ name, email, password, role: userRole }) {
    setSession({
      email: email.trim(),
      name: name.trim(),
      role: userRole,
      registeredAt: new Date().toISOString(),
    })
    if (userRole === 'teacher') router.push(ROUTES.TEACHER_DASHBOARD)
    else router.push(ROUTES.STUDENT_DASHBOARD)
  }

  function logout() {
    clearSession()
    router.push(ROUTES.LOGIN)
  }

  return {
    session,
    isAuthenticated,
    user,
    role,
    login,
    register,
    logout,
  }
}
