<template>
  <v-app-bar flat class="app-header glass-header px-2 px-md-4">
    <v-app-bar-nav-icon
      class="d-md-none"
      @click="$emit('toggle-drawer')"
    />
    <v-toolbar-title class="text-h6 font-weight-bold text-truncate">
      {{ title }}
    </v-toolbar-title>
    <v-spacer />
    <template v-if="role === 'teacher'">
      <v-btn
        class="btn-glow d-none d-sm-flex me-2"
        prepend-icon="mdi-cloud-upload"
        size="small"
        to="/teacher/upload"
      >
        رفع درس
      </v-btn>
      <v-btn
        class="d-sm-none me-2"
        icon
        variant="tonal"
        color="primary"
        to="/teacher/upload"
      >
        <v-icon>mdi-cloud-upload</v-icon>
      </v-btn>
    </template>
    <v-menu>
      <template #activator="{ props: menuProps }">
        <v-btn icon v-bind="menuProps">
          <v-avatar size="38" class="eduspark-gradient">
            <span v-if="userInitial" class="text-body-2 text-white font-weight-bold">
              {{ userInitial }}
            </span>
            <v-icon v-else color="white" size="20">mdi-account</v-icon>
          </v-avatar>
        </v-btn>
      </template>
      <v-list class="glass-card" density="compact">
        <v-list-item
          v-if="role === 'student'"
          prepend-icon="mdi-account-cog"
          title="الملف الشخصي"
          to="/student/profile"
        />
        <v-list-item prepend-icon="mdi-logout" title="تسجيل الخروج" @click="logout" />
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup>
import { computed } from 'vue'
import { useAuth } from '../../composables/useAuth.js'

defineProps({
  title: { type: String, default: '' },
  role: { type: String, default: 'teacher' },
})

defineEmits(['toggle-drawer'])

const { user, logout } = useAuth()
const userInitial = computed(() => user.value?.name?.charAt(0) ?? '')
</script>

<style scoped>
.glass-header {
  background: rgba(10, 14, 28, 0.6) !important;
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--em-border);
}
</style>
