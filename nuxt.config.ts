import { existsSync, readdirSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import mkcert from 'vite-plugin-mkcert'

const mkcertDir = join(homedir(), '.vite-plugin-mkcert')
const rootDir = dirname(fileURLToPath(import.meta.url))
// The dated folder of the glossary Word volumes the data is parsed from (source/README.md), named in exports.
const docxSnapshots = join(rootDir, 'source/glossary-docx')
const glossarySnapshot = existsSync(docxSnapshots)
    ? readdirSync(docxSnapshots).filter(name => /^\d{4}-\d{2}-\d{2}$/u.test(name)).sort().at(-1) || ''
    : ''

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
                    rel: 'preload',
                    href: '/fonts/GentiumPlus-Regular.ttf',
                    as: 'font',
                    type: 'font/ttf',
                    crossorigin: 'anonymous',
                },
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
        glossarySnapshot,
        public: {
            siteFixture: process.env.NUXT_SITE_FIXTURE === '1' && process.env.NODE_ENV !== 'production',
            siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://turoyo-verb-glossary.lvh.me:3456',
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
        // The first request for a multi-part export writes the whole document (up to about 12 s);
        // 60 s is allowed on every Vercel plan.
        vercel: { functions: { maxDuration: 60 } },
        scanDirs: ['server'],
        // pdfkit needs @noble/hashes 1.x and better-auth 2.x. Traced side by side, the 1.x copy's import of
        // itself resolves to 2.x and the server fails to start, so pdfkit and its crypto helpers are bundled.
        externals: { inline: ['pdfkit', '@noble/hashes', '@noble/ciphers'] },
        // Gentium Plus for the PDF exports, bundled into the server from the files the site serves.
        serverAssets: [{
            baseName: 'fonts',
            dir: join(rootDir, 'public/fonts'),
        }],
    },
    vite: {
        plugins: [
            mkcert({ hosts: ['*.lvh.me', 'lvh.me', 'localhost'] }),
        ],
        server: {
            strictPort: true,
            watch: {
                ignored: [
                    '**/.output/**',
                    '**/dist/**',
                    '**/.vercel/**',
                    '**/.nuxt/**',
                    '**/build/**',
                    '**/.data/**',
                    '**/.devkit/**',
                    '**/.backup/**',
                    '**/.playwright-mcp/**',
                    '**/parser/**',
                    '**/scripts/**',
                    '**/source/**',
                    '**/data/**',
                    '**/.wrangler/**',
                ],
            },
        },
        build: { sourcemap: false },
    },

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
    fonts: {
        providers: {
            google: false,
            googleicons: false,
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
