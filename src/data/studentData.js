/** بيانات تجريبية لواجهة الطالب */

export const studentProfile = {
  name: 'سارة محمد',
  grade: 'الصف التاسع',
}

export const studentStats = [
  {
    title: 'دروس متاحة',
    value: '6',
    icon: 'mdi-book-open-variant',
    color: 'primary',
    trend: 'جاهزة للتعلم',
  },
  {
    title: 'دروس مكتملة',
    value: '3',
    icon: 'mdi-check-decagram',
    color: 'success',
    trend: '+1 هذا الأسبوع',
  },
  {
    title: 'جلسات AI',
    value: '18',
    icon: 'mdi-robot-happy',
    color: 'secondary',
    trend: 'نشط اليوم',
  },
  {
    title: 'معدل الاختبارات',
    value: '92%',
    icon: 'mdi-chart-arc',
    color: 'accent',
    trend: 'ممتاز',
  },
]

export const studentLessons = [
  {
    id: 1,
    title: 'المعادلات الخطية',
    teacherName: 'أستاذ أحمد',
    subject: 'الرياضيات',
    grade: 'الصف التاسع',
    description: 'فهم المتغيرات وحل المعادلات بأسلوب مبسط وبلهجة سورية',
    progress: 72,
    duration: '25 دقيقة',
    pages: 12,
    accent: 'primary',
    chatMessages: [
      {
        id: 1,
        role: 'ai',
        text: 'أهلاً فيك سارة! أنا معلمك الذكي اليوم 🧠 رح نشرح درس المعادلات الخطية بأسلوب الأستاذ أحمد وبلهجة سورية مبسطة. جاهزة نبلّش؟',
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
        text: 'تمام، تخيّلي إنو x هو رقم مجهول بدنا نكتشفه. مثل لما تقولي: عندي 3 علب حليب ومجموع السعر 15 ليرة، كم سعر العلبة؟ هون x هو سعر العلبة.',
        time: '10:04',
      },
    ],
    aiResponses: [
      'سؤال ممتاز! خليني أشرحلك بطريقة أبسط بنفس أسلوب الأستاذ أحمد...',
      'ممتاز إنك فكرتي بالموضوع. تذكّري: المعادلة مثل ميزان — الطرفين لازم يتساووا.',
      'هلّق فهمتي الفكرة! جربي تحلي المعادلة 2x + 6 = 14 خطوة بخطوة.',
      'ما تقلقي، كل الطلاب بيسألوا هالسؤال. خلينا نرسم مثال عملي معاً.',
    ],
    quizQuestions: [
      {
        id: 1,
        question: 'ما قيمة x في المعادلة 2x + 4 = 12؟',
        options: ['x = 2', 'x = 4', 'x = 6', 'x = 8'],
        correctIndex: 1,
        hint: 'اطرح 4 من الطرفين ثم اقسمي على 2',
      },
      {
        id: 2,
        question: 'أي من المعادلات التالية خطية؟',
        options: ['y = x² + 1', 'y = 3x - 2', 'y = 1/x', 'y = √x'],
        correctIndex: 1,
        hint: 'المعادلة الخطية متغيرها أساسه 1',
      },
    ],
  },
  {
    id: 2,
    title: 'قوانين نيوتن',
    teacherName: 'أستاذ أحمد',
    subject: 'الفيزياء',
    grade: 'الصف العاشر',
    description: 'القوانين الثلاثة للحركة بأمثلة من الحياة اليومية',
    progress: 35,
    duration: '30 دقيقة',
    pages: 18,
    accent: 'secondary',
    chatMessages: [
      {
        id: 1,
        role: 'ai',
        text: 'مرحباً! اليوم رح نفهم قوانين نيوتن الثلاثة. تخيّلي كرة واقفة — ليش ما بتتحرك لحالها؟',
        time: '14:10',
      },
    ],
    aiResponses: [
      'قانون نيوتن الأول بيقول: الجسم بيضل بحاله إلا إذا تأثر بقوة خارجية.',
      'مثال عملي: لما تدفعي كرسي، القوة عندك بتغيّر حركته.',
    ],
    quizQuestions: [
      {
        id: 1,
        question: 'ما نص قانون نيوتن الأول؟',
        options: [
          'القوة = كتلة × تسارع',
          'الجسم يبقى في حالته ما لم تؤثر عليه قوة',
          'لكل فعل رد فعل',
          'الطاقة لا تفنى',
        ],
        correctIndex: 1,
        hint: 'يُعرف أيضاً بقانون القصور الذاتي',
      },
    ],
  },
  {
    id: 3,
    title: 'الخلية والأنسجة',
    teacherName: 'أستاذة ليلى',
    subject: 'العلوم',
    grade: 'الصف الثامن',
    description: 'بناء الكائن الحي من الخلية إلى الأنسجة',
    progress: 0,
    duration: '22 دقيقة',
    pages: 15,
    accent: 'success',
    chatMessages: [
      {
        id: 1,
        role: 'ai',
        text: 'أهلاً! رح نستكشف عالم الخلية — أصغر وحدة حية في جسمك. مستعدة؟',
        time: '09:00',
      },
    ],
    aiResponses: [
      'الخلية هي مثل مصنع صغير — فيها نواة وسويتوبلازم وغيرها.',
      'الأنسجة مجموعة خلايا متشابهة بتشتغل مع بعض.',
    ],
    quizQuestions: [],
  },
  {
    id: 4,
    title: 'النحو والصرف',
    teacherName: 'أستاذة ليلى',
    subject: 'اللغة العربية',
    grade: 'الصف السابع',
    description: 'أساسيات الإعراب والجملة الاسمية',
    progress: 100,
    duration: '20 دقيقة',
    pages: 10,
    accent: 'accent',
    chatMessages: [],
    aiResponses: ['الجملة الاسمية تبدأ بمبتدأ وخبر.', 'الإعراب بيحدد وظيفة الكلمة بالجملة.'],
    quizQuestions: [],
  },
  {
    id: 5,
    title: 'التفاعلات الكيميائية',
    teacherName: 'أستاذ أحمد',
    subject: 'الكيمياء',
    grade: 'الصف الحادي عشر',
    description: 'أنواع التفاعلات وموازنة المعادلات',
    progress: 15,
    duration: '28 دقيقة',
    pages: 14,
    accent: 'info',
    chatMessages: [
      {
        id: 1,
        role: 'ai',
        text: 'اليوم رح نتعلم كيف المواد تتحول لمواد جديدة — مثل الصدأ على الحديد!',
        time: '11:30',
      },
    ],
    aiResponses: [
      'التفاعل الكيميائي فيه تكسر روابط وعمل روابط جديدة.',
      'موازنة المعادلة ضرورية لحفظ كتلة المواد.',
    ],
    quizQuestions: [],
  },
  {
    id: 6,
    title: 'الحضارة الإسلامية',
    teacherName: 'أستاذة ليلى',
    subject: 'التاريخ',
    grade: 'الصف الثامن',
    description: 'العصر الذهبي للحضارة الإسلامية',
    progress: 50,
    duration: '18 دقيقة',
    pages: 11,
    accent: 'warning',
    chatMessages: [
      {
        id: 1,
        role: 'ai',
        text: 'رح نسافر بالزمن لعصر ازدهار العلوم والفنون في الحضارة الإسلامية.',
        time: '13:00',
      },
    ],
    aiResponses: [
      'بغداد ودمشق كانت مراكز علمية عظيمة.',
      'العلماء المسلمون ساهموا في الرياضيات والطب.',
    ],
    quizQuestions: [],
  },
]

export function getStudentLessonById(id) {
  const numId = Number(id)
  return studentLessons.find((l) => l.id === numId) ?? studentLessons[0]
}

export function getAvailableStudentLessons() {
  return studentLessons
}
