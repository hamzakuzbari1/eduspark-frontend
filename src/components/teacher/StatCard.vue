<template>
  <v-card class="glass-card eduspark-card-hover pa-5 pa-md-6" variant="flat">
    <div class="d-flex align-start justify-space-between">
      <div>
        <div class="text-caption text-medium-emphasis mb-2">{{ stat.title }}</div>
        <div class="text-h4 font-weight-bold mb-1">{{ stat.value }}</div>
        <div class="text-caption text-success d-flex align-center gap-1">
          <v-icon size="14">mdi-trending-up</v-icon>
          {{ stat.trend }}
        </div>
      </div>
      <v-avatar
        size="56"
        rounded="xl"
        class="stat-icon"
        :style="{ '--glow': glowColor }"
      >
        <v-icon :icon="stat.icon" size="28" :color="stat.color" />
      </v-avatar>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stat: { type: Object, required: true },
})

const glowMap = {
  primary: 'rgba(124, 108, 240, 0.4)',
  secondary: 'rgba(34, 211, 238, 0.4)',
  accent: 'rgba(167, 139, 250, 0.4)',
  success: 'rgba(52, 211, 153, 0.4)',
}

const glowColor = computed(() => glowMap[props.stat.color] ?? glowMap.primary)
</script>

<style scoped>
.stat-icon {
  background: rgba(124, 108, 240, 0.12) !important;
  border: 1px solid var(--em-border);
  box-shadow: 0 0 24px var(--glow);
}
</style>
