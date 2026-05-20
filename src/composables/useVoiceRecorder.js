import { computed, onUnmounted, ref } from 'vue'
import { VOICE_SAMPLE_SECONDS } from '../constants/app.js'

const BAR_COUNT = 16

export function useVoiceRecorder(maxSeconds = VOICE_SAMPLE_SECONDS) {
  const recording = ref(false)
  const elapsed = ref(0)
  const ready = ref(false)
  const audioBlob = ref(null)
  const barHeights = ref(Array(BAR_COUNT).fill(10))

  let tickTimer = null
  let waveTimer = null
  let mediaRecorder = null
  let mediaStream = null
  let chunks = []

  const formattedTime = computed(() => {
    const s = Math.min(elapsed.value, maxSeconds)
    return `00:${String(s).padStart(2, '0')}`
  })

  const progressPercent = computed(() => (elapsed.value / maxSeconds) * 100)
  const remainingSeconds = computed(() => Math.max(0, maxSeconds - elapsed.value))

  function animateWaveform() {
    waveTimer = setInterval(() => {
      barHeights.value = barHeights.value.map(() => 8 + Math.random() * 44)
    }, 90)
  }

  function stopWaveform() {
    if (waveTimer) {
      clearInterval(waveTimer)
      waveTimer = null
    }
    barHeights.value = Array(BAR_COUNT).fill(10)
  }

  function cleanupStream() {
    if (mediaStream) {
      mediaStream.getTracks().forEach((t) => t.stop())
      mediaStream = null
    }
  }

  async function startRecording() {
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      // Demo fallback when mic unavailable
      elapsed.value = 0
      recording.value = true
      ready.value = false
      audioBlob.value = new Blob(['demo'], { type: 'audio/webm' })
      animateWaveform()
      tickTimer = setInterval(() => {
        elapsed.value += 1
        if (elapsed.value >= maxSeconds) stopRecording(true)
      }, 1000)
      return
    }

    chunks = []
    mediaRecorder = new MediaRecorder(mediaStream)
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data)
    }
    mediaRecorder.onstop = () => {
      if (chunks.length) {
        audioBlob.value = new Blob(chunks, { type: mediaRecorder.mimeType || 'audio/webm' })
      }
      cleanupStream()
    }
    mediaRecorder.start()

    elapsed.value = 0
    recording.value = true
    ready.value = false
    animateWaveform()

    tickTimer = setInterval(() => {
      elapsed.value += 1
      if (elapsed.value >= maxSeconds) stopRecording(true)
    }, 1000)
  }

  function stopRecording(completed = false) {
    recording.value = false
    stopWaveform()
    if (tickTimer) {
      clearInterval(tickTimer)
      tickTimer = null
    }
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
    } else {
      cleanupStream()
    }
    if (elapsed.value > 0 || completed) {
      ready.value = true
      if (!audioBlob.value) {
        audioBlob.value = new Blob(['demo'], { type: 'audio/webm' })
      }
    }
  }

  function toggleRecording() {
    if (recording.value) stopRecording()
    else startRecording()
  }

  function reset() {
    stopRecording()
    elapsed.value = 0
    ready.value = false
    audioBlob.value = null
    chunks = []
  }

  onUnmounted(() => {
    if (tickTimer) clearInterval(tickTimer)
    stopWaveform()
    cleanupStream()
  })

  return {
    recording,
    elapsed,
    ready,
    audioBlob,
    barHeights,
    barCount: BAR_COUNT,
    formattedTime,
    progressPercent,
    remainingSeconds,
    maxSeconds,
    toggleRecording,
    reset,
  }
}
