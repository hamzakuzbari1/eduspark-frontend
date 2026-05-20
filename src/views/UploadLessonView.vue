<template>
  <div class="upload-page page-container slide-up-enter-active">
    <PageHeader
      eyebrow="الميزة الأساسية"
      eyebrow-icon="mdi-creation"
      title="رفع درس جديد"
      :gradient-title="true"
      subtitle="ارفع ملف PDF وسجّل 30 ثانية من صوتك — سيشرح الذكاء الاصطناعي الدرس بأسلوبك وبلهجتك السورية"
    />

    <UploadCard
      class="mb-6 mb-md-8"
      :file="file"
      :uploading="uploading"
      :progress="progress"
      :error="error"
      :subtitle="`PDF · حتى ${maxSizeLabel}`"
      @select="onPdfSelect"
      @remove="clearFile"
      @dismiss-error="dismissError"
    />

    <v-row class="upload-grid" align="start">
      <v-col cols="12" lg="7">
        <v-row class="mb-4 mb-md-6" dense>
          <v-col cols="12" sm="6">
            <v-select
              v-model="subject"
              :items="subjects"
              item-title="title"
              item-value="value"
              label="المادة *"
              prepend-inner-icon="mdi-book-education"
              class="em-select"
              placeholder="اختر المادة"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-select
              v-model="grade"
              :items="grades"
              item-title="title"
              item-value="value"
              label="الصف الدراسي (1–12) *"
              prepend-inner-icon="mdi-school"
              class="em-select"
              placeholder="اختر الصف"
            />
          </v-col>
        </v-row>

        <VoiceRecorder
          v-model:ready="voiceReady"
          @update:audio-blob="voiceBlob = $event"
          class="mb-6"
        />

        <v-alert
          v-if="processError"
          type="error"
          variant="tonal"
          class="mb-4 rounded-lg"
          closable
          @click:close="processError = ''"
        >
          {{ processError }}
        </v-alert>

        <v-btn
          size="x-large"
          block
          rounded="lg"
          class="btn-glow process-btn"
          :disabled="!canProcess"
          :loading="processing"
          prepend-icon="mdi-creation"
          @click="processLesson"
        >
          معالجة الدرس بالذكاء الاصطناعي
        </v-btn>

        <v-fade-transition>
          <v-alert
            v-if="!canProcess && showValidation"
            type="warning"
            variant="tonal"
            class="mt-4 glass-card"
            density="compact"
            rounded="lg"
          >
            أكمل جميع الخطوات: PDF، المادة، الصف، وتسجيل الصوت
          </v-alert>
        </v-fade-transition>
      </v-col>

      <v-col cols="12" lg="5">
        <PdfPreviewCard
          :file="file"
          :page-count="estimatedPages"
          :uploading="uploading"
          :error="error"
          class="mb-4 mb-md-6"
        />

        <UploadChecklist :items="checklistItems" class="mb-4 mb-md-6" />

        <v-card class="glass-card pa-5 pa-md-6" variant="flat">
          <h4 class="text-subtitle-1 font-weight-bold mb-4 d-flex align-center gap-2">
            <v-icon color="secondary" size="20">mdi-route</v-icon>
            خطوات المعالجة
          </h4>
          <v-timeline side="end" density="compact" truncate-line="both" class="timeline-dark">
            <v-timeline-item
              v-for="(step, i) in processSteps"
              :key="i"
              :dot-color="stepDotColor(i)"
              size="small"
              :icon="stepIcon(i)"
            >
              <div
                class="text-body-2"
                :class="stepTextClass(i)"
              >
                {{ step }}
              </div>
            </v-timeline-item>
          </v-timeline>
        </v-card>
      </v-col>
    </v-row>

    <LoadingOverlay
      :show="processing"
      :progress="processProgress"
      :step="currentStep"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '../components/common/PageHeader.vue'
import UploadChecklist from '../components/common/UploadChecklist.vue'
import UploadCard from '../components/common/UploadCard.vue'
import PdfPreviewCard from '../components/teacher/PdfPreviewCard.vue'
import VoiceRecorder from '../components/teacher/VoiceRecorder.vue'
import LoadingOverlay from '../components/common/LoadingOverlay.vue'
import { uploadPdfApi, uploadVoiceApi, processLessonApi } from '../api/teacher.js'
import { getErrorMessage } from '../api/client.js'
import { usePdfUpload } from '../composables/usePdfUpload.js'
import { MAX_PDF_SIZE_LABEL } from '../constants/app.js'
import { subjects, grades } from '../data/dummyData.js'
import { isApiMode } from '../utils/session.js'

const router = useRouter()
const maxSizeLabel = MAX_PDF_SIZE_LABEL

const {
  file,
  uploading,
  progress,
  error,
  estimatedPages,
  isReady: pdfReady,
  handleFileSelect,
  clearFile,
  dismissError,
} = usePdfUpload()

const subject = ref(null)
const grade = ref(null)
const voiceReady = ref(false)
const voiceBlob = ref(null)
const processing = ref(false)
const processError = ref('')
const processProgress = ref(0)
const currentStep = ref(0)
const showValidation = ref(false)

const processSteps = [
  'رفع ملف PDF',
  'استخراج المحتوى',
  'تحليل عينة الصوت',
  'بناء أسلوب الشرح',
  'تفعيل المعلّم الذكي',
]

const checklistItems = computed(() => [
  { key: 'pdf', label: 'رفع ملف PDF', done: pdfReady.value },
  { key: 'subject', label: 'اختيار المادة', done: !!subject.value },
  { key: 'grade', label: 'اختيار الصف', done: !!grade.value },
  { key: 'voice', label: 'تسجيل عينة الصوت (30 ث)', done: voiceReady.value },
])

const canProcess = computed(() =>
  checklistItems.value.every((i) => i.done),
)

async function onPdfSelect(candidate) {
  await handleFileSelect(candidate)
}

function stepDotColor(i) {
  if (processing.value && currentStep.value >= i) return 'secondary'
  const idleDone = [
    pdfReady.value,
    pdfReady.value,
    voiceReady.value,
    voiceReady.value && subject.value && grade.value,
    canProcess.value,
  ]
  if (idleDone[i]) return 'success'
  return 'grey-darken-2'
}

function stepIcon(i) {
  if (processing.value && currentStep.value > i) return 'mdi-check'
  if (!processing.value && stepDotColor(i) === 'success') return 'mdi-check'
  return undefined
}

function stepTextClass(i) {
  const active =
    (processing.value && currentStep.value >= i) ||
    (!processing.value && stepDotColor(i) === 'success')
  return active ? 'font-weight-bold text-secondary' : 'text-medium-emphasis'
}

function resolveSubjectLabel() {
  return subjects.find((s) => s.value === subject.value)?.title || subject.value
}

function resolveGradeLabel() {
  return grades.find((g) => g.value === grade.value)?.title || grade.value
}

async function runProgressAnimation(maxStep) {
  for (let step = 0; step < maxStep; step++) {
    currentStep.value = step
    const target = ((step + 1) / processSteps.length) * 100
    while (processProgress.value < target) {
      await delay(120)
      processProgress.value = Math.min(target, processProgress.value + 4)
    }
    await delay(300)
  }
}

async function processLesson() {
  showValidation.value = true
  if (!canProcess.value) return

  processing.value = true
  processError.value = ''
  processProgress.value = 0
  currentStep.value = 0

  try {
    if (isApiMode() && file.value) {
      await runProgressAnimation(2)
      const pdfRes = await uploadPdfApi({
        file: file.value,
        subject: resolveSubjectLabel(),
        grade: resolveGradeLabel(),
        title: file.value.name?.replace(/\.pdf$/i, '') || 'درس جديد',
      })
      const lessonId = pdfRes.lesson_id

      if (voiceBlob.value) {
        const voiceFile = new File([voiceBlob.value], 'voice-sample.webm', {
          type: voiceBlob.value.type || 'audio/webm',
        })
        await uploadVoiceApi({ file: voiceFile, lessonId })
      }

      currentStep.value = 3
      processProgress.value = 75
      const result = await processLessonApi(lessonId)
      if (result.status === 'error') {
        throw new Error(result.message || 'فشلت معالجة الدرس')
      }
      processProgress.value = 100
      currentStep.value = processSteps.length - 1
    } else {
      for (let step = 0; step < processSteps.length; step++) {
        currentStep.value = step
        const target = ((step + 1) / processSteps.length) * 100
        while (processProgress.value < target) {
          await delay(120)
          processProgress.value = Math.min(target, processProgress.value + 4)
        }
        await delay(400)
      }
    }
    router.push('/teacher/dashboard')
  } catch (err) {
    processError.value = getErrorMessage(err, 'فشل رفع أو معالجة الدرس')
  } finally {
    processing.value = false
  }
}

function delay(ms) {
  return new Promise((r) => setTimeout(r, ms))
}
</script>

<style scoped>
.upload-page {
  max-width: 1280px;
  margin: 0 auto;
}

.upload-hero {
  position: relative;
  overflow: hidden;
}

.upload-hero::after {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.4), transparent);
}

.process-btn {
  min-height: 56px;
  font-size: 1.05rem !important;
}

.timeline-dark :deep(.v-timeline-divider__dot) {
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.3);
}
</style>
