<template>
  <v-card class="glass-card eduspark-card-hover pa-5 lesson-card" variant="flat">
    <div class="d-flex align-center gap-3 mb-4">
      <v-avatar size="48" class="eduspark-gradient" rounded="lg">
        <v-icon color="white">mdi-file-pdf-box</v-icon>
      </v-avatar>
      <div class="flex-grow-1 min-width-0">
        <div class="text-subtitle-1 font-weight-bold text-truncate">{{ lesson.title }}</div>
        <div class="text-caption text-medium-emphasis">
          {{ lesson.subject }} · {{ lesson.grade }}
        </div>
      </div>
      <StatusBadge :status="lesson.status" />
    </div>

    <v-divider class="border-opacity-25 mb-4" />

    <div class="d-flex flex-wrap gap-3 text-caption text-medium-emphasis mb-4">
      <span>
        <v-icon size="14" class="me-1" color="secondary">mdi-file-document</v-icon>
        {{ lesson.pages }} صفحة
      </span>
      <span>
        <v-icon size="14" class="me-1" color="secondary">mdi-account-group</v-icon>
        {{ lesson.students }} طالب
      </span>
      <span>
        <v-icon size="14" class="me-1" color="secondary">mdi-calendar</v-icon>
        {{ lesson.uploadedAt }}
      </span>
    </div>

    <div class="d-flex gap-2 flex-wrap">
      <v-btn
        v-if="lesson.status === 'processed'"
        class="btn-glow-outline flex-grow-1"
        size="small"
        prepend-icon="mdi-eye"
        :to="`/student/lesson/${lesson.id}`"
      >
        معاينة الطالب
      </v-btn>
      <v-btn
        v-else-if="lesson.status === 'processing'"
        variant="tonal"
        color="warning"
        size="small"
        disabled
        class="flex-grow-1"
        prepend-icon="mdi-cog"
      >
        جاري المعالجة...
      </v-btn>
      <v-btn
        v-else
        class="btn-glow-outline flex-grow-1"
        size="small"
        prepend-icon="mdi-pencil"
        to="/teacher/upload"
      >
        إكمال الرفع
      </v-btn>
    </div>
  </v-card>
</template>

<script setup>
import StatusBadge from '../common/StatusBadge.vue'

defineProps({
  lesson: { type: Object, required: true },
})
</script>

<style scoped>
.lesson-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.lesson-card .d-flex.gap-2 {
  margin-top: auto;
}
</style>
