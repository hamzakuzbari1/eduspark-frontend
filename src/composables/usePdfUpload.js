import { computed, ref } from 'vue'
import {
  ACCEPTED_PDF_TYPES,
  MAX_PDF_SIZE_BYTES,
  MAX_PDF_SIZE_LABEL,
} from '../constants/app.js'
import { estimatePdfPages } from '../utils/format.js'

export function usePdfUpload() {
  const file = ref(null)
  const uploading = ref(false)
  const progress = ref(0)
  const error = ref(null)
  let uploadTimer = null

  const estimatedPages = computed(() => estimatePdfPages(file.value))
  const isReady = computed(() => !!file.value && !uploading.value && !error.value)

  function validatePdf(candidate) {
    if (!candidate) return 'لم يتم اختيار ملف.'
    const isPdf =
      ACCEPTED_PDF_TYPES.includes(candidate.type) ||
      candidate.name?.toLowerCase().endsWith('.pdf')
    if (!isPdf) return 'يُقبل ملفات PDF فقط.'
    if (candidate.size > MAX_PDF_SIZE_BYTES) {
      return `حجم الملف يتجاوز الحد الأقصى (${MAX_PDF_SIZE_LABEL}).`
    }
    if (candidate.size === 0) return 'الملف فارغ. اختر ملفاً صالحاً.'
    return null
  }

  function simulateUpload() {
    return new Promise((resolve) => {
      uploading.value = true
      progress.value = 0
      uploadTimer = setInterval(() => {
        progress.value = Math.min(100, progress.value + Math.random() * 14 + 6)
        if (progress.value >= 100) {
          progress.value = 100
          uploading.value = false
          clearInterval(uploadTimer)
          uploadTimer = null
          resolve()
        }
      }, 220)
    })
  }

  async function handleFileSelect(candidate) {
    error.value = null
    const validationError = validatePdf(candidate)
    if (validationError) {
      error.value = validationError
      return false
    }
    file.value = candidate
    await simulateUpload()
    return true
  }

  function clearFile() {
    if (uploadTimer) {
      clearInterval(uploadTimer)
      uploadTimer = null
    }
    file.value = null
    uploading.value = false
    progress.value = 0
    error.value = null
  }

  function dismissError() {
    error.value = null
  }

  return {
    file,
    uploading,
    progress,
    error,
    estimatedPages,
    isReady,
    handleFileSelect,
    clearFile,
    dismissError,
  }
}
