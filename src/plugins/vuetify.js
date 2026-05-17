import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import { ar } from 'vuetify/locale'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default createVuetify({
  components,
  directives,
  locale: {
    locale: 'ar',
    messages: { ar },
  },
  rtl: true,
  theme: {
    defaultTheme: 'edusparkDark',
    themes: {
      edusparkDark: {
        dark: true,
        colors: {
          primary: '#7C6CF0',
          secondary: '#22D3EE',
          accent: '#A78BFA',
          success: '#34D399',
          warning: '#FBBF24',
          error: '#F87171',
          info: '#38BDF8',
          background: '#080C18',
          surface: '#0F1629',
          'on-background': '#E8ECF4',
          'on-surface': '#E8ECF4',
        },
      },
    },
  },
  defaults: {
    VBtn: { rounded: 'lg', elevation: 0 },
    VCard: { rounded: 'xl', elevation: 0, color: 'transparent' },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      bgColor: 'rgba(15, 22, 45, 0.6)',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      bgColor: 'rgba(15, 22, 45, 0.6)',
    },
    VNavigationDrawer: { color: 'transparent' },
    VAppBar: { color: 'transparent' },
  },
})
