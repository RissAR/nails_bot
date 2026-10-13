/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        nude: {
          bg: '#F4ECE4',           // Теплий пісочний льон (5-7% темніший)
          surface: '#FAF7F2',      // М'яка слонова кістка
          primary: '#C28751',      // Карамельна бронза
          primaryHover: '#B37842', // Насичена карамель
          accent: '#EBD9C8',       // Теплий лате / активні чіпси
          secondary: '#E8DDD3',    // Нейтральний лате
          border: '#E4D8CC',       // Теплий контурний бордер
          text: '#231E1B',         // Глибокий еспресо-графіт
          muted: '#6E6157',        // Тепле мокко
          green: '#3E6B48',
          greenLight: '#E2EBE4',
        }
      },
      boxShadow: {
        'card': '0 4px 16px rgba(60, 40, 25, 0.06)',
        'card-active': '0 8px 24px rgba(60, 40, 25, 0.10)',
        'dock': '0 -4px 20px rgba(60, 40, 25, 0.08)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
