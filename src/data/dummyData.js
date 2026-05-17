export const subjects = [
  { title: 'الرياضيات', value: 'math' },
  { title: 'العلوم', value: 'science' },
  { title: 'اللغة العربية', value: 'arabic' },
  { title: 'الفيزياء', value: 'physics' },
  { title: 'الكيمياء', value: 'chemistry' },
  { title: 'التاريخ', value: 'history' },
]

export const grades = Array.from({ length: 12 }, (_, i) => {
  const n = i + 1
  const labels = [
    'الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس', 'السادس',
    'السابع', 'الثامن', 'التاسع', 'العاشر', 'الحادي عشر', 'الثاني عشر',
  ]
  return { title: `الصف ${labels[i]}`, value: String(n) }
})

export const teacherStats = [
  {
    title: 'الدروس المرفوعة',
    value: '24',
    icon: 'mdi-book-open-page-variant',
    color: 'primary',
    trend: '+3 هذا الأسبوع',
  },
  {
    title: 'الطلاب النشطون',
    value: '156',
    icon: 'mdi-account-group',
    color: 'secondary',
    trend: '+12 هذا الشهر',
  },
  {
    title: 'جلسات الذكاء الاصطناعي',
    value: '1,284',
    icon: 'mdi-robot-happy',
    color: 'accent',
    trend: '+89 اليوم',
  },
  {
    title: 'معدل الإكمال',
    value: '87%',
    icon: 'mdi-chart-line',
    color: 'success',
    trend: '+5% عن الشهر الماضي',
  },
]

export const recentLessons = [
  {
    id: 1,
    title: 'المعادلات الخطية',
    subject: 'الرياضيات',
    grade: 'الصف التاسع',
    pages: 12,
    status: 'processed',
    uploadedAt: '2026-05-15',
    students: 42,
  },
  {
    id: 2,
    title: 'قوانين نيوتن',
    subject: 'الفيزياء',
    grade: 'الصف العاشر',
    pages: 18,
    status: 'processed',
    uploadedAt: '2026-05-14',
    students: 38,
  },
  {
    id: 3,
    title: 'الخلية والأنسجة',
    subject: 'العلوم',
    grade: 'الصف الثامن',
    pages: 15,
    status: 'processing',
    uploadedAt: '2026-05-16',
    students: 0,
  },
  {
    id: 4,
    title: 'النحو والصرف',
    subject: 'اللغة العربية',
    grade: 'الصف السابع',
    pages: 10,
    status: 'draft',
    uploadedAt: '2026-05-12',
    students: 0,
  },
]

export const chatMessages = [
  {
    id: 1,
    role: 'ai',
    text: 'أهلاً فيك! أنا معلمك الذكي اليوم. رح نشرح درس المعادلات الخطية بأسلوب الأستاذ أحمد وبلهجة سورية مبسطة. جاهز نبلّش؟',
    time: '10:02',
  },
  {
    id: 2,
    role: 'student',
    text: 'أيوه، بس ما فهمت شو يعني متغير x؟',
    time: '10:03',
  },
  {
    id: 3,
    role: 'ai',
    text: 'تمام، تخيّل إنو x هو رقم مجهول بدنا نكتشفه. مثل لما تقول: عندي 3 علب حليب ومجموع السعر 15 ليرة، كم سعر العلبة الوحدة؟ هون x هو سعر العلبة.',
    time: '10:04',
  },
  {
    id: 4,
    role: 'student',
    text: 'هلّق فهمت! يعني المعادلة 3x = 15',
    time: '10:05',
  },
  {
    id: 5,
    role: 'ai',
    text: 'بالضبط! ممتاز. لنقسم الطرفين على 3: x = 5. يعني كل علبة بخمس ليرات. فيك تجرب مثال تاني؟',
    time: '10:05',
  },
]

export const quizQuestions = [
  {
    id: 1,
    question: 'ما قيمة x في المعادلة 2x + 4 = 12؟',
    options: ['x = 2', 'x = 4', 'x = 6', 'x = 8'],
    correctIndex: 1,
  },
  {
    id: 2,
    question: 'أي من المعادلات التالية خطية؟',
    options: ['y = x² + 1', 'y = 3x - 2', 'y = 1/x', 'y = √x'],
    correctIndex: 1,
  },
  {
    id: 3,
    question: 'إذا كان سعر 5 أقلام 25 ليرة، ما سعر قلم واحد؟',
    options: ['3 ليرات', '4 ليرات', '5 ليرات', '6 ليرات'],
    correctIndex: 2,
  },
]

export function getLessonById(id) {
  const numId = Number(id)
  return recentLessons.find((l) => l.id === numId) ?? recentLessons[0]
}

export const feedbackCards = [
  {
    id: 1,
    type: 'success',
    title: 'إجابة صحيحة!',
    message: 'ممتاز! فهمت مفهوم المتغير بشكل ممتاز.',
  },
  {
    id: 2,
    type: 'hint',
    title: 'تلميح',
    message: 'جرب تقسم الطرفين على نفس الرقم للوصول للحل.',
  },
]
