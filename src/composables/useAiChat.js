import { nextTick, ref } from 'vue'
import { sendAiChatApi, voiceChatApi, resolveAiAudioUrl } from '../api/ai.js'
import { getErrorMessage } from '../api/client.js'
import { formatTimeArabic } from '../utils/format.js'
import { isApiMode } from '../utils/session.js'

export function useAiChat(initialMessages = [], responsePool = []) {
  const messages = ref([...initialMessages])
  const chatInput = ref('')
  const isTyping = ref(false)
  const chatContainer = ref(null)
  const aiResponses = ref([...responsePool])
  const lessonId = ref(null)

  function pickAiResponse() {
    const pool = aiResponses.value
    if (!pool.length) {
      return 'سؤال ممتاز! خليني أشرحلك بطريقة أبسط بنفس أسلوب معلمك...'
    }
    return pool[Math.floor(Math.random() * pool.length)]
  }

  async function scrollToBottom() {
    await nextTick()
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }

  function setLessonId(id) {
    lessonId.value = id
  }

  async function sendMessage() {
    const text = chatInput.value.trim()
    if (!text || isTyping.value) return

    messages.value.push({
      id: Date.now(),
      role: 'student',
      text,
      time: formatTimeArabic(),
    })
    chatInput.value = ''
    scrollToBottom()
    isTyping.value = true

    try {
      if (isApiMode() && lessonId.value) {
        const data = await sendAiChatApi({ lessonId: lessonId.value, message: text })
        messages.value = data.messages.map((m) => ({
          id: m.id,
          role: m.role,
          text: m.text,
          time: m.time || formatTimeArabic(),
        }))
      } else {
        await new Promise((r) => setTimeout(r, 1200 + Math.random() * 800))
        messages.value.push({
          id: Date.now() + 1,
          role: 'ai',
          text: pickAiResponse(),
          time: formatTimeArabic(),
        })
      }
    } catch (err) {
      messages.value.push({
        id: Date.now() + 1,
        role: 'ai',
        text: getErrorMessage(err, 'تعذر الاتصال بالمعلّم الذكي — حاول مرة أخرى'),
        time: formatTimeArabic(),
      })
    } finally {
      isTyping.value = false
      scrollToBottom()
    }
  }

  async function sendVoiceMessage(audioBlob) {
    if (!audioBlob || isTyping.value || !lessonId.value || !isApiMode()) return

    isTyping.value = true
    try {
      const file = new File([audioBlob], 'question.webm', {
        type: audioBlob.type || 'audio/webm',
      })
      const data = await voiceChatApi({ file, lessonId: lessonId.value })
      messages.value = data.messages.map((m) => ({
        id: m.id,
        role: m.role,
        text: m.text,
        time: m.time || formatTimeArabic(),
        audioUrl: m.audioUrl,
      }))
      if (data.audio_url) {
        const url = resolveAiAudioUrl(data.audio_url)
        const last = messages.value[messages.value.length - 1]
        if (last?.role === 'ai' && url) {
          last.audioUrl = url
          const audio = new Audio(url)
          audio.play().catch(() => {})
        }
      }
    } catch (err) {
      messages.value.push({
        id: Date.now(),
        role: 'ai',
        text: getErrorMessage(err, 'تعذر إرسال السؤال الصوتي'),
        time: formatTimeArabic(),
      })
    } finally {
      isTyping.value = false
      scrollToBottom()
    }
  }

  function loadConversation(initial = [], responses = []) {
    messages.value = [...initial]
    aiResponses.value = [...responses]
    chatInput.value = ''
    isTyping.value = false
  }

  return {
    messages,
    chatInput,
    isTyping,
    chatContainer,
    sendMessage,
    sendVoiceMessage,
    scrollToBottom,
    loadConversation,
    setLessonId,
  }
}
