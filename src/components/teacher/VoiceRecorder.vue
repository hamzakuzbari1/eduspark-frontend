<template>
  <v-card class="glass-card glass-card--elevated pa-6 pa-md-8" variant="flat">
    <div class="d-flex align-center gap-3 mb-6 flex-wrap">
      <v-avatar size="48" class="eduspark-gradient" rounded="lg">
        <v-icon color="white">mdi-waveform</v-icon>
      </v-avatar>
      <div class="flex-grow-1">
        <span class="section-eyebrow mb-0">الخطوة الثانية</span>
        <div class="text-h6 font-weight-bold">عينة الصوت · {{ maxSeconds }} ثانية</div>
        <div class="text-caption text-medium-emphasis">
          يتعلّم الذكاء الاصطناعي أسلوب شرحك ولهجتك السورية
        </div>
      </div>
      <v-chip
        v-if="ready"
        color="success"
        variant="tonal"
        size="small"
        prepend-icon="mdi-check"
      >
        مكتمل
      </v-chip>
    </div>

    <div class="recorder-visual text-center py-8 px-4">
      <div class="timer-display mb-6" :class="{ 'timer-display--active': recording }">
        <span class="timer-value">{{ formattedTime }}</span>
        <span class="timer-max">/ 00:{{ String(maxSeconds).padStart(2, '0') }}</span>
        <span v-if="recording" class="timer-remaining">
          متبقي {{ remainingSeconds }} ث
        </span>
      </div>

      <div class="waveform d-flex justify-center align-end gap-1 mb-8" style="height: 64px">
        <div
          v-for="(h, i) in barHeights"
          :key="i"
          class="waveform-bar"
          :class="{ 'waveform-bar--active': recording }"
          :style="{
            height: `${h}px`,
            animationDelay: recording ? `${i * 0.05}s` : '0s',
          }"
        />
      </div>

      <button
        type="button"
        class="mic-glow mx-auto d-block"
        :class="{ 'mic-glow--recording': recording }"
        :aria-label="recording ? 'إيقاف التسجيل' : 'بدء التسجيل'"
        @click="toggleRecording"
      >
        <Transition name="fade" mode="out-in">
          <v-icon :key="recording ? 'stop' : 'mic'" color="white" size="44">
            {{ recording ? 'mdi-stop' : 'mdi-microphone' }}
          </v-icon>
        </Transition>
      </button>

      <p class="recorder-status mt-6 mb-0" :class="statusClass">
        {{ statusText }}
      </p>
    </div>

    <v-progress-linear
      :model-value="progressPercent"
      height="6"
      rounded
      class="progress-glow mb-2"
      :color="recording ? 'error' : ready ? 'success' : 'primary'"
      bg-color="rgba(124, 108, 240, 0.12)"
    />

    <v-fade-transition>
      <div
        v-if="ready && !recording"
        class="success-banner mt-4 pa-3 rounded-xl d-flex align-center gap-2"
      >
        <v-icon color="success">mdi-check-decagram</v-icon>
        <span class="text-body-2">تم حفظ عينة الصوت — جاهزة للمعالجة بالذكاء الاصطناعي</span>
      </div>
    </v-fade-transition>
  </v-card>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useVoiceRecorder } from '../../composables/useVoiceRecorder.js'

const props = defineProps({
  maxSeconds: { type: Number, default: 30 },
})

const emit = defineEmits(['update:ready'])

const {
  recording,
  ready,
  barHeights,
  formattedTime,
  progressPercent,
  remainingSeconds,
  maxSeconds,
  toggleRecording,
} = useVoiceRecorder(props.maxSeconds)

const statusText = computed(() => {
  if (recording.value) return 'جاري التسجيل — اضغط للإيقاف'
  if (ready.value) return 'تم التسجيل · اضغط لإعادة التسجيل'
  return 'اضغط على الميكروفون لبدء التسجيل'
})

const statusClass = computed(() => ({
  'recorder-status--active': recording.value,
  'recorder-status--done': ready.value && !recording.value,
}))

watch(ready, (val) => emit('update:ready', val), { immediate: true })
</script>

<style scoped>
.recorder-visual {
  background:
    radial-gradient(ellipse 80% 60% at 50% 100%, rgba(124, 108, 240, 0.18) 0%, transparent 60%),
    rgba(8, 12, 24, 0.5);
  border-radius: 20px;
  border: 1px solid rgba(124, 108, 240, 0.15);
}

.timer-value {
  font-family: 'Cairo', monospace;
  font-size: clamp(2.5rem, 6vw, 3.25rem);
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  background: linear-gradient(135deg, #e8ecf4 0%, #22d3ee 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.timer-display--active .timer-value {
  background: linear-gradient(135deg, #fca5a5 0%, #f87171 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

.timer-max {
  display: block;
  font-size: 0.85rem;
  color: var(--em-text-muted);
  margin-top: 4px;
}

.timer-remaining {
  display: block;
  font-size: 0.75rem;
  color: var(--em-cyan);
  margin-top: 8px;
}

.recorder-status {
  color: var(--em-text-muted);
  font-size: 0.95rem;
  transition: color 0.25s;
}

.recorder-status--active {
  color: #f87171;
}

.recorder-status--done {
  color: #34d399;
}

.success-banner {
  background: rgba(52, 211, 153, 0.1);
  border: 1px solid rgba(52, 211, 153, 0.28);
}
</style>
