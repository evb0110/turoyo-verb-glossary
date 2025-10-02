// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  srcDir: 'app',
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/eslint', '@nuxt/ui'],
  css: ['~/assets/css/main.css'],
  pages: true,
  devServer: {
    host: 'localhost',
    port: 3456
  },
  vite: {
    server: {
      strictPort: true
    }
  },
  components: [{ path: '~/components', pathPrefix: false }]
})