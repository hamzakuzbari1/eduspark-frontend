<template>
  <div
    class="eduspark-logo"
    :class="sizeClass"
  >
    <div class="eduspark-logo__ring" aria-hidden="true" />
    <div class="eduspark-logo__glass">
      <img
        :src="logoSrc"
        alt="EduSpark — Smarter Learning"
        class="eduspark-logo__img"
        loading="eager"
        decoding="async"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import logoSrc from '../../assets/logo.png'

const props = defineProps({
  size: {
    type: String,
    default: 'auth',
    validator: (v) => ['auth', 'sidebar', 'compact'].includes(v),
  },
  compact: { type: Boolean, default: false },
})

const sizeClass = computed(() => {
  if (props.compact) return 'eduspark-logo--compact'
  return `eduspark-logo--${props.size}`
})
</script>

<style scoped>
.eduspark-logo {
  position: relative;
  margin: 0 auto;
  cursor: default;
  aspect-ratio: 1 / 1;
  transition: transform 0.45s cubic-bezier(0.34, 1.2, 0.64, 1);
}

.eduspark-logo--auth {
  width: clamp(140px, 32vw, 172px);
  height: clamp(140px, 32vw, 172px);
}

.eduspark-logo--sidebar {
  width: 72px;
  height: 72px;
}

.eduspark-logo--compact {
  width: clamp(108px, 24vw, 132px);
  height: clamp(108px, 24vw, 132px);
}

.eduspark-logo:hover {
  transform: translateY(-4px) scale(1.02);
}

.eduspark-logo__ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  background: conic-gradient(
    from 180deg,
    rgba(124, 108, 240, 0.9),
    rgba(34, 211, 238, 0.75),
    rgba(168, 85, 247, 0.85),
    rgba(124, 108, 240, 0.9)
  );
  opacity: 0.85;
  filter: blur(1px);
  animation: logo-ring-spin 10s linear infinite;
  z-index: 0;
}

.eduspark-logo:hover .eduspark-logo__ring {
  opacity: 1;
  animation-duration: 6s;
}

.eduspark-logo__glass {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(12, 18, 40, 0.55);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(124, 108, 240, 0.35);
  box-shadow:
    0 0 32px rgba(124, 108, 240, 0.45),
    0 0 64px rgba(34, 211, 238, 0.2),
    inset 0 0 24px rgba(124, 108, 240, 0.12);
  transition: box-shadow 0.45s ease, border-color 0.45s ease;
}

.eduspark-logo:hover .eduspark-logo__glass {
  border-color: rgba(34, 211, 238, 0.5);
  box-shadow:
    0 0 48px rgba(124, 108, 240, 0.65),
    0 0 80px rgba(34, 211, 238, 0.35),
    0 0 120px rgba(168, 85, 247, 0.25),
    inset 0 0 28px rgba(34, 211, 238, 0.15);
}

.eduspark-logo__img {
  width: auto;
  height: auto;
  max-width: 88%;
  max-height: 88%;
  object-fit: contain;
  object-position: center;
  display: block;
  transition: opacity 0.45s ease;
}

.eduspark-logo:hover .eduspark-logo__img {
  opacity: 0.95;
}

.eduspark-logo--sidebar .eduspark-logo__img {
  max-width: 90%;
  max-height: 90%;
}

@keyframes logo-ring-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 600px) {
  .eduspark-logo__ring {
    inset: -4px;
  }

  .eduspark-logo--auth {
    width: clamp(128px, 36vw, 152px);
    height: clamp(128px, 36vw, 152px);
  }
}
</style>
