import { homedir } from 'node:os'
import { join } from 'node:path'
import mkcert from 'vite-plugin-mkcert'

const mkcertDir = join(homedir(), '.vite-plugin-mkcert')

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
        betterAuthSecret: '',
        databaseUrl: '',
        googleClientId: '',
        googleClientSecret: '',
        public: { siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://turoyo-verb-glossary.lvh.me:3456' },
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
        host: '0.0.0.0',
        port: 3456,
        https: {
            key: join(mkcertDir, 'dev.pem'),
            cert: join(mkcertDir, 'cert.pem'),
        },
    },
    compatibilityDate: '2025-07-15',
    nitro: {
        preset: process.env.VERCEL ? 'vercel' : process.env.CLOUDFLARE ? 'cloudflare-pages' : undefined,
        publicAssets: [{
            dir: 'public',
            baseURL: '/',
        }],
        ignore: process.env.VERCEL ? ['server/routes/data/api/**'] : [],
        scanDirs: ['server'],
    },
    vite: {
        plugins: [
            mkcert({ hosts: ['*.lvh.me', 'lvh.me', 'localhost'] }),
        ],
        server: { strictPort: true },
        build: { sourcemap: false },
    },
    typescript: { typeCheck: true },

    hooks: {
        listen() {
            const devUrl = 'https://turoyo-verb-glossary.lvh.me:3456'
            console.log(`\n  ➜ Dev URL (HTTPS): \x1b[36m${devUrl}\x1b[0m`)
        },
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
