export default defineNitroPlugin((nitroApp) => {
    nitroApp.hooks.hook('request', (event) => {
        const cfEnv = event.context.cloudflare?.env

        if (!cfEnv) return

        const config = useRuntimeConfig(event)

        if (cfEnv.NUXT_BETTER_AUTH_SECRET && !config.betterAuthSecret) {
            config.betterAuthSecret = cfEnv.NUXT_BETTER_AUTH_SECRET
        }

        if (cfEnv.NUXT_DATABASE_URL && !config.databaseUrl) {
            config.databaseUrl = cfEnv.NUXT_DATABASE_URL
        }

        if (cfEnv.NUXT_GOOGLE_CLIENT_ID && !config.googleClientId) {
            config.googleClientId = cfEnv.NUXT_GOOGLE_CLIENT_ID
        }

        if (cfEnv.NUXT_GOOGLE_CLIENT_SECRET && !config.googleClientSecret) {
            config.googleClientSecret = cfEnv.NUXT_GOOGLE_CLIENT_SECRET
        }

        if (cfEnv.NUXT_PUBLIC_SITE_URL && !config.public.siteUrl) {
            config.public.siteUrl = cfEnv.NUXT_PUBLIC_SITE_URL
        }
    })
})
