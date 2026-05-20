import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { loginApi, registerApi } from '../api/auth.js'
import { getErrorMessage } from '../api/client.js'
import { getSession, setSession, clearSession, isApiMode } from '../utils/session.js'
import { ROUTES } from '../constants/app.js'

export function useAuth() {
  const router = useRouter()

  const session = computed(() => getSession())
  const isAuthenticated = computed(() =>
    isApiMode()
      ? !!session.value?.accessToken
      : !!(session.value?.accessToken || session.value?.loggedInAt),
  )
  const user = computed(() => session.value)
  const role = computed(() => session.value?.role ?? null)

  function persistAndRedirect({ user: u, accessToken }, selectedRole) {
    if (!u?.email) {
      throw new Error('استجابة غير صالحة من الخادم')
    }
    if (selectedRole && u.role && u.role !== selectedRole) {
      throw new Error(
        u.role === 'teacher'
          ? 'هذا الحساب للمعلم. اختر «معلم» أو استخدم حساب الطالب.'
          : 'هذا الحساب للطالب. اختر «طالب» أو استخدم حساب المعلم.',
      )
    }
    if (!accessToken) {
      throw new Error('لم يُرجع الخادم رمز الدخول')
    }

    setSession({
      id: u.id,
      email: u.email,
      name: u.name,
      role: u.role,
      accessToken,
      loggedInAt: new Date().toISOString(),
    })

    const target =
      u.role === 'teacher' ? ROUTES.TEACHER_DASHBOARD : ROUTES.STUDENT_DASHBOARD
    return router.push(target)
  }

  async function login({ email, password, name, role: userRole }) {
    if (isApiMode()) {
      clearSession()
      const data = await loginApi({ email, password })
      await persistAndRedirect(data, userRole)
      return
    }
    setSession({
      email: email.trim(),
      name: name || email.split('@')[0],
      role: userRole,
      loggedInAt: new Date().toISOString(),
    })
    if (userRole === 'teacher') await router.push(ROUTES.TEACHER_DASHBOARD)
    else await router.push(ROUTES.STUDENT_DASHBOARD)
  }

  async function register({ name, email, password, role: userRole }) {
    if (isApiMode()) {
      clearSession()
      const data = await registerApi({ name, email, password, role: userRole })
      await persistAndRedirect(data, userRole)
      return
    }
    setSession({
      email: email.trim(),
      name: name.trim(),
      role: userRole,
      registeredAt: new Date().toISOString(),
    })
    if (userRole === 'teacher') await router.push(ROUTES.TEACHER_DASHBOARD)
    else await router.push(ROUTES.STUDENT_DASHBOARD)
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
    getErrorMessage,
  }
}
