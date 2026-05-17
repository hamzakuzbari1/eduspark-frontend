<template>
  <header class="page-header" :class="{ 'page-header--compact': compact }">
    <span v-if="eyebrow" class="section-eyebrow">
      <v-icon v-if="eyebrowIcon" size="14">{{ eyebrowIcon }}</v-icon>
      {{ eyebrow }}
    </span>
    <h1 class="section-title" :class="{ 'eduspark-gradient-text': gradientTitle }">
      {{ title }}
    </h1>
    <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
    <slot />
  </header>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  eyebrowIcon: { type: String, default: '' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  gradientTitle: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
})
</script>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}

.page-header--compact {
  margin-bottom: 1.25rem;
}
</style>
