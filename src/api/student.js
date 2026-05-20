import { api } from './client.js'

export async function fetchStudentLessons() {
  const { data } = await api.get('/student/lessons')
  return data
}

export async function fetchStudentLesson(id) {
  const { data } = await api.get(`/student/lesson/${id}`)
  return data
}

export async function sendChatApi({ lessonId, message }) {
  const { data } = await api.post('/student/chat', {
    lesson_id: lessonId,
    message,
  })
  return data
}

export async function fetchQuizApi(lessonId) {
  const { data } = await api.get(`/student/quiz/${lessonId}`)
  return data
}

export async function submitQuizApi({ lessonId, answers }) {
  const { data } = await api.post('/student/quiz/submit', {
    lesson_id: lessonId,
    answers,
  })
  return data
}

export async function getProfileApi() {
  const { data } = await api.get('/student/profile')
  return data
}

export async function updateProfileApi({ interests, difficulty }) {
  const { data } = await api.put('/student/profile', { interests, difficulty })
  return data
}
