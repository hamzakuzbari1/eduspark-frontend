<template>
  <div
    class="chat-row d-flex mb-4"
    :class="message.role === 'student' ? 'flex-row-reverse' : ''"
  >
    <v-avatar
      :class="message.role === 'ai' ? 'eduspark-gradient' : 'avatar-student'"
      size="42"
      class="flex-shrink-0"
    >
      <v-icon size="22" :color="message.role === 'ai' ? 'white' : 'white'">
        {{ message.role === 'ai' ? 'mdi-robot-happy' : 'mdi-account' }}
      </v-icon>
    </v-avatar>

    <div
      class="chat-bubble mx-3 pa-4"
      :class="message.role === 'ai' ? 'chat-bubble--ai' : 'chat-bubble--student'"
    >
      <div v-if="message.role === 'ai'" class="ai-label text-caption mb-2 d-flex align-center gap-1">
        <v-icon size="12" color="secondary">mdi-creation</v-icon>
        المعلّم الذكي
      </div>
      <p class="text-body-1 mb-2 lh-relaxed">{{ message.text }}</p>
      <span class="text-caption bubble-time">{{ message.time }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: { type: Object, required: true },
})
</script>

<style scoped>
.chat-bubble {
  max-width: min(85%, 520px);
  border-radius: 18px;
  transition: transform 0.2s ease;
}

.chat-bubble:hover {
  transform: translateY(-1px);
}

.chat-bubble--ai {
  background: rgba(17, 25, 52, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid var(--em-border);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  border-top-right-radius: 4px;
}

.chat-bubble--student {
  background: linear-gradient(135deg, #7c6cf0 0%, #5b4fcf 45%, #22d3ee 100%);
  color: #fff;
  border-top-left-radius: 4px;
  box-shadow:
    0 4px 24px rgba(124, 108, 240, 0.35),
    0 0 20px rgba(34, 211, 238, 0.15);
}

.bubble-time {
  color: rgba(255, 255, 255, 0.65);
}

.chat-bubble--ai .bubble-time {
  color: var(--em-text-muted);
}

.avatar-student {
  background: linear-gradient(135deg, #3b82f6, #22d3ee) !important;
}

.lh-relaxed {
  line-height: 1.7;
}

.ai-label {
  color: var(--em-cyan);
  font-weight: 600;
  letter-spacing: 0.02em;
}
</style>
