<template>
  <v-card class="glass-card pa-4 pa-md-5" variant="flat">
    <div class="text-subtitle-2 font-weight-bold mb-3 d-flex align-center gap-2">
      <v-icon color="secondary" size="18">mdi-clipboard-check-outline</v-icon>
      جاهزية المعالجة
    </div>
    <v-list density="compact" class="pa-0 bg-transparent">
      <v-list-item
        v-for="item in items"
        :key="item.key"
        class="px-0 checklist-item"
        :class="{ 'checklist-item--done': item.done }"
      >
        <template #prepend>
          <v-icon
            :color="item.done ? 'success' : 'grey-darken-1'"
            size="20"
          >
            {{ item.done ? 'mdi-check-circle' : 'mdi-circle-outline' }}
          </v-icon>
        </template>
        <v-list-item-title class="text-body-2">{{ item.label }}</v-list-item-title>
      </v-list-item>
    </v-list>
    <v-progress-linear
      :model-value="completionPercent"
      height="6"
      rounded
      class="progress-glow mt-3"
      color="secondary"
      bg-color="rgba(124, 108, 240, 0.12)"
    />
    <div class="text-caption text-medium-emphasis mt-2 text-center">
      {{ doneCount }} / {{ items.length }} مكتمل
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
})

const doneCount = computed(() => props.items.filter((i) => i.done).length)
const completionPercent = computed(() =>
  props.items.length ? (doneCount.value / props.items.length) * 100 : 0,
)
</script>

<style scoped>
.checklist-item {
  transition: opacity 0.2s;
}

.checklist-item--done :deep(.v-list-item-title) {
  color: var(--em-text);
}

.checklist-item:not(.checklist-item--done) :deep(.v-list-item-title) {
  color: var(--em-text-muted);
}
</style>
