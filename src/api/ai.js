import { api } from './client.js'
import { pollLessonProcessing } from './teacher.js'

/** RAG chat (same behavior as /student/chat). */
export async function sendAiChatApi({ lessonId, message }) {
  const { data } = await api.post('/ai/chat', {
    lesson_id: lessonId,
    message,
  })
  return data
}

/** Upload PDF + optional auto RAG processing. */
export async function uploadPdfAiApi({ file, subject, grade, title, lessonId, autoProcess = false }) {
  const form = new FormData()
  form.append('file', file)
  form.append('subject', subject)
  form.append('grade', grade)
  if (title) form.append('title', title)
  if (lessonId) form.append('lesson_id', String(lessonId))
  form.append('auto_process', autoProcess ? 'true' : 'false')

  const { data } = await api.post('/ai/pdf/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function processLessonAiApi(lessonId, options = {}) {
  const { poll = true, onStatus } = options
  const { data } = await api.post(`/ai/lessons/${lessonId}/process`, null, {
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

export async function transcribeAudioApi({ file, lessonId }) {
  const form = new FormData()
  form.append('file', file)
  if (lessonId) form.append('lesson_id', String(lessonId))

  const { data } = await api.post('/ai/transcribe', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function voiceChatApi({ file, lessonId }) {
  const form = new FormData()
  form.append('file', file)
  form.append('lesson_id', String(lessonId))

  const { data } = await api.post('/ai/chat/voice', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function textToSpeechApi({ text, lessonId }) {
  const { data } = await api.post('/ai/tts', { text, lesson_id: lessonId })
  return data
}

/** Resolve TTS audio URL (relative /api path). */
export function resolveAiAudioUrl(path) {
  if (!path) return null
  if (path.startsWith('http')) return path
  const base = import.meta.env.VITE_API_URL || ''
  if (base) return `${base.replace(/\/$/, '')}${path}`
  return path
}
