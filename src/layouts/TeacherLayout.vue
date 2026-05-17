<template>
  <v-layout class="teacher-layout">
    <AppSidebar
      v-model:drawer="drawer"
      :items="teacherNavItems"
    />

    <v-main class="teacher-main">
      <AppHeader
        :title="pageTitle"
        @toggle-drawer="drawer = !drawer"
      />
      <v-container fluid class="page-container pa-4 pa-md-6">
        <router-view v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '../components/layout/AppSidebar.vue'
import AppHeader from '../components/layout/AppHeader.vue'
import { teacherNavItems } from '../config/navigation.js'

const drawer = ref(true)
const route = useRoute()

const pageTitle = computed(() => route.meta.title ?? 'لوحة المعلم')
</script>

<style scoped>
.teacher-layout {
  min-height: 100vh;
}

.teacher-main {
  background: transparent;
}
</style>
