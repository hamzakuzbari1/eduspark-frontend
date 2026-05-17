<template>
  <v-container fluid class="auth-page fill-height pa-4">
    <v-row align="center" justify="center" class="fill-height">
      <v-col cols="12" sm="10" md="6" lg="5" xl="4">
        <v-card class="auth-card glass-card glass-card--elevated pa-8 pa-md-10" elevation="0">
          <div class="text-center mb-8">
            <slot name="brand">
              <EduSparkLogo size="auth" class="mb-5" />
              <p class="text-caption text-medium-emphasis mb-0">Smarter Learning</p>
            </slot>
            <p class="text-body-1 text-medium-emphasis auth-subtitle">{{ subtitle }}</p>
          </div>
          <slot />
        </v-card>
        <p v-if="footerLink" class="text-center mt-6">
          <span class="text-medium-emphasis">{{ footerLink.text }} </span>
          <router-link :to="footerLink.to" class="auth-link">{{ footerLink.label }}</router-link>
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import EduSparkLogo from './EduSparkLogo.vue'

defineProps({
  subtitle: { type: String, default: 'منصة التعليم الذكي — لهجة سورية' },
  footerLink: { type: Object, default: null },
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
}

.auth-card {
  position: relative;
  z-index: 1;
}

.auth-subtitle {
  margin-top: 1.25rem;
  margin-bottom: 0;
}

.auth-link {
  color: var(--em-cyan);
  text-decoration: none;
  font-weight: 600;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>
