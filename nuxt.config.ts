export default defineNuxtConfig({
    modules: ['@nuxt/eslint', '@nuxt/ui'],
    pages: true,
    components: [{
        path: '~/components',
        pathPrefix: false,
    }],
    devtools: { enabled: true },
    app: {
        head: {
            title: 'Turoyo Verb Glossary',
            titleTemplate: '%s · Turoyo Verb Glossary',
            meta: [
                {
                    name: 'theme-color',
                    content: '#2e7d73',
                },
            ],
            link: [
                {
                    rel: 'icon',
                    type: 'image/svg+xml',
                    href: '/favicon.svg?v=2',
                },
                {
                    rel: 'mask-icon',
                    href: '/safari-pinned-tab.svg?v=2',
                    color: '#2e7d73',
                },
            ],
        },
    },
    css: ['~/assets/css/main.css'],
    runtimeConfig: {
        betterAuthSecret: process.env.BETTER_AUTH_SECRET,
        databaseUrl: process.env.DATABASE_URL,
        googleClientId: process.env.GOOGLE_CLIENT_ID,
        googleClientSecret: process.env.GOOGLE_CLIENT_SECRET,
        public: {
            siteUrl: process.env.NUXT_PUBLIC_SITE_URL
                || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3456'),
        },
    },
    dir: { public: 'public' },
    srcDir: 'app',
    routeRules: {
        '/_nuxt/**': { headers: { 'cache-control': 'public, max-age=31536000, immutable' } },
        '/favicon.ico': { headers: { 'cache-control': 'public, max-age=31536000, immutable' } },
        '/favicon.svg': { headers: { 'cache-control': 'public, max-age=31536000, immutable' } },
        '/safari-pinned-tab.svg': { headers: { 'cache-control': 'public, max-age=31536000, immutable' } },
    },
    devServer: {
        host: 'localhost',
        port: 3456,
    },
    compatibilityDate: '2025-07-15',
    nitro: {
        preset: process.env.VERCEL ? 'vercel' : undefined,
        publicAssets: [{
            dir: 'public',
            baseURL: '/',
        }],
        ignore: process.env.VERCEL ? ['server/routes/data/api/**'] : [],
        scanDirs: ['server'],
    },
    vite: {
        server: { strictPort: true },
        build: { sourcemap: false },
    },
    eslint: {
        config: {
            stylistic: {
                indent: 4,
                quotes: 'single',
                semi: false,
                commaDangle: 'never',
            },
        },
    },

    icon: {
        serverBundle: { collections: ['heroicons', 'lucide'] },
        clientBundle: {
            scan: true,
            sizeLimitKb: 512,
            icons: [
                'lucide:check',
                'lucide:loader-circle',
                'lucide:x',
            ],
        },
        fallbackToApi: false,
        localApiEndpoint: false,
        mode: 'svg',
        provider: 'iconify',
    },
})
