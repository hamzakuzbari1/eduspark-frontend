export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(email || '').trim())
}

export function validateLogin({ email, password }) {
  const errors = {}
  if (!email?.trim()) errors.email = 'يرجى إدخال البريد الإلكتروني'
  else if (!isValidEmail(email)) errors.email = 'صيغة البريد الإلكتروني غير صحيحة'
  if (!password) errors.password = 'يرجى إدخال كلمة المرور'
  else if (password.length < 6) errors.password = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'
  return errors
}

export function validateRegister({ name, email, password, confirmPassword, role }) {
  const errors = {}
  if (!name?.trim()) errors.name = 'يرجى إدخال الاسم الكامل'
  if (!email?.trim()) errors.email = 'يرجى إدخال البريد الإلكتروني'
  else if (!isValidEmail(email)) errors.email = 'صيغة البريد الإلكتروني غير صحيحة'
  if (!password) errors.password = 'يرجى إدخال كلمة المرور'
  else if (password.length < 6) errors.password = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'
  if (password !== confirmPassword) errors.confirmPassword = 'كلمتا المرور غير متطابقتين'
  if (!role) errors.role = 'يرجى اختيار نوع الحساب'
  return errors
}
