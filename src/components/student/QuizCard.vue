<template>
  <v-card class="glass-card quiz-card pa-5 pa-md-6 mb-4" variant="flat">
    <div class="d-flex align-start gap-3 mb-5">
      <v-avatar size="40" class="eduspark-gradient" rounded="lg">
        <span class="text-body-2 font-weight-bold text-white">{{ index + 1 }}</span>
      </v-avatar>
      <p class="text-subtitle-1 font-weight-medium flex-grow-1 mb-0">{{ question.question }}</p>
    </div>

    <div class="quiz-options">
      <button
        v-for="(option, i) in question.options"
        :key="i"
        type="button"
        class="quiz-option-btn w-100 text-start pa-4 rounded-xl mb-2 d-flex align-center gap-3"
        :class="optionClass(i)"
        :disabled="submitted"
        @click="selectOption(i)"
      >
        <span class="option-letter">{{ optionLetters[i] }}</span>
        <span class="text-body-1 flex-grow-1">{{ option }}</span>
        <v-icon v-if="submitted && i === question.correctIndex" color="success" size="20">
          mdi-check-circle
        </v-icon>
        <v-icon
          v-else-if="submitted && i === selected && i !== question.correctIndex"
          color="error"
          size="20"
        >
          mdi-close-circle
        </v-icon>
      </button>
    </div>

    <v-expand-transition>
      <div v-if="submitted && question.hint && selected !== question.correctIndex" class="hint-box mt-3 pa-3 rounded-lg">
        <v-icon color="info" size="18" class="me-2">mdi-lightbulb-on</v-icon>
        <span class="text-body-2">{{ question.hint }}</span>
      </div>
    </v-expand-transition>
  </v-card>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  question: { type: Object, required: true },
  index: { type: Number, default: 0 },
})

const emit = defineEmits(['answer'])

const optionLetters = ['أ', 'ب', 'ج', 'د']
const selected = ref(null)
const submitted = ref(false)

function selectOption(i) {
  if (submitted.value) return
  selected.value = i
  submitted.value = true
  emit('answer', {
    questionId: props.question.id,
    selectedIndex: i,
    correct: i === props.question.correctIndex,
  })
}

function optionClass(i) {
  if (!submitted.value) return ''
  if (i === props.question.correctIndex) return 'quiz-option-btn--correct'
  if (i === selected.value) return 'quiz-option-btn--wrong'
  return 'quiz-option-btn--muted'
}

watch(
  () => props.question.id,
  () => {
    selected.value = null
    submitted.value = false
  },
)
</script>

<style scoped>
.quiz-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.quiz-option-btn {
  border: 1px solid var(--em-border);
  background: rgba(8, 12, 24, 0.5);
  color: var(--em-text);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.34, 1.2, 0.64, 1);
  font-family: inherit;
}

.quiz-option-btn:hover:not(:disabled):not(.quiz-option-btn--correct):not(.quiz-option-btn--wrong) {
  border-color: rgba(34, 211, 238, 0.4);
  background: rgba(34, 211, 238, 0.08);
  transform: translateX(-4px);
}

.option-letter {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: rgba(124, 108, 240, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--em-cyan);
  flex-shrink: 0;
}

.quiz-option-btn--correct {
  border-color: rgba(52, 211, 153, 0.5) !important;
  background: rgba(52, 211, 153, 0.12) !important;
  box-shadow: 0 0 24px rgba(52, 211, 153, 0.15);
  animation: correct-pop 0.4s ease;
}

.quiz-option-btn--wrong {
  border-color: rgba(248, 113, 113, 0.45) !important;
  background: rgba(248, 113, 113, 0.1) !important;
  animation: shake 0.4s ease;
}

.quiz-option-btn--muted {
  opacity: 0.5;
}

.hint-box {
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.25);
  display: flex;
  align-items: flex-start;
}

@keyframes correct-pop {
  0% { transform: scale(0.98); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}
</style>
