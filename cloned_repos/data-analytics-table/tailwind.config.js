/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Space Grotesk"', '"Segoe UI"', 'system-ui', 'sans-serif'],
      },
      colors: {
        canvas: '#f6f8fb',
      },
    },
  },
  plugins: [],
};
