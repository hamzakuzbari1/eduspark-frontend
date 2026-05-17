<template>
  <div
    ref="zoneRef"
    class="upload-zone pa-6 pa-md-14 text-center"
    :class="zoneClasses"
    @dragenter.prevent="onDragEnter"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
    @click="onZoneClick"
    @keydown.enter.space.prevent="triggerFileInput"
    role="button"
    tabindex="0"
    :aria-label="ariaLabel"
  >
    <input
      ref="fileInput"
      type="file"
      accept="application/pdf,.pdf"
      class="d-none"
      @change="onFileSelect"
    />

    <!-- Error -->
    <div v-if="error && !uploading" class="upload-state">
      <v-icon size="64" color="error" class="mb-4">mdi-alert-circle-outline</v-icon>
      <h3 class="section-title text-h5 mb-2 text-error">تعذّر رفع الملف</h3>
      <p class="section-subtitle mx-auto mb-6 text-error">{{ error }}</p>
      <v-btn class="btn-glow-outline me-2" prepend-icon="mdi-refresh" @click.stop="$emit('dismiss-error')">
        إغلاق
      </v-btn>
      <v-btn class="btn-glow-outline" prepend-icon="mdi-folder-open" @click.stop="triggerFileInput">
        اختيار ملف آخر
      </v-btn>
    </div>

    <!-- Uploading -->
    <div v-else-if="uploading" class="upload-state">
      <div class="upload-icon-wrap">
        <v-progress-circular
          :model-value="progress"
          :size="100"
          :width="6"
          color="secondary"
          class="mb-2"
        >
          <v-icon size="40" color="primary">mdi-file-pdf-box</v-icon>
        </v-progress-circular>
      </div>
      <h3 class="section-title text-h5 mb-2">جاري رفع الملف...</h3>
      <p class="text-body-2 text-medium-emphasis mb-6 text-truncate px-4">{{ file?.name }}</p>
      <div class="progress-wrap mx-auto">
        <v-progress-linear
          :model-value="progress"
          height="10"
          rounded
          class="progress-glow"
          bg-color="rgba(124, 108, 240, 0.15)"
          color="primary"
        />
        <div class="d-flex justify-space-between mt-2 text-caption">
          <span class="text-medium-emphasis">التقدّم</span>
          <span class="font-weight-bold text-secondary">{{ Math.round(progress) }}%</span>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <template v-else-if="!file">
      <div class="upload-icon-wrap">
        <div class="pdf-hero-icon">
          <v-icon size="96" color="primary" class="pdf-icon-glow">mdi-file-pdf-box</v-icon>
        </div>
      </div>
      <span class="section-eyebrow">
        <v-icon size="14">mdi-star-four-points</v-icon>
        الخطوة الأولى
      </span>
      <h3 class="section-title text-h4 mb-2">اسحب ملف PDF وأفلته هنا</h3>
      <p class="section-subtitle mx-auto mb-8">
        أو انقر لاختيار ملف — PDF فقط · حتى {{ maxSizeLabel }}
      </p>
      <v-btn
        class="btn-glow-outline"
        size="large"
        prepend-icon="mdi-folder-open"
        rounded="lg"
        @click.stop="triggerFileInput"
      >
        اختيار ملف PDF
      </v-btn>
    </template>

    <!-- Success -->
    <template v-else>
      <div class="upload-state upload-state--success">
        <Transition name="fade">
          <div v-if="showSuccessFlash" class="success-check mb-4">
            <v-icon size="48" color="success">mdi-check-circle</v-icon>
          </div>
        </Transition>
        <div class="upload-icon-wrap">
          <v-icon size="80" color="success" class="pdf-icon-glow">mdi-file-pdf-box</v-icon>
        </div>
        <h3 class="section-title text-h5 mb-1 text-truncate px-2">{{ file.name }}</h3>
        <p class="section-subtitle mb-4">{{ formatFileSize(file.size) }}</p>
        <v-chip color="success" variant="tonal" prepend-icon="mdi-check" class="mb-4">
          تم الرفع بنجاح
        </v-chip>
        <div class="d-flex justify-center gap-2 flex-wrap">
          <v-btn
            variant="text"
            color="error"
            size="small"
            prepend-icon="mdi-close"
            @click.stop="$emit('remove')"
          >
            إزالة الملف
          </v-btn>
          <v-btn
            class="btn-glow-outline"
            size="small"
            prepend-icon="mdi-swap-horizontal"
            @click.stop="triggerFileInput"
          >
            استبدال
          </v-btn>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { MAX_PDF_SIZE_LABEL } from '../../constants/app.js'
import { formatFileSize } from '../../utils/format.js'

const props = defineProps({
  file: { type: Object, default: null },
  uploading: { type: Boolean, default: false },
  progress: { type: Number, default: 0 },
  error: { type: String, default: null },
})

const emit = defineEmits(['select', 'remove', 'dismiss-error'])

const fileInput = ref(null)
const zoneRef = ref(null)
const dragCounter = ref(0)
const showSuccessFlash = ref(false)

const maxSizeLabel = MAX_PDF_SIZE_LABEL

const zoneClasses = computed(() => ({
  'upload-zone--active': dragCounter.value > 0,
  'upload-zone--has-file': !!props.file && !props.uploading && !props.error,
  'upload-zone--error': !!props.error,
  'upload-zone--success': showSuccessFlash.value,
  'cursor-pointer': !props.uploading,
}))

const ariaLabel = computed(() => {
  if (props.error) return 'خطأ في الرفع، انقر لإعادة المحاولة'
  if (props.uploading) return 'جاري رفع الملف'
  if (props.file) return `ملف مرفوع: ${props.file.name}`
  return 'منطقة رفع PDF، اسحب الملف أو انقر للاختيار'
})

watch(
  () => props.uploading,
  (val, oldVal) => {
    if (oldVal && !val && props.file && !props.error) {
      showSuccessFlash.value = true
      setTimeout(() => { showSuccessFlash.value = false }, 1200)
    }
  },
)

function triggerFileInput() {
  if (!props.uploading) fileInput.value?.click()
}

function onZoneClick(e) {
  if (props.uploading || props.error) return
  if (e.target.closest('.v-btn')) return
  if (!props.file) triggerFileInput()
}

function onDragEnter() {
  dragCounter.value += 1
}

function onDragOver() {
  /* required for drop */
}

function onDragLeave() {
  dragCounter.value = Math.max(0, dragCounter.value - 1)
}

function onDrop(e) {
  dragCounter.value = 0
  const dropped = e.dataTransfer?.files?.[0]
  if (dropped) emit('select', dropped)
}

function onFileSelect(e) {
  const selected = e.target.files?.[0]
  if (selected) emit('select', selected)
  e.target.value = ''
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:focus-visible {
  outline: 2px solid var(--em-cyan);
  outline-offset: 4px;
}

.progress-wrap {
  max-width: 420px;
  width: 100%;
}

.pdf-hero-icon {
  padding: 28px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(124, 108, 240, 0.22) 0%, transparent 70%);
}

.success-check {
  animation: pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.upload-state--success {
  animation: fade-in 0.4s ease;
}

@keyframes pop {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
