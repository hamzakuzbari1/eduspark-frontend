<template>
  <v-card class="glass-card pa-5 pa-md-6" variant="flat">
    <div class="d-flex align-center justify-space-between mb-4">
      <div class="d-flex align-center gap-3 min-width-0">
        <v-avatar
          :class="previewState === 'ready' ? 'eduspark-gradient' : ''"
          :color="previewState === 'ready' ? undefined : 'grey-darken-3'"
          variant="tonal"
          rounded="lg"
          size="44"
        >
          <v-icon :color="previewState === 'ready' ? 'white' : undefined">mdi-file-pdf-box</v-icon>
        </v-avatar>
        <div class="min-width-0">
          <div class="text-subtitle-1 font-weight-bold">معاينة الدرس</div>
          <div class="text-caption text-truncate text-medium-emphasis">
            {{ previewLabel }}
          </div>
        </div>
      </div>
      <v-chip
        v-if="previewState === 'ready'"
        color="success"
        size="small"
        variant="tonal"
        prepend-icon="mdi-check"
      >
        جاهز
      </v-chip>
      <v-chip v-else-if="previewState === 'uploading'" color="secondary" size="small" variant="tonal">
        <v-progress-circular indeterminate size="14" width="2" class="me-1" />
        رفع...
      </v-chip>
      <v-chip v-else-if="previewState === 'error'" color="error" size="small" variant="tonal" prepend-icon="mdi-alert">
        خطأ
      </v-chip>
    </div>

    <div
      class="pdf-preview-surface rounded-xl pa-6 text-center"
      :class="`pdf-preview-surface--${previewState}`"
    >
      <template v-if="previewState === 'error'">
        <v-icon size="56" color="error" class="mb-3">mdi-file-alert</v-icon>
        <div class="text-body-2 text-error">{{ error }}</div>
      </template>
      <template v-else-if="file">
        <div class="preview-glow mb-4">
          <v-icon size="72" color="primary" class="pdf-icon-glow">mdi-file-document-outline</v-icon>
        </div>
        <div class="text-body-1 font-weight-bold mb-1">صفحة 1 من {{ pageCount }}</div>
        <div class="text-caption text-medium-emphasis mb-5">
          سيتم استخراج المحتوى عند المعالجة بالذكاء الاصطناعي
        </div>
        <div class="d-flex justify-center gap-2">
          <v-btn icon variant="tonal" size="small" disabled color="primary">
            <v-icon>mdi-chevron-right</v-icon>
          </v-btn>
          <v-chip variant="outlined" size="small" color="primary">1 / {{ pageCount }}</v-chip>
          <v-btn icon variant="tonal" size="small" disabled color="primary">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
        </div>
      </template>
      <template v-else>
        <v-icon size="56" color="grey-darken-1" class="mb-3 opacity-50">mdi-file-hidden</v-icon>
        <div class="text-body-2 text-medium-emphasis">ارفع ملف PDF لعرض المعاينة</div>
      </template>
    </div>

    <v-row v-if="file && previewState !== 'error'" class="mt-4" dense>
      <v-col cols="6">
        <div class="stat-pill eduspark-gradient-soft text-center pa-3 rounded-xl">
          <div class="text-h6 font-weight-bold text-secondary">{{ pageCount }}</div>
          <div class="text-caption text-medium-emphasis">صفحات</div>
        </div>
      </v-col>
      <v-col cols="6">
        <div class="stat-pill eduspark-gradient-soft text-center pa-3 rounded-xl">
          <div class="text-h6 font-weight-bold text-primary">{{ formatFileSize(file.size) }}</div>
          <div class="text-caption text-medium-emphasis">حجم الملف</div>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { formatFileSize } from '../../utils/format.js'

const props = defineProps({
  file: { type: Object, default: null },
  pageCount: { type: Number, default: 1 },
  uploading: { type: Boolean, default: false },
  error: { type: String, default: null },
})

const previewState = computed(() => {
  if (props.error) return 'error'
  if (props.uploading) return 'uploading'
  if (props.file) return 'ready'
  return 'empty'
})

const previewLabel = computed(() => {
  if (props.error) return 'فشل الرفع'
  if (props.file) return props.file.name
  return 'في انتظار الملف'
})
</script>

<style scoped>
.pdf-preview-surface {
  background:
    linear-gradient(180deg, rgba(124, 108, 240, 0.06) 0%, rgba(8, 12, 24, 0.5) 100%);
  border: 1px dashed rgba(124, 108, 240, 0.25);
  min-height: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.pdf-preview-surface--ready {
  border-color: rgba(52, 211, 153, 0.3);
  box-shadow: inset 0 0 40px rgba(52, 211, 153, 0.05);
}

.pdf-preview-surface--error {
  border-color: rgba(248, 113, 113, 0.35);
  background: rgba(248, 113, 113, 0.05);
}

.preview-glow {
  padding: 20px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.12) 0%, transparent 70%);
}

.stat-pill {
  transition: transform 0.2s ease;
}

.stat-pill:hover {
  transform: translateY(-2px);
}

.min-width-0 {
  min-width: 0;
}
</style>
