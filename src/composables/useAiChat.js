import { nextTick, ref } from 'vue'
import { formatTimeArabic } from '../utils/format.js'

export function useAiChat(initialMessages = [], responsePool = []) {
  const messages = ref([...initialMessages])
  const chatInput = ref('')
  const isTyping = ref(false)
  const chatContainer = ref(null)
  const aiResponses = ref([...responsePool])

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

  function sendMessage() {
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
    const delay = 1200 + Math.random() * 800
    setTimeout(() => {
      isTyping.value = false
      messages.value.push({
        id: Date.now() + 1,
        role: 'ai',
        text: pickAiResponse(),
        time: formatTimeArabic(),
      })
      scrollToBottom()
    }, delay)
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
    scrollToBottom,
    loadConversation,
  }
}
