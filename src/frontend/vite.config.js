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
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/chat': {
        target: 'http://localhost:10001',
        changeOrigin: true,
      },
      '/sessions': {
        target: 'http://localhost:10001',
        changeOrigin: true,
      },
      '/agents': {
        target: 'http://localhost:10001',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:10001',
        changeOrigin: true,
      },
      '/lmstudio': {
        target: 'http://127.0.0.1:1234',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/lmstudio/, '')
      },
    },
  },
})