<template>
  <div class="typing-row d-flex align-end gap-2 mb-4">
    <v-avatar size="42" class="eduspark-gradient flex-shrink-0">
      <v-icon color="white" size="22">mdi-robot-happy</v-icon>
    </v-avatar>
    <div class="typing-bubble pa-4 rounded-xl">
      <div class="typing-dots d-flex align-center gap-1">
        <span v-for="i in 3" :key="i" class="typing-dot" :style="{ animationDelay: `${i * 0.15}s` }" />
      </div>
      <span class="text-caption text-medium-emphasis ms-3">المعلّم الذكي يكتب...</span>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.typing-bubble {
  background: rgba(17, 25, 52, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid var(--em-border);
  box-shadow: 0 4px 24px rgba(124, 108, 240, 0.15);
  border-top-right-radius: 4px;
  display: flex;
  align-items: center;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--em-cyan);
  animation: typing-bounce 1s ease-in-out infinite;
}

@keyframes typing-bounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-6px);
    opacity: 1;
    box-shadow: 0 0 8px var(--em-cyan);
  }
}
</style>
