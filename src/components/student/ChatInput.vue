<template>
  <div class="chat-input-bar">
    <v-text-field
      :model-value="modelValue"
      :placeholder="placeholder"
      variant="solo-filled"
      flat
      rounded="xl"
      hide-details
      bg-color="rgba(8, 12, 24, 0.6)"
      color="secondary"
      class="chat-input-field"
      :disabled="disabled"
      @update:model-value="$emit('update:modelValue', $event)"
      @keyup.enter="submit"
    >
      <template #append-inner>
        <v-btn
          icon
          size="small"
          class="btn-glow send-btn"
          :disabled="!modelValue?.trim() || disabled"
          :loading="loading"
          aria-label="إرسال"
          @click="submit"
        >
          <v-icon color="white">mdi-send</v-icon>
        </v-btn>
      </template>
    </v-text-field>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'اكتب سؤالك هنا...' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'send'])

function submit() {
  if (!props.modelValue?.trim() || props.disabled) return
  emit('send')
}
</script>

<style scoped>
.chat-input-field :deep(.v-field) {
  border: 1px solid var(--em-border);
  transition: border-color 0.25s, box-shadow 0.25s;
}

.chat-input-field :deep(.v-field--focused) {
  border-color: rgba(34, 211, 238, 0.45);
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.1);
}

.send-btn {
  transition: transform 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.08);
}
</style>
