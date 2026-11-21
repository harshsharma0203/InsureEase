/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc7fb',
          400: '#36aaf5',
          500: '#0c8de4',
          600: '#0270c3',
          700: '#03599e',
          800: '#074c82',
          900: '#0c406d',
          950: '#072848',
        },
        navy: {
          800: '#0f172a',
          850: '#0c1424',
          900: '#090e1a',
          950: '#04070e',
        }
      },
    },
  },
  plugins: [],
}
