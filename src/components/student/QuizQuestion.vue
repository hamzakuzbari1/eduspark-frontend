<template>
  <v-card class="glass-card pa-5 pa-md-6 mb-4" variant="flat">
    <div class="d-flex align-start gap-3 mb-5">
      <v-avatar size="40" class="eduspark-gradient" rounded="lg">
        <span class="text-body-2 font-weight-bold text-white">{{ index + 1 }}</span>
      </v-avatar>
      <p class="text-subtitle-1 font-weight-medium flex-grow-1 mb-0">{{ question.question }}</p>
    </div>

    <v-radio-group
      v-model="selected"
      hide-details
      @update:model-value="onSelect"
    >
      <v-radio
        v-for="(option, i) in question.options"
        :key="i"
        :label="option"
        :value="i"
        :color="radioColor(i)"
        class="quiz-option mb-2 pa-3 rounded-xl"
        :class="optionClass(i)"
      />
    </v-radio-group>
  </v-card>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  question: { type: Object, required: true },
  index: { type: Number, default: 0 },
})

const emit = defineEmits(['answer'])

const selected = ref(null)
const submitted = ref(false)

function onSelect(val) {
  if (submitted.value) return
  submitted.value = true
  emit('answer', {
    questionId: props.question.id,
    selectedIndex: val,
    correct: val === props.question.correctIndex,
  })
}

function radioColor(i) {
  if (!submitted.value) return 'secondary'
  if (i === props.question.correctIndex) return 'success'
  if (i === selected.value) return 'error'
  return 'grey'
}

function optionClass(i) {
  if (!submitted.value) return ''
  if (i === props.question.correctIndex) return 'quiz-option--correct'
  if (i === selected.value && i !== props.question.correctIndex) return 'quiz-option--wrong'
  return ''
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
.quiz-option {
  border: 1px solid var(--em-border);
  background: rgba(8, 12, 24, 0.4);
  transition: all 0.25s ease;
}

.quiz-option:hover:not(.quiz-option--correct):not(.quiz-option--wrong) {
  border-color: rgba(34, 211, 238, 0.35);
  background: rgba(34, 211, 238, 0.06);
}

.quiz-option--correct {
  background: rgba(52, 211, 153, 0.1) !important;
  border-color: rgba(52, 211, 153, 0.45) !important;
  box-shadow: 0 0 20px rgba(52, 211, 153, 0.12);
}

.quiz-option--wrong {
  background: rgba(248, 113, 113, 0.08) !important;
  border-color: rgba(248, 113, 113, 0.35) !important;
}
</style>
