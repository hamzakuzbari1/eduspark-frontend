<template>
  <v-card
    v-if="show"
    class="glass-card glass-card--elevated quiz-results pa-6 pa-md-8 mb-4"
    variant="flat"
  >
    <div class="text-center mb-6">
      <v-progress-circular
        :model-value="scorePercent"
        :size="100"
        :width="8"
        :color="scoreColor"
        class="mb-4"
      >
        <span class="text-h5 font-weight-bold">{{ scorePercent }}%</span>
      </v-progress-circular>
      <h3 class="text-h6 font-weight-bold mb-1">{{ resultTitle }}</h3>
      <p class="text-body-2 text-medium-emphasis">
        {{ correctCount }} من {{ total }} إجابات صحيحة
      </p>
    </div>

    <v-row dense class="mb-4">
      <v-col cols="6">
        <div class="result-stat eduspark-gradient-soft pa-3 rounded-xl text-center">
          <v-icon color="success" class="mb-1">mdi-check-circle</v-icon>
          <div class="text-h6 font-weight-bold text-success">{{ correctCount }}</div>
          <div class="text-caption">صحيحة</div>
        </div>
      </v-col>
      <v-col cols="6">
        <div class="result-stat eduspark-gradient-soft pa-3 rounded-xl text-center">
          <v-icon color="error" class="mb-1">mdi-close-circle</v-icon>
          <div class="text-h6 font-weight-bold text-error">{{ total - correctCount }}</div>
          <div class="text-caption">خاطئة</div>
        </div>
      </v-col>
    </v-row>

    <v-btn
      v-if="canRetry"
      block
      class="btn-glow-outline"
      prepend-icon="mdi-refresh"
      @click="$emit('retry')"
    >
      إعادة الاختبار
    </v-btn>
    <v-btn
      v-else
      block
      class="btn-glow mt-2"
      prepend-icon="mdi-arrow-left"
      :to="dashboardTo"
    >
      العودة للدروس
    </v-btn>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { ROUTES } from '../../constants/app.js'

const props = defineProps({
  show: { type: Boolean, default: false },
  correctCount: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  canRetry: { type: Boolean, default: true },
})

defineEmits(['retry'])

const dashboardTo = ROUTES.STUDENT_DASHBOARD

const scorePercent = computed(() =>
  props.total ? Math.round((props.correctCount / props.total) * 100) : 0,
)

const scoreColor = computed(() => {
  if (scorePercent.value >= 80) return 'success'
  if (scorePercent.value >= 50) return 'warning'
  return 'error'
})

const resultTitle = computed(() => {
  if (scorePercent.value >= 80) return 'أداء ممتاز! 🎉'
  if (scorePercent.value >= 50) return 'جيد — واصل التمرين'
  return 'راجع الدرس وحاول مرة أخرى'
})
</script>

<style scoped>
.quiz-results {
  animation: slide-up 0.5s cubic-bezier(0.34, 1.2, 0.64, 1);
}

.result-stat {
  transition: transform 0.2s;
}

.result-stat:hover {
  transform: translateY(-2px);
}
</style>
