export const teacherNavItems = [
  { title: 'لوحة التحكم', icon: 'mdi-view-dashboard', to: '/teacher/dashboard' },
  { title: 'رفع درس', icon: 'mdi-cloud-upload', to: '/teacher/upload' },
  { title: 'دروسي', icon: 'mdi-book-multiple', to: '/teacher/dashboard#lessons' },
  { title: 'الإعدادات', icon: 'mdi-cog', to: '/teacher/dashboard' },
]

export const studentNavItems = [
  { title: 'دروسي', icon: 'mdi-view-dashboard', to: '/student/dashboard' },
  { title: 'جلسة تعلّم', icon: 'mdi-book-open-page-variant', to: '/student/lesson/1' },
  { title: 'تقدّمي', icon: 'mdi-chart-timeline-variant', to: '/student/dashboard#progress' },
  { title: 'الملف الشخصي', icon: 'mdi-account-cog', to: '/student/profile' },
]
