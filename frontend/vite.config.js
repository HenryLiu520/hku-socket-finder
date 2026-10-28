import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const backend = process.env.SF_BACKEND || 'http://127.0.0.1:8081'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: Number(process.env.SF_WEB_PORT || 5175),
    strictPort: true,
    proxy: {
      '/api': { target: backend, changeOrigin: true }
    }
  }
})
