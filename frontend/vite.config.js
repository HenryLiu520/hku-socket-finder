import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const backend = process.env.SF_BACKEND || 'http://127.0.0.1:8081'

export default defineConfig({
  plugins: [vue()],
  // vue-i18n's bundler build asks for these feature flags; setting them keeps the
  // production build quiet and drops the legacy (Options API) API we do not use.
  define: {
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __VUE_I18N_PROD_DEVTOOLS__: false
  },
  server: {
    port: Number(process.env.SF_WEB_PORT || 5175),
    strictPort: true,
    proxy: {
      '/api': { target: backend, changeOrigin: true }
    }
  }
})
