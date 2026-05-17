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
      <BrandMark tagline="واجهة الطالب — Smarter Learning" />
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
            <v-icon color="secondary" size="18">mdi-robot-happy</v-icon>
            <span class="text-body-2 font-weight-bold">معلّمك الذكي</span>
          </div>
          <div class="text-caption text-medium-emphasis">
            اسأل أي سؤال — الشرح بأسلوب معلمك وبلهجة سورية مبسطة.
          </div>
        </v-card>
        <v-btn
          variant="text"
          color="grey"
          size="small"
          block
          class="mt-3"
          prepend-icon="mdi-logout"
          @click="logout"
        >
          تسجيل الخروج
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup>
import { useDisplay } from 'vuetify'
import { studentNavItems } from '../../config/navigation.js'
import { useAuth } from '../../composables/useAuth.js'
import BrandMark from './BrandMark.vue'

const { logout } = useAuth()

defineProps({
  drawer: { type: Boolean, default: true },
})

defineEmits(['update:drawer'])

const items = studentNavItems
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
