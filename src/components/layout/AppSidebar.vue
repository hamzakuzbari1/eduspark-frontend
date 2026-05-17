<template>
  <v-navigation-drawer
    :model-value="drawer"
    :temporary="mobile"
    :permanent="!mobile"
    width="280"
    class="sidebar glass-sidebar"
    @update:model-value="$emit('update:drawer', $event)"
  >
    <div class="sidebar-brand pa-6">
      <BrandMark tagline="منصة التعليم الذكي" />
    </div>

    <v-divider class="border-opacity-25" />

    <v-list nav density="comfortable" class="px-3 py-3">
      <v-list-item
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        rounded="lg"
        color="primary"
        class="nav-item mb-1"
        active-class="nav-item--active"
      />
    </v-list>

    <template #append>
      <div class="pa-4">
        <v-card class="glass-card eduspark-gradient-soft pa-4" variant="flat">
          <div class="d-flex align-center gap-2 mb-2">
            <v-icon color="secondary" size="18">mdi-lightbulb-on</v-icon>
            <span class="text-body-2 font-weight-bold">نصيحة AI</span>
          </div>
          <div class="text-caption text-medium-emphasis">
            سجّل 30 ثانية من صوتك ليشرح الذكاء الاصطناعي الدروس بأسلوبك.
          </div>
        </v-card>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup>
import { useDisplay } from 'vuetify'
import BrandMark from './BrandMark.vue'

defineProps({
  drawer: { type: Boolean, default: true },
  items: { type: Array, default: () => [] },
})

defineEmits(['update:drawer'])

const { mobile } = useDisplay()
</script>

<style scoped>
.glass-sidebar {
  background: rgba(10, 14, 28, 0.75) !important;
  backdrop-filter: blur(24px);
  border-left: 1px solid var(--em-border) !important;
  box-shadow: 8px 0 40px rgba(0, 0, 0, 0.35);
}

.sidebar-brand {
  text-align: center;
}

.nav-item--active {
  background: rgba(124, 108, 240, 0.15) !important;
  box-shadow: inset 0 0 20px rgba(124, 108, 240, 0.08);
}

.nav-item:hover {
  background: rgba(124, 108, 240, 0.08);
}
</style>
