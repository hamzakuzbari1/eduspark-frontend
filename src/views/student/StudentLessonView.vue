<template>
  <div class="lesson-page slide-up-enter-active">
    <v-card class="glass-card pa-4 pa-md-5 mb-5 mb-md-6 lesson-banner" variant="flat">
      <div class="d-flex align-center flex-wrap gap-3">
        <v-btn
          icon
          variant="tonal"
          color="primary"
          :to="ROUTES.STUDENT_DASHBOARD"
          aria-label="العودة للدروس"
        >
          <v-icon>mdi-arrow-right</v-icon>
        </v-btn>
        <v-avatar size="48" class="eduspark-gradient">
          <v-icon color="white">mdi-book-open-page-variant</v-icon>
        </v-avatar>
        <div class="flex-grow-1 min-width-0">
          <h2 class="text-h6 text-md-h5 font-weight-bold text-truncate">{{ lesson.title }}</h2>
          <p class="text-caption text-medium-emphasis mb-0">
            {{ lesson.teacherName }} · {{ lesson.subject }} · {{ lesson.grade }}
          </p>
        </div>
        <v-chip color="secondary" variant="tonal" prepend-icon="mdi-robot-happy" class="ai-chip">
          <span class="ai-chip__dot" />
          معلّم ذكي
        </v-chip>
      </div>
    </v-card>

    <v-row align="start">
      <v-col cols="12" lg="7" class="d-flex">
        <ChatPanel
          ref="chatPanelRef"
          v-model="chatInput"
          :messages="messages"
          :is-typing="isTyping"
          :teacher-name="lesson.teacherName"
          class="w-100"
          @send="onSend"
        />
      </v-col>

      <v-col cols="12" lg="5">
        <div class="lesson-sidebar">
          <div class="mb-5">
            <h3 class="text-h6 font-weight-bold mb-4 d-flex align-center gap-2">
              <v-icon color="secondary">mdi-message-star</v-icon>
              التغذية الراجعة
            </h3>
            <TransitionGroup name="feedback">
              <FeedbackCard
                v-for="fb in activeFeedback"
                :key="fb.id"
                :feedback="fb"
              />
            </TransitionGroup>
            <p v-if="!activeFeedback.length" class="text-caption text-medium-emphasis">
              أجب على الأسئلة لتحصل على تغذية راجعة فورية
            </p>
          </div>

          <template v-if="lesson.quizQuestions?.length">
            <QuizResults
              :show="quizComplete"
              :correct-count="quizScore.correct"
              :total="lesson.quizQuestions.length"
              @retry="resetQuiz"
            />

            <div v-if="!quizComplete">
              <h3 class="text-h6 font-weight-bold mb-4 d-flex align-center gap-2">
                <v-icon color="primary">mdi-clipboard-check</v-icon>
                اختبار سريع
                <v-chip size="x-small" variant="tonal" color="primary">
                  {{ answeredCount }}/{{ lesson.quizQuestions.length }}
                </v-chip>
              </h3>
              <QuizCard
                v-for="(q, i) in lesson.quizQuestions"
                v-show="currentQuizIndex === i || quizAnswers[q.id] !== undefined"
                :key="`${q.id}-${quizResetKey}`"
                :question="q"
                :index="i"
                @answer="onQuizAnswer"
              />
            </div>
          </template>

          <v-card v-else class="glass-card pa-6 text-center" variant="flat">
            <v-icon size="48" color="primary" class="mb-2 opacity-70">mdi-chat-question</v-icon>
            <p class="text-body-2 text-medium-emphasis mb-0">
              ركّز على المحادثة مع المعلّم الذكي — الاختبار قريباً
            </p>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ChatPanel from '../../components/student/ChatPanel.vue'
import QuizCard from '../../components/student/QuizCard.vue'
import QuizResults from '../../components/student/QuizResults.vue'
import FeedbackCard from '../../components/student/FeedbackCard.vue'
import { fetchStudentLesson } from '../../api/student.js'
import { useAiChat } from '../../composables/useAiChat.js'
import { getStudentLessonById } from '../../data/studentData.js'
import { ROUTES } from '../../constants/app.js'
import { isApiMode } from '../../utils/session.js'

const props = defineProps({
  id: { type: String, required: true },
})

const route = useRoute()
const lessonId = computed(() => props.id || route.params.id)
const lesson = ref({
  title: '…',
  subject: '',
  grade: '',
  teacherName: '',
  quizQuestions: [],
})

const chatPanelRef = ref(null)
const activeFeedback = ref([])
const quizAnswers = reactive({})
const quizResetKey = ref(0)

const {
  messages,
  chatInput,
  isTyping,
  sendMessage,
  loadConversation,
  setLessonId,
} = useAiChat([], [])

const answeredCount = computed(() => Object.keys(quizAnswers).length)
const quizComplete = computed(() => {
  const total = lesson.value.quizQuestions?.length ?? 0
  return total > 0 && answeredCount.value >= total
})

const quizScore = computed(() => {
  let correct = 0
  for (const q of lesson.value.quizQuestions || []) {
    if (quizAnswers[q.id] === q.correctIndex) correct += 1
  }
  return { correct }
})

const currentQuizIndex = computed(() => {
  const qs = lesson.value.quizQuestions || []
  const next = qs.findIndex((q) => quizAnswers[q.id] === undefined)
  return next >= 0 ? next : qs.length - 1
})

async function loadLesson() {
  activeFeedback.value = []
  Object.keys(quizAnswers).forEach((k) => delete quizAnswers[k])
  quizResetKey.value += 1

  if (isApiMode()) {
    try {
      const data = await fetchStudentLesson(lessonId.value)
      lesson.value = data
      loadConversation(data.chatMessages || [], [])
      setLessonId(Number(lessonId.value))
    } catch {
      const l = getStudentLessonById(lessonId.value)
      lesson.value = l
      loadConversation(l.chatMessages, l.aiResponses)
    }
  } else {
    const l = getStudentLessonById(lessonId.value)
    lesson.value = l
    loadConversation(l.chatMessages, l.aiResponses)
  }
  chatPanelRef.value?.scrollToBottom()
}

watch(lessonId, loadLesson, { immediate: true })

watch(messages, () => {
  chatPanelRef.value?.scrollToBottom()
}, { deep: true })

function onSend() {
  sendMessage()
}

function onQuizAnswer({ correct, questionId, selectedIndex }) {
  quizAnswers[questionId] = selectedIndex
  activeFeedback.value = [
    correct
      ? {
          id: Date.now(),
          type: 'success',
          title: 'إجابة صحيحة!',
          message: 'ممتاز! فهمت المفهوم بشكل رائع — استمري.',
        }
      : {
          id: Date.now(),
          type: 'hint',
          title: 'حاولي مرة أخرى',
          message: 'راجعي الشرح في المحادثة وجربي مرة تانية — أنتِ قريبة!',
        },
  ]
}

function resetQuiz() {
  Object.keys(quizAnswers).forEach((k) => delete quizAnswers[k])
  activeFeedback.value = []
  quizResetKey.value += 1
}
</script>

<style scoped>
.lesson-banner {
  border: 1px solid var(--em-border-bright);
  box-shadow: var(--em-glow-cyan);
}

.ai-chip__dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--em-cyan);
  margin-inline-start: 6px;
  animation: blink 1.5s ease infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--em-cyan); }
  50% { opacity: 0.4; }
}

.lesson-sidebar {
  position: sticky;
  top: 88px;
}

@media (max-width: 1279px) {
  .lesson-sidebar {
    position: static;
  }
}

.min-width-0 {
  min-width: 0;
}

.feedback-enter-active {
  transition: all 0.35s ease;
}

.feedback-enter-from {
  opacity: 0;
  transform: translateX(12px);
}
</style>
