export const interestOptions = [
  { title: 'الرياضيات', value: 'math', icon: 'mdi-calculator' },
  { title: 'العلوم', value: 'science', icon: 'mdi-flask' },
  { title: 'اللغة العربية', value: 'arabic', icon: 'mdi-book-open-variant' },
  { title: 'الفيزياء', value: 'physics', icon: 'mdi-atom' },
  { title: 'البرمجة', value: 'coding', icon: 'mdi-code-tags' },
  { title: 'التاريخ', value: 'history', icon: 'mdi-earth' },
  { title: 'الفنون', value: 'arts', icon: 'mdi-palette' },
  { title: 'اللغات', value: 'languages', icon: 'mdi-translate' },
]

export const difficultyLevels = [
  {
    value: 'easy',
    title: 'سهل',
    description: 'شرح بطيء مع أمثلة كثيرة',
    icon: 'mdi-speedometer-slow',
  },
  {
    value: 'medium',
    title: 'متوسط',
    description: 'توازن بين التفصيل والسرعة',
    icon: 'mdi-speedometer-medium',
  },
  {
    value: 'hard',
    title: 'متقدم',
    description: 'تحديات إضافية ومفاهيم أعمق',
    icon: 'mdi-speedometer',
  },
]

export const defaultProfilePrefs = {
  interests: ['math', 'science'],
  difficulty: 'medium',
}
