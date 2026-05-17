<template>
  <v-card class="glass-card glass-card--elevated chat-panel d-flex flex-column h-100" variant="flat">
    <div class="chat-panel__header pa-4 pa-md-5 border-b">
      <div class="d-flex align-center justify-space-between flex-wrap gap-2">
        <div>
          <span class="section-eyebrow mb-1">الشرح التفاعلي</span>
          <h3 class="text-h6 font-weight-bold mb-0">محادثة مع المعلّم الذكي</h3>
        </div>
        <v-chip color="secondary" variant="tonal" size="small" class="ai-live-chip">
          <span class="ai-live-chip__dot" />
          متصل
        </v-chip>
      </div>
      <p v-if="teacherName" class="text-caption text-medium-emphasis mt-2 mb-0">
        بأسلوب {{ teacherName }} · لهجة سورية مبسطة
      </p>
    </div>

    <div ref="messagesEl" class="chat-messages flex-grow-1 pa-4 pa-md-5 chat-scroll">
      <TransitionGroup name="chat-msg">
        <ChatBubble
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
        />
      </TransitionGroup>
      <TypingIndicator v-if="isTyping" />
    </div>

    <div class="pa-4 pa-md-5 border-t chat-panel__footer">
      <ChatInput
        :model-value="modelValue"
        :loading="isTyping"
        :placeholder="placeholder"
        @update:model-value="$emit('update:modelValue', $event)"
        @send="$emit('send')"
      />
    </div>
  </v-card>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import ChatBubble from './ChatBubble.vue'
import ChatInput from './ChatInput.vue'
import TypingIndicator from './TypingIndicator.vue'

defineProps({
  messages: { type: Array, required: true },
  modelValue: { type: String, default: '' },
  isTyping: { type: Boolean, default: false },
  teacherName: { type: String, default: '' },
  placeholder: { type: String, default: 'اكتب سؤالك للمعلّم الذكي...' },
})

defineEmits(['update:modelValue', 'send'])

const messagesEl = ref(null)

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

defineExpose({ scrollToBottom, messagesEl })
</script>

<style scoped>
.chat-panel {
  min-height: min(560px, calc(100vh - 180px));
  max-height: calc(100vh - 120px);
}

.chat-panel__header {
  flex-shrink: 0;
}

.chat-messages {
  overflow-y: auto;
  min-height: 300px;
  max-height: calc(100vh - 320px);
}

.chat-panel__footer {
  flex-shrink: 0;
}

.border-b {
  border-bottom: 1px solid var(--em-border);
}

.border-t {
  border-top: 1px solid var(--em-border);
}

.ai-live-chip__dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--em-cyan);
  margin-inline-end: 6px;
  animation: blink 1.5s ease infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--em-cyan); }
  50% { opacity: 0.35; }
}

.chat-msg-enter-active {
  transition: all 0.35s cubic-bezier(0.34, 1.2, 0.64, 1);
}

.chat-msg-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
</style>
