import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/chat': {
        target: 'http://localhost:10000',
        changeOrigin: true,
      },
      '/sessions': {
        target: 'http://localhost:10000',
        changeOrigin: true,
      },
      '/agents': {
        target: 'http://localhost:10000',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:10000',
        changeOrigin: true,
      },
    },
  },
})