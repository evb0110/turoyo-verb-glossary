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
    },
    build: {
      sourcemap: false
    }
  },
  components: [{ path: '~/components', pathPrefix: false }],
  nitro: {
    preset: process.env.VERCEL ? 'vercel' : undefined,
    ignore: process.env.VERCEL ? ['server/routes/data/api/**'] : []
  }
})