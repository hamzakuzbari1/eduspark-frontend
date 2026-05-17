<template>
  <ProcessingOverlay
    :show="show"
    :progress="progress"
    :step="step"
    :title="title"
    :subtitle="subtitle"
  />
</template>

<script setup>
import ProcessingOverlay from '../teacher/ProcessingOverlay.vue'

defineProps({
  show: { type: Boolean, default: false },
  progress: { type: Number, default: 0 },
  step: { type: Number, default: 0 },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
})
</script>
