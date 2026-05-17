export const MAX_PDF_SIZE_BYTES = 50 * 1024 * 1024
export const MAX_PDF_SIZE_LABEL = '50 ميجابايت'
export const VOICE_SAMPLE_SECONDS = 30
export const ACCEPTED_PDF_TYPES = ['application/pdf']

export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  TEACHER_DASHBOARD: '/teacher/dashboard',
  TEACHER_UPLOAD: '/teacher/upload',
  STUDENT_DASHBOARD: '/student/dashboard',
  STUDENT_PROFILE: '/student/profile',
  STUDENT_LESSON: (id = '1') => `/student/lesson/${id}`,
}

export const LESSON_STATUS = {
  PROCESSED: 'processed',
  PROCESSING: 'processing',
  DRAFT: 'draft',
  ERROR: 'error',
}
