<template>
  <div class="slide-up-enter-active">
    <PageHeader
      eyebrow="الملف الشخصي"
      title="تفضيلات التعلّم"
      subtitle="خصّص تجربتك مع المعلّم الذكي — اختياراتك تساعد على تخصيص الشرح والاختبارات"
    />

    <v-row>
      <v-col cols="12" lg="8">
        <v-card class="glass-card pa-6 pa-md-8 mb-6" variant="flat">
          <h3 class="text-h6 font-weight-bold mb-2 d-flex align-center gap-2">
            <v-icon color="secondary">mdi-heart-outline</v-icon>
            اهتماماتك
          </h3>
          <p class="text-body-2 text-medium-emphasis mb-4">
            اختر المواضيع التي تهمك (يمكن اختيار أكثر من واحد)
          </p>
          <div class="interests-grid">
            <v-chip
              v-for="opt in interestOptions"
              :key="opt.value"
              :color="prefs.interests.includes(opt.value) ? 'primary' : undefined"
              :variant="prefs.interests.includes(opt.value) ? 'flat' : 'outlined'"
              class="interest-chip pa-4"
              size="large"
              @click="toggleInterest(opt.value)"
            >
              <v-icon start size="18">{{ opt.icon }}</v-icon>
              {{ opt.title }}
            </v-chip>
          </div>
        </v-card>

        <v-card class="glass-card pa-6 pa-md-8 mb-6" variant="flat">
          <h3 class="text-h6 font-weight-bold mb-4 d-flex align-center gap-2">
            <v-icon color="primary">mdi-speedometer</v-icon>
            مستوى الصعوبة
          </h3>
          <v-item-group v-model="prefs.difficulty" mandatory class="difficulty-group">
            <v-row>
              <v-col
                v-for="level in difficultyLevels"
                :key="level.value"
                cols="12"
                md="4"
              >
                <v-item :value="level.value" v-slot="{ isSelected, toggle }">
                  <v-card
                    class="difficulty-card pa-4 h-100"
                    :class="{ 'difficulty-card--active': isSelected }"
                    variant="flat"
                    @click="toggle"
                  >
                    <v-icon :color="isSelected ? 'secondary' : undefined" class="mb-2">
                      {{ level.icon }}
                    </v-icon>
                    <div class="text-subtitle-1 font-weight-bold">{{ level.title }}</div>
                    <div class="text-caption text-medium-emphasis">{{ level.description }}</div>
                  </v-card>
                </v-item>
              </v-col>
            </v-row>
          </v-item-group>
        </v-card>

        <v-alert
          v-if="saveSuccess"
          type="success"
          variant="tonal"
          class="mb-4 rounded-lg"
          closable
          @click:close="saveSuccess = false"
        >
          تم حفظ تفضيلاتك بنجاح — سيأخذها المعلّم الذكي بعين الاعتبار
        </v-alert>

        <v-btn
          size="x-large"
          block
          rounded="lg"
          class="btn-glow"
          :loading="saving"
          prepend-icon="mdi-content-save"
          @click="save"
        >
          حفظ التفضيلات
        </v-btn>
      </v-col>

      <v-col cols="12" lg="4">
        <v-card class="glass-card eduspark-gradient-soft pa-6 mb-4" variant="flat">
          <v-avatar size="64" class="eduspark-gradient mb-4">
            <span class="text-h5 text-white">{{ initials }}</span>
          </v-avatar>
          <h4 class="text-h6 font-weight-bold">{{ displayName }}</h4>
          <p class="text-caption text-medium-emphasis mb-0">{{ userEmail }}</p>
        </v-card>

        <v-card class="glass-card pa-5" variant="flat">
          <h4 class="text-subtitle-2 font-weight-bold mb-3">ملخص التفضيلات</h4>
          <v-list density="compact" class="bg-transparent pa-0">
            <v-list-item class="px-0" prepend-icon="mdi-heart">
              <v-list-item-title class="text-body-2">
                {{ selectedInterestsLabel }}
              </v-list-item-title>
            </v-list-item>
            <v-list-item class="px-0" prepend-icon="mdi-speedometer">
              <v-list-item-title class="text-body-2">
                {{ selectedDifficultyLabel }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import PageHeader from '../../components/common/PageHeader.vue'
import { useAuth } from '../../composables/useAuth.js'
import { getStudentProfilePrefs, setStudentProfilePrefs } from '../../utils/session.js'
import {
  interestOptions,
  difficultyLevels,
  defaultProfilePrefs,
} from '../../data/profileOptions.js'

const { user } = useAuth()

const prefs = reactive({
  interests: [...defaultProfilePrefs.interests],
  difficulty: defaultProfilePrefs.difficulty,
})
const saving = ref(false)
const saveSuccess = ref(false)

const displayName = computed(() => user.value?.name || 'طالب')
const userEmail = computed(() => user.value?.email || '')
const initials = computed(() => {
  const n = displayName.value.trim()
  return n ? n.charAt(0) : 'ط'
})

const selectedInterestsLabel = computed(() => {
  if (!prefs.interests.length) return 'لم تُحدد بعد'
  return interestOptions
    .filter((o) => prefs.interests.includes(o.value))
    .map((o) => o.title)
    .join('، ')
})

const selectedDifficultyLabel = computed(() =>
  difficultyLevels.find((l) => l.value === prefs.difficulty)?.title ?? 'متوسط',
)

onMounted(() => {
  const saved = getStudentProfilePrefs()
  if (saved) {
    prefs.interests = [...(saved.interests || defaultProfilePrefs.interests)]
    prefs.difficulty = saved.difficulty || defaultProfilePrefs.difficulty
  }
})

function toggleInterest(value) {
  const i = prefs.interests.indexOf(value)
  if (i >= 0) prefs.interests.splice(i, 1)
  else prefs.interests.push(value)
}

function save() {
  saving.value = true
  setTimeout(() => {
    setStudentProfilePrefs({ ...prefs })
    saving.value = false
    saveSuccess.value = true
  }, 500)
}
</script>

<style scoped>
.interests-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.interest-chip {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.interest-chip:hover {
  transform: translateY(-2px);
}

.difficulty-card {
  border: 1px solid var(--em-border);
  background: rgba(8, 12, 24, 0.4);
  cursor: pointer;
  transition: all 0.25s ease;
}

.difficulty-card:hover {
  border-color: rgba(34, 211, 238, 0.35);
}

.difficulty-card--active {
  border-color: rgba(34, 211, 238, 0.5);
  background: rgba(34, 211, 238, 0.08);
  box-shadow: 0 0 24px rgba(34, 211, 238, 0.12);
}
</style>
