<template>
  <v-alert
    :type="alertType"
    variant="tonal"
    class="feedback-card mb-3 rounded-xl"
    :icon="icon"
    :title="feedback.title"
  >
    {{ feedback.message }}
  </v-alert>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  feedback: { type: Object, required: true },
})

const typeMap = {
  success: 'success',
  hint: 'info',
  warning: 'warning',
  error: 'error',
}

const iconMap = {
  success: 'mdi-check-circle',
  hint: 'mdi-lightbulb-on',
  warning: 'mdi-alert',
  error: 'mdi-close-circle',
}

const alertType = computed(() => typeMap[props.feedback.type] ?? 'info')
const icon = computed(() => iconMap[props.feedback.type] ?? 'mdi-information')
</script>

<style scoped>
.feedback-card {
  background: rgba(17, 25, 52, 0.6) !important;
  backdrop-filter: blur(8px);
  border: 1px solid var(--em-border);
}
</style>
