<template>
  <v-card class="glass-card eduspark-card-hover lesson-card h-100 d-flex flex-column" variant="flat">
    <div class="lesson-card__glow" :class="`lesson-card__glow--${lesson.accent || 'primary'}`" />

    <v-card-text class="pa-5 pa-md-6 flex-grow-1 d-flex flex-column">
      <div class="d-flex align-start justify-space-between gap-2 mb-4">
        <v-avatar size="48" class="eduspark-gradient" rounded="lg">
          <v-icon color="white">mdi-book-open-page-variant</v-icon>
        </v-avatar>
        <v-chip
          v-if="lesson.progress >= 100"
          color="success"
          size="x-small"
          variant="tonal"
          prepend-icon="mdi-check"
        >
          مكتمل
        </v-chip>
        <v-chip
          v-else-if="lesson.progress > 0"
          color="secondary"
          size="x-small"
          variant="tonal"
        >
          {{ lesson.progress }}%
        </v-chip>
        <v-chip v-else color="grey" size="x-small" variant="tonal">
          جديد
        </v-chip>
      </div>

      <h3 class="text-h6 font-weight-bold mb-1">{{ lesson.title }}</h3>
      <p class="text-caption text-medium-emphasis mb-3">
        <v-icon size="14" class="me-1">mdi-account-tie</v-icon>
        {{ lesson.teacherName }}
      </p>
      <p class="text-body-2 text-medium-emphasis mb-4 flex-grow-1 lesson-desc">
        {{ lesson.description }}
      </p>

      <div class="d-flex flex-wrap gap-2 mb-4">
        <v-chip size="small" variant="outlined" color="primary">{{ lesson.subject }}</v-chip>
        <v-chip size="small" variant="outlined" color="secondary">{{ lesson.grade }}</v-chip>
      </div>

      <div v-if="lesson.progress > 0 && lesson.progress < 100" class="mb-4">
        <div class="d-flex justify-space-between text-caption mb-1">
          <span class="text-medium-emphasis">التقدّم</span>
          <span class="text-secondary font-weight-bold">{{ lesson.progress }}%</span>
        </div>
        <v-progress-linear
          :model-value="lesson.progress"
          height="6"
          rounded
          color="secondary"
          bg-color="rgba(124, 108, 240, 0.15)"
        />
      </div>

      <div class="d-flex gap-3 text-caption text-medium-emphasis mb-5">
        <span><v-icon size="14">mdi-clock-outline</v-icon> {{ lesson.duration }}</span>
        <span><v-icon size="14">mdi-file-document</v-icon> {{ lesson.pages }} ص</span>
      </div>

      <v-btn
        block
        size="large"
        rounded="lg"
        class="btn-glow mt-auto"
        :to="`/student/lesson/${lesson.id}`"
      >
        <v-icon start>mdi-play-circle</v-icon>
        ابدأ التعلّم
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  lesson: { type: Object, required: true },
})
</script>

<style scoped>
.lesson-card {
  position: relative;
  overflow: hidden;
}

.lesson-card__glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--em-purple), var(--em-cyan), transparent);
  opacity: 0.6;
}

.lesson-desc {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
}
</style>
