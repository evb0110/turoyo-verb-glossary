import { betterAuth } from 'better-auth'
import { drizzleAdapter } from 'better-auth/adapters/drizzle'
import { db } from '~~/server/db'
import * as schema from '~~/server/db/schema'

const config = useRuntimeConfig()

export const auth = betterAuth({
    baseURL: config.public.siteUrl,
    secret: config.betterAuthSecret,
    database: drizzleAdapter(db, {
        provider: 'pg',
        schema,
    }),
    session: {
        cookieCache: {
            enabled: true,
            maxAge: 5 * 60,
        },
    },
    socialProviders: {
        google: {
            clientId: config.googleClientId,
            clientSecret: config.googleClientSecret,
            prompt: 'select_account',
        },
    },
})
