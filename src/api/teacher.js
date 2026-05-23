import { api } from './client.js'

export async function fetchTeacherContent() {
  const { data } = await api.get('/teacher/content')
  return data
}

export async function uploadPdfApi({ file, subject, grade, title, lessonId }) {
  const form = new FormData()
  form.append('file', file)
  form.append('subject', subject)
  form.append('grade', grade)
  if (title) form.append('title', title)
  if (lessonId) form.append('lesson_id', String(lessonId))

  const { data } = await api.post('/teacher/upload/pdf', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
    onUploadProgress: (e) => {
      if (e.total) return Math.round((e.loaded * 100) / e.total)
      return 0
    },
  })
  return data
}

export async function uploadVoiceApi({ file, lessonId }) {
  const form = new FormData()
  form.append('file', file)
  form.append('lesson_id', String(lessonId))

  const { data } = await api.post('/teacher/upload/voice', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
  return data
}

export async function getLessonStatusApi(lessonId) {
  const { data } = await api.get(`/teacher/lessons/${lessonId}/status`, {
    timeout: 15000,
  })
  return data
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/** Poll GET /teacher/lessons/{id}/status until processed or error. */
export async function pollLessonProcessing(lessonId, options = {}) {
  const {
    maxWaitMs = 30 * 60 * 1000,
    pollIntervalMs = 2500,
    onStatus,
  } = options

  const start = Date.now()
  while (Date.now() - start < maxWaitMs) {
    await delay(pollIntervalMs)
    const status = await getLessonStatusApi(lessonId)
    if (onStatus) onStatus(status)

    if (status.status === 'processed') {
      return {
        lesson_id: lessonId,
        status: 'processed',
        message: status.message || 'اكتملت المعالجة بنجاح',
      }
    }
    if (status.status === 'error') {
      throw new Error(status.message || 'فشلت معالجة الدرس')
    }
  }

  throw new Error(
    'انتهت مهلة انتظار المعالجة. قد تكون OCR ما زالت تعمل — راجع لوحة التحكم لاحقاً.',
  )
}

/**
 * Start lesson processing. When the backend runs OCR in the background,
 * polls status until processed/error (up to maxWaitMs).
 */
export async function processLessonApi(lessonId, options = {}) {
  const { poll = true, onStatus } = options

  const { data } = await api.post(`/teacher/lessons/${lessonId}/process`, null, {
    timeout: 30000,
  })

  if (!poll || data.status !== 'processing') {
    if (data.status === 'error') {
      throw new Error(data.message || 'فشلت معالجة الدرس')
    }
    return data
  }

  if (onStatus) onStatus(data)
  return pollLessonProcessing(lessonId, options)
}
