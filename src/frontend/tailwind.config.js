/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'primary': '#ef4444',
        'accent': '#fbbf24',
        'accent-gold': '#d4af37',
        'background-light': '#ffffff',
        'background-dark': '#111827',
      },
      fontFamily: {
        'display': ['Space Grotesk', 'Noto Sans SC', 'sans-serif'],
      },
      borderRadius: {
        'DEFAULT': '0.75rem',
        'lg': '1rem',
        'xl': '1.5rem',
        'full': '9999px',
      },
    },
  },
  plugins: [],
}