// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    modules: ['@nuxt/eslint', '@nuxt/ui'],
    pages: true,
    components: [{ path: '~/components', pathPrefix: false }],
    devtools: { enabled: true },
    app: {
        head: {
            title: 'Turoyo Verb Glossary',
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            titleTemplate: ((title?: string) => title ? `${title} · Turoyo Verb Glossary` : 'Turoyo Verb Glossary') as any,
            meta: [
                { name: 'theme-color', content: '#2e7d73' }
            ],
            link: [
                { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg?v=2' },
                { rel: 'mask-icon', href: '/safari-pinned-tab.svg?v=2', color: '#2e7d73' }
            ]
        }
    },
    css: ['~/assets/css/main.css'],
    runtimeConfig: {
        betterAuthSecret: process.env.BETTER_AUTH_SECRET,
        databaseUrl: process.env.DATABASE_URL,
        googleClientId: process.env.GOOGLE_CLIENT_ID,
        googleClientSecret: process.env.GOOGLE_CLIENT_SECRET,
        public: {
            siteUrl: process.env.NUXT_PUBLIC_SITE_URL
                || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3456')
        }
    },
    dir: { public: 'public' },
    srcDir: 'app',
    devServer: {
        host: 'localhost',
        port: 3456
    },
    compatibilityDate: '2025-07-15',
    nitro: {
        preset: process.env.VERCEL ? 'vercel' : undefined,
        publicAssets: [{ dir: 'public', baseURL: '/' }],
        ignore: process.env.VERCEL ? ['server/routes/data/api/**'] : [],
        // Explicitly tell Nitro where server files are (since srcDir is 'app')
        scanDirs: ['server']
    },
    vite: {
        server: {
            strictPort: true
        },
        build: {
            sourcemap: false
        }
    },
    eslint: {
        config: {
            stylistic: {
                indent: 4,
                quotes: 'single',
                semi: false,
                commaDangle: 'never'
            }
        }
    }
})
