/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#1B2430',
        'ink-soft': '#2A3648',
        paper: '#EEF3F1',
        'paper-raised': '#F8FAF9',
        graphite: '#22262B',
        'graphite-soft': '#5B6570',
        line: '#C9CDCB',
        teal: '#0F6E56',
        'teal-dark': '#085041',
        stamp: '#B23A2E',
      },
    },
  },
  plugins: [],
}
