<template>
  <div class="slide-up-enter-active">
    <PageHeader
      eyebrow="مرحباً"
      :title="`أهلاً، ${profile.name}`"
      :subtitle="`استمري بتعلّمك مع المعلّم الذكي — ${profile.grade}`"
    />

    <v-row class="mb-8">
      <v-col
        v-for="(stat, index) in studentStats"
        :key="stat.title"
        cols="12"
        sm="6"
        lg="3"
        class="stat-col"
        :style="{ animationDelay: `${index * 0.08}s` }"
      >
        <StatCard :stat="stat" />
      </v-col>
    </v-row>

    <v-card class="glass-card glass-card--elevated pa-5 pa-md-6 mb-8" variant="flat">
      <div class="d-flex align-center gap-3 flex-wrap">
        <v-avatar size="48" class="eduspark-gradient">
          <v-icon color="white">mdi-robot-happy</v-icon>
        </v-avatar>
        <div class="flex-grow-1">
          <h3 class="text-h6 font-weight-bold mb-1">معلّمك الذكي جاهز</h3>
          <p class="text-body-2 text-medium-emphasis mb-0">
            اختاري درساً وابدئي محادثة تفاعلية — الشرح بأسلوب معلمك الحقيقي وبلهجة سورية
          </p>
        </div>
        <v-chip color="secondary" variant="tonal" prepend-icon="mdi-creation">
          AI Tutor
        </v-chip>
      </div>
    </v-card>

    <section id="lessons">
      <div class="d-flex align-center justify-space-between mb-5 flex-wrap gap-2">
        <div>
          <h3 class="text-h6 font-weight-bold">دروسي المتاحة</h3>
          <p class="text-caption text-medium-emphasis mb-0">{{ lessons.length }} دروس جاهزة للتعلّم</p>
        </div>
        <v-text-field
          v-model="search"
          density="compact"
          variant="outlined"
          prepend-inner-icon="mdi-magnify"
          placeholder="بحث في الدروس..."
          hide-details
          class="search-field"
          clearable
        />
      </div>

      <v-row v-if="filteredLessons.length">
        <v-col
          v-for="lesson in filteredLessons"
          :key="lesson.id"
          cols="12"
          sm="6"
          lg="4"
        >
          <StudentLessonCard :lesson="lesson" />
        </v-col>
      </v-row>

      <v-card v-else class="glass-card pa-10 text-center" variant="flat">
        <v-icon size="56" color="grey" class="mb-3">mdi-book-off</v-icon>
        <p class="text-body-1 text-medium-emphasis">لا توجد دروس تطابق البحث</p>
      </v-card>
    </section>

    <section id="progress" class="mt-10">
      <h3 class="text-h6 font-weight-bold mb-4">تقدّمك الأخير</h3>
      <v-row>
        <v-col
          v-for="lesson in inProgressLessons"
          :key="`p-${lesson.id}`"
          cols="12"
          md="6"
        >
          <v-card class="glass-card pa-4 d-flex align-center gap-4" variant="flat">
            <v-progress-circular
              :model-value="lesson.progress"
              :size="56"
              :width="5"
              color="secondary"
            >
              <span class="text-caption font-weight-bold">{{ lesson.progress }}%</span>
            </v-progress-circular>
            <div class="flex-grow-1 min-width-0">
              <div class="text-subtitle-2 font-weight-bold text-truncate">{{ lesson.title }}</div>
              <div class="text-caption text-medium-emphasis">{{ lesson.subject }}</div>
            </div>
            <v-btn
              icon
              variant="tonal"
              color="primary"
              :to="`/student/lesson/${lesson.id}`"
            >
              <v-icon>mdi-play</v-icon>
            </v-btn>
          </v-card>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../../components/common/PageHeader.vue'
import StatCard from '../../components/teacher/StatCard.vue'
import StudentLessonCard from '../../components/student/StudentLessonCard.vue'
import { fetchStudentLessons } from '../../api/student.js'
import {
  studentProfile,
  studentStats,
  getAvailableStudentLessons,
} from '../../data/studentData.js'
import { useAuth } from '../../composables/useAuth.js'
import { isApiMode } from '../../utils/session.js'

const { user } = useAuth()
const profile = computed(() => ({
  ...studentProfile,
  name: user.value?.name || studentProfile.name,
}))
const lessons = ref(getAvailableStudentLessons())
const search = ref('')
const loading = ref(false)

const filteredLessons = computed(() => {
  const q = search.value?.trim().toLowerCase()
  if (!q) return lessons.value
  return lessons.value.filter(
    (l) =>
      l.title.toLowerCase().includes(q) ||
      l.subject.toLowerCase().includes(q) ||
      (l.teacherName || '').toLowerCase().includes(q),
  )
})

const inProgressLessons = computed(() =>
  lessons.value.filter((l) => l.progress > 0 && l.progress < 100),
)

onMounted(async () => {
  if (!isApiMode()) return
  loading.value = true
  try {
    const data = await fetchStudentLessons()
    lessons.value = data.map((l) => ({
      id: l.id,
      title: l.title,
      subject: l.subject,
      grade: l.grade,
      teacherName: l.teacherName,
      preview: l.preview,
      icon: l.icon || 'mdi-book-open-page-variant',
      progress: 0,
    }))
  } catch {
    lessons.value = getAvailableStudentLessons()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stat-col {
  animation: slide-up 0.5s cubic-bezier(0.34, 1.2, 0.64, 1) backwards;
}

.search-field {
  max-width: 280px;
  min-width: 200px;
}

.min-width-0 {
  min-width: 0;
}
</style>
