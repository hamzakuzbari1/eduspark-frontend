import { createRouter, createWebHistory } from 'vue-router'
import { getSession } from '../utils/session.js'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { title: 'تسجيل الدخول', guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
    meta: { title: 'إنشاء حساب', guest: true },
  },
  {
    path: '/teacher',
    component: () => import('../layouts/TeacherLayout.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      {
        path: '',
        redirect: { name: 'teacher-dashboard' },
      },
      {
        path: 'dashboard',
        name: 'teacher-dashboard',
        component: () => import('../views/TeacherDashboardView.vue'),
        meta: { title: 'لوحة المعلم' },
      },
      {
        path: 'upload',
        name: 'upload-lesson',
        component: () => import('../views/UploadLessonView.vue'),
        meta: { title: 'رفع درس جديد' },
      },
    ],
  },
  {
    path: '/student',
    component: () => import('../layouts/StudentLayout.vue'),
    meta: { requiresAuth: true, role: 'student' },
    children: [
      {
        path: '',
        redirect: { name: 'student-dashboard' },
      },
      {
        path: 'dashboard',
        name: 'student-dashboard',
        component: () => import('../views/student/StudentDashboardView.vue'),
        meta: { title: 'دروسي' },
      },
      {
        path: 'lesson/:id',
        name: 'student-lesson',
        component: () => import('../views/student/StudentLessonView.vue'),
        meta: { title: 'جلسة التعلّم' },
        props: true,
      },
      {
        path: 'profile',
        name: 'student-profile',
        component: () => import('../views/student/StudentProfileView.vue'),
        meta: { title: 'الملف الشخصي' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth', top: 80 }
    }
    return { top: 0, behavior: 'smooth' }
  },
})

router.beforeEach((to) => {
  const session = getSession()
  const isAuth = !!session

  if (to.meta.guest && isAuth) {
    return session.role === 'teacher'
      ? { name: 'teacher-dashboard' }
      : { name: 'student-dashboard' }
  }

  if (to.meta.requiresAuth && !isAuth) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.role && session?.role !== to.meta.role) {
    return session?.role === 'teacher'
      ? { name: 'teacher-dashboard' }
      : { name: 'student-dashboard' }
  }
})

router.afterEach((to) => {
  const base = 'EduSpark'
  document.title = to.meta.title ? `${to.meta.title} | ${base}` : base
})

export default router
