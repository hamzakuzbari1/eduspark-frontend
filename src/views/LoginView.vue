<template>
  <AuthShell
    subtitle="معلّم ذكي يشرح الدروس بأسلوبك وبلهجتك السورية"
    :footer-link="{ text: 'ليس لديك حساب؟', label: 'إنشاء حساب', to: '/register' }"
  >
    <template #brand>
      <EduSparkLogo size="auth" class="mb-2" />
    </template>

    <v-form @submit.prevent="handleLogin">
      <v-text-field
        v-model="email"
        label="البريد الإلكتروني"
        type="email"
        prepend-inner-icon="mdi-email-outline"
        autocomplete="email"
        :error-messages="errors.email"
        class="mb-2"
        @update:model-value="clearError('email')"
      />

      <v-text-field
        v-model="password"
        label="كلمة المرور"
        :type="showPassword ? 'text' : 'password'"
        prepend-inner-icon="mdi-lock-outline"
        :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
        autocomplete="current-password"
        :error-messages="errors.password"
        class="mb-4"
        @click:append-inner="showPassword = !showPassword"
        @update:model-value="clearError('password')"
      />

      <p class="text-subtitle-2 font-weight-medium mb-2 text-medium-emphasis">نوع الحساب</p>
      <v-btn-toggle
        v-model="role"
        mandatory
        color="primary"
        variant="outlined"
        divided
        class="role-toggle w-100 mb-6"
      >
        <v-btn value="teacher" class="flex-grow-1" prepend-icon="mdi-school">معلم</v-btn>
        <v-btn value="student" class="flex-grow-1" prepend-icon="mdi-account-school">طالب</v-btn>
      </v-btn-toggle>

      <v-alert
        v-if="submitError"
        type="error"
        variant="tonal"
        density="compact"
        class="mb-4 rounded-lg"
      >
        {{ submitError }}
      </v-alert>

      <v-btn
        type="submit"
        size="x-large"
        block
        rounded="lg"
        class="btn-glow mb-4"
        :loading="loading"
      >
        تسجيل الدخول
      </v-btn>

      <p class="text-center text-caption text-medium-emphasis">
        بتسجيلك، أنت توافق على شروط استخدام المنصة
      </p>
    </v-form>
  </AuthShell>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import AuthShell from '../components/auth/AuthShell.vue'
import EduSparkLogo from '../components/auth/EduSparkLogo.vue'
import { useAuth } from '../composables/useAuth.js'
import { validateLogin } from '../utils/validate.js'
import { getErrorMessage } from '../api/client.js'

const route = useRoute()
const { login } = useAuth()

const email = ref('teacher@eduspark.sy')
const password = ref('teacher123')
const role = ref('teacher')
const showPassword = ref(false)
const loading = ref(false)
const submitError = ref('')
const errors = reactive({})

onMounted(() => {
  if (route.query.role === 'student') role.value = 'student'
})

function clearError(field) {
  delete errors[field]
  submitError.value = ''
}

async function handleLogin() {
  Object.keys(errors).forEach((k) => delete errors[k])
  const validation = validateLogin({ email: email.value, password: password.value })
  Object.assign(errors, validation)
  if (Object.keys(validation).length) return

  loading.value = true
  submitError.value = ''
  try {
    await login({
      email: email.value,
      password: password.value,
      name: role.value === 'teacher' ? 'أستاذ أحمد' : 'سارة محمد',
      role: role.value,
    })
  } catch (err) {
    submitError.value = getErrorMessage(err, 'تعذر تسجيل الدخول')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.role-toggle :deep(.v-btn) {
  letter-spacing: 0;
}
</style>