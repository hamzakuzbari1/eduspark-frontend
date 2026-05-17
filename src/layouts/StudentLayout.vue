<template>
  <v-layout class="student-layout">
    <StudentSidebar v-model:drawer="drawer" />

    <v-main class="student-main">
      <AppHeader
        :title="pageTitle"
        role="student"
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
import StudentSidebar from '../components/layout/StudentSidebar.vue'
import AppHeader from '../components/layout/AppHeader.vue'

const drawer = ref(true)
const route = useRoute()

const pageTitle = computed(() => route.meta.title ?? 'واجهة الطالب')
</script>

<style scoped>
.student-layout {
  min-height: 100vh;
}

.student-main {
  background: transparent;
}
</style>
