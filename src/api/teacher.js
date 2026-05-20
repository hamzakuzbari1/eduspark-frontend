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
  })
  return data
}

export async function processLessonApi(lessonId) {
  const { data } = await api.post(`/teacher/lessons/${lessonId}/process`)
  return data
}
