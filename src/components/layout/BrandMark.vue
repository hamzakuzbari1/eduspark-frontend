<template>
  <div class="brand-mark text-center">
    <EduSparkLogo :size="logoSize" class="mb-3" />
    <div class="text-h6 font-weight-bold eduspark-gradient-text">EduSpark</div>
    <div class="text-caption text-medium-emphasis">{{ tagline }}</div>
  </div>
</template>

<script setup>
import EduSparkLogo from '../auth/EduSparkLogo.vue'

defineProps({
  tagline: { type: String, default: 'منصة التعليم الذكي' },
  logoSize: { type: String, default: 'sidebar' },
})
</script>

<style scoped>
.brand-mark {
  padding: 0 4px;
}
</style>
