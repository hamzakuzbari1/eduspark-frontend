<template>
  <v-card class="glass-card pa-5 pa-md-6" variant="flat">
    <h3 class="text-h6 font-weight-bold mb-4 d-flex align-center gap-2">
      <v-icon color="secondary">mdi-history</v-icon>
      النشاط الأخير
    </h3>
    <v-timeline side="end" density="compact" truncate-line="both" class="activity-timeline">
      <v-timeline-item
        v-for="item in items"
        :key="item.id"
        :dot-color="item.color"
        size="small"
      >
        <div class="d-flex align-start gap-2">
          <v-icon :icon="item.icon" :color="item.color" size="18" class="mt-1" />
          <div>
            <div class="text-body-2 font-weight-medium">{{ item.title }}</div>
            <div class="text-caption text-medium-emphasis">{{ item.time }}</div>
          </div>
        </div>
      </v-timeline-item>
    </v-timeline>
  </v-card>
</template>

<script setup>
defineProps({
  items: { type: Array, required: true },
})
</script>

<style scoped>
.activity-timeline :deep(.v-timeline-divider__dot) {
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.25);
}
</style>
