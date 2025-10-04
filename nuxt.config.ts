// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  srcDir: 'app',
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/eslint', '@nuxt/ui'],
  css: ['~/assets/css/main.css'],
  pages: true,
  dir: { public: 'public' },
  app: {
    head: {
      title: 'Turoyo Verb Glossary',
      titleTemplate: ((title?: string) => title ? `${title} · Turoyo Verb Glossary` : 'Turoyo Verb Glossary') as any,
      meta: [
        { name: 'theme-color', content: '#0EA5E9' }
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'mask-icon', href: '/safari-pinned-tab.svg', color: '#0EA5E9' }
      ]
    }
  },
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
    publicAssets: [{ dir: 'public', baseURL: '/' }],
    ignore: process.env.VERCEL ? ['server/routes/data/api/**'] : []
  }
})