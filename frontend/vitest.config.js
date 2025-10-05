import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/frontend/setupTests.js'],
    css: false,
    globals: true,
    include: ['tests/**/*.test.{js,jsx,ts,tsx}', 'tests/**/*.spec.{js,jsx,ts,tsx}'],
  },
})
