/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#06090f',
          900: '#0a0f1a',
          800: '#0f172a',
          700: '#1e293b',
          600: '#334155',
        },
        accent: '#3b82f6',
        amber: {
          400: '#fbbf24',
          500: '#f59e0b',
        },
        emerald: {
          400: '#34d399',
          500: '#10b981',
        },
        coral: {
          400: '#f87171',
          500: '#ef4444',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
        sans: ['Outfit', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
}
