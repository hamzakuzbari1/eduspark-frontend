<template>
  <section class="upload-card glass-card glass-card--elevated pa-5 pa-md-8">
    <div v-if="showHeader" class="d-flex align-center justify-space-between flex-wrap gap-3 mb-6">
      <div class="d-flex align-center gap-3">
        <v-avatar size="44" class="eduspark-gradient" rounded="lg">
          <v-icon color="white">mdi-file-pdf-box</v-icon>
        </v-avatar>
        <div>
          <div class="text-h6 font-weight-bold">{{ title }}</div>
          <div class="text-caption text-medium-emphasis">{{ subtitle }}</div>
        </div>
      </div>
      <v-chip v-if="badge" color="secondary" variant="tonal" size="small" prepend-icon="mdi-star-four-points">
        {{ badge }}
      </v-chip>
    </div>
    <PdfUploadBox
      :file="file"
      :uploading="uploading"
      :progress="progress"
      :error="error"
      @select="$emit('select', $event)"
      @remove="$emit('remove')"
      @dismiss-error="$emit('dismiss-error')"
    />
  </section>
</template>

<script setup>
import PdfUploadBox from '../teacher/PdfUploadBox.vue'

defineProps({
  file: { type: Object, default: null },
  uploading: { type: Boolean, default: false },
  progress: { type: Number, default: 0 },
  error: { type: String, default: null },
  title: { type: String, default: 'ملف الدرس' },
  subtitle: { type: String, default: 'PDF · حتى 50 ميجابايت' },
  badge: { type: String, default: 'التركيز الرئيسي' },
  showHeader: { type: Boolean, default: true },
})

defineEmits(['select', 'remove', 'dismiss-error'])
</script>
