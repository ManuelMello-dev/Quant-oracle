/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'oracle-dark': '#0a0e27',
        'oracle-darker': '#060918',
        'oracle-blue': '#3b82f6',
        'oracle-green': '#10b981',
        'oracle-red': '#ef4444',
        'oracle-yellow': '#f59e0b',
      },
    },
  },
  plugins: [],
}
