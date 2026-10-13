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
          bg: '#FDFBF7',
          surface: '#FFFFFF',
          primary: '#D4A373',
          primaryHover: '#C59261',
          accent: '#FAEDCD',
          secondary: '#F1EAE0',
          border: '#E8E2D8',
          text: '#2B2623',
          muted: '#7D7571',
          green: '#3E6B48',
          greenLight: '#E2EBE4',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
