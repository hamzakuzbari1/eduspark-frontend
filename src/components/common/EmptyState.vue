<template>
  <v-card class="glass-card empty-state pa-8 pa-md-12 text-center" variant="flat">
    <div class="empty-state__icon mx-auto mb-5">
      <v-icon :icon="icon" :size="iconSize" :color="iconColor" />
    </div>
    <h3 class="text-h6 font-weight-bold mb-2">{{ title }}</h3>
    <p class="text-body-2 text-medium-emphasis mb-6 mx-auto empty-state__desc">
      {{ description }}
    </p>
    <slot name="action">
      <v-btn
        v-if="actionLabel"
        :to="actionTo"
        :prepend-icon="actionIcon"
        class="btn-glow"
        rounded="lg"
        @click="$emit('action')"
      >
        {{ actionLabel }}
      </v-btn>
    </slot>
  </v-card>
</template>

<script setup>
defineProps({
  icon: { type: String, default: 'mdi-folder-open-outline' },
  iconSize: { type: [Number, String], default: 56 },
  iconColor: { type: String, default: 'primary' },
  title: { type: String, required: true },
  description: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
  actionTo: { type: String, default: '' },
  actionIcon: { type: String, default: 'mdi-plus' },
})

defineEmits(['action'])
</script>

<style scoped>
.empty-state__icon {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle, rgba(124, 108, 240, 0.15) 0%, transparent 70%);
}

.empty-state__desc {
  max-width: 360px;
}
</style>
