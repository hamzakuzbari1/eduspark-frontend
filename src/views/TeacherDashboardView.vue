<template>
  <div class="slide-up-enter-active">
    <PageHeader
      eyebrow="لوحة المعلم"
      :title="`مرحباً، ${teacherName}`"
      subtitle="إدارة دروسك ومتابعة تفاعل الطلاب مع المعلّم الذكي"
    />

    <v-row class="mb-8">
      <v-col
        v-for="(stat, index) in displayStats"
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

    <v-row class="mb-8">
      <v-col cols="12" lg="8">
        <v-card class="glass-card glass-card--elevated pa-6" variant="flat">
          <div class="d-flex align-center justify-space-between mb-5 flex-wrap gap-3">
            <div>
              <h3 class="text-h6 font-weight-bold mb-1">رفع درس جديد</h3>
              <p class="text-caption text-medium-emphasis mb-0">
                ارفع PDF وسجّل عينة صوتك ليبدأ الذكاء الاصطناعي بالشرح
              </p>
            </div>
            <v-btn class="btn-glow" prepend-icon="mdi-cloud-upload" to="/teacher/upload">
              رفع درس
            </v-btn>
          </div>
          <v-sheet
            class="upload-teaser rounded-xl pa-8 pa-md-10 text-center"
            role="button"
            tabindex="0"
            @click="$router.push('/teacher/upload')"
            @keydown.enter="$router.push('/teacher/upload')"
          >
            <v-icon size="56" color="primary" class="mb-4 pdf-icon-glow">mdi-file-pdf-box</v-icon>
            <p class="text-body-1 font-weight-medium mb-3">اسحب ملف الدرس أو ابدأ من هنا</p>
            <v-btn class="btn-glow-outline" prepend-icon="mdi-arrow-left" to="/teacher/upload">
              الانتقال لصفحة الرفع
            </v-btn>
          </v-sheet>
        </v-card>
      </v-col>
      <v-col cols="12" lg="4">
        <RecentActivityList :items="recentActivity" />
      </v-col>
    </v-row>

    <section id="lessons">
      <div class="d-flex align-center justify-space-between mb-5 flex-wrap gap-2">
        <div>
          <h3 class="text-h6 font-weight-bold">الدروس المرفوعة</h3>
          <p class="text-caption text-medium-emphasis mb-0">{{ lessons.length }} درس</p>
        </div>
        <v-btn variant="text" color="secondary" size="small" to="/teacher/upload">
          + درس جديد
        </v-btn>
      </div>

      <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" />

      <v-row v-if="lessons.length">
        <v-col
          v-for="lesson in lessons"
          :key="lesson.id"
          cols="12"
          md="6"
          xl="4"
        >
          <LessonCard :lesson="lesson" />
        </v-col>
      </v-row>

      <EmptyState
        v-else-if="!loading"
        icon="mdi-book-plus-outline"
        title="لا توجد دروس بعد"
        description="ابدأ برفع أول درس PDF وتسجيل عينة صوتك ليبدأ المعلّم الذكي بشرح المحتوى للطلاب"
        action-label="رفع أول درس"
        action-to="/teacher/upload"
        action-icon="mdi-cloud-upload"
      />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../components/common/PageHeader.vue'
import StatCard from '../components/teacher/StatCard.vue'
import LessonCard from '../components/teacher/LessonCard.vue'
import EmptyState from '../components/common/EmptyState.vue'
import RecentActivityList from '../components/common/RecentActivityList.vue'
import { fetchTeacherContent } from '../api/teacher.js'
import { recentLessons, teacherStats } from '../data/dummyData.js'
import { recentActivity } from '../data/activityData.js'
import { useAuth } from '../composables/useAuth.js'
import { isApiMode } from '../utils/session.js'

const { user } = useAuth()
const teacherName = computed(() => user.value?.name || 'أستاذ أحمد')

const lessons = ref([])
const loading = ref(false)

function mapApiLesson(l) {
  const date = l.created_at ? new Date(l.created_at) : new Date()
  return {
    id: l.id,
    title: l.title,
    subject: l.subject,
    grade: l.grade,
    status: l.status,
    pages: l.page_count || 0,
    students: l.students || 0,
    uploadedAt: date.toLocaleDateString('ar-SY'),
  }
}

const displayStats = computed(() => {
  if (!isApiMode() || !lessons.value.length) return teacherStats
  const processed = lessons.value.filter((l) => l.status === 'processed').length
  return [
    { ...teacherStats[0], value: String(lessons.value.length) },
    { ...teacherStats[1], value: String(processed * 12) },
    { ...teacherStats[2], value: String(processed * 48) },
    { ...teacherStats[3], value: `${Math.min(99, processed * 20)}%` },
  ]
})

onMounted(async () => {
  if (!isApiMode()) {
    lessons.value = recentLessons
    return
  }
  loading.value = true
  try {
    const data = await fetchTeacherContent()
    lessons.value = data.map(mapApiLesson)
  } catch {
    lessons.value = recentLessons
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stat-col {
  animation: slide-up 0.5s cubic-bezier(0.34, 1.2, 0.64, 1) backwards;
}

.upload-teaser {
  background:
    radial-gradient(ellipse 80% 50% at 50% 0%, rgba(34, 211, 238, 0.08) 0%, transparent 60%),
    rgba(8, 12, 24, 0.4);
  border: 2px dashed rgba(124, 108, 240, 0.3);
  transition: border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  cursor: pointer;
}

.upload-teaser:hover {
  border-color: rgba(34, 211, 238, 0.45);
  box-shadow: 0 0 40px rgba(34, 211, 238, 0.1);
  transform: translateY(-2px);
}
</style>
