<template>
  <AuthShell
    subtitle="أنشئ حسابك وابدأ رحلة التعليم الذكي مع EduSpark"
    :footer-link="{ text: 'لديك حساب؟', label: 'تسجيل الدخول', to: '/login' }"
  >
    <template #brand>
      <EduSparkLogo size="auth" class="mb-2" />
    </template>

    <v-form @submit.prevent="handleRegister">
      <v-text-field
        v-model="name"
        label="الاسم الكامل"
        prepend-inner-icon="mdi-account"
        :error-messages="errors.name"
        class="mb-2"
        @update:model-value="clearError('name')"
      />

      <v-text-field
        v-model="email"
        label="البريد الإلكتروني"
        type="email"
        prepend-inner-icon="mdi-email-outline"
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
        :error-messages="errors.password"
        class="mb-2"
        @click:append-inner="showPassword = !showPassword"
        @update:model-value="clearError('password')"
      />

      <v-text-field
        v-model="confirmPassword"
        label="تأكيد كلمة المرور"
        :type="showConfirm ? 'text' : 'password'"
        prepend-inner-icon="mdi-lock-check"
        :append-inner-icon="showConfirm ? 'mdi-eye-off' : 'mdi-eye'"
        :error-messages="errors.confirmPassword"
        class="mb-4"
        @click:append-inner="showConfirm = !showConfirm"
        @update:model-value="clearError('confirmPassword')"
      />

      <p class="text-subtitle-2 font-weight-medium mb-2 text-medium-emphasis">نوع الحساب</p>
      <v-btn-toggle
        v-model="role"
        mandatory
        color="primary"
        variant="outlined"
        divided
        class="role-toggle w-100 mb-2"
      >
        <v-btn value="teacher" class="flex-grow-1" prepend-icon="mdi-school">معلم</v-btn>
        <v-btn value="student" class="flex-grow-1" prepend-icon="mdi-account-school">طالب</v-btn>
      </v-btn-toggle>
      <p v-if="errors.role" class="text-caption text-error mb-4">{{ errors.role }}</p>

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
        إنشاء حساب
      </v-btn>

      <p class="text-center text-caption text-medium-emphasis">
        بالتسجيل، أنت توافق على شروط استخدام منصة EduSpark
      </p>
    </v-form>
  </AuthShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import AuthShell from '../components/auth/AuthShell.vue'
import EduSparkLogo from '../components/auth/EduSparkLogo.vue'
import { useAuth } from '../composables/useAuth.js'
import { validateRegister } from '../utils/validate.js'
import { getErrorMessage } from '../api/client.js'

const { register } = useAuth()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const role = ref('student')
const showPassword = ref(false)
const showConfirm = ref(false)
const loading = ref(false)
const submitError = ref('')
const errors = reactive({})

function clearError(field) {
  delete errors[field]
  submitError.value = ''
}

async function handleRegister() {
  Object.keys(errors).forEach((k) => delete errors[k])
  const validation = validateRegister({
    name: name.value,
    email: email.value,
    password: password.value,
    confirmPassword: confirmPassword.value,
    role: role.value,
  })
  Object.assign(errors, validation)
  if (Object.keys(validation).length) return

  loading.value = true
  submitError.value = ''
  try {
    await register({
      name: name.value,
      email: email.value,
      password: password.value,
      role: role.value,
    })
  } catch (err) {
    submitError.value = getErrorMessage(err, 'تعذر إنشاء الحساب')
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
