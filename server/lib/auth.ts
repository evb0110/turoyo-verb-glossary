import { betterAuth } from 'better-auth'
import { drizzleAdapter } from 'better-auth/adapters/drizzle'
import { db } from '~~/server/db'
import * as schema from '~~/server/db/schema'

const config = useRuntimeConfig()

export const auth = betterAuth({
    secret: config.betterAuthSecret,
    database: drizzleAdapter(db, {
        provider: 'pg',
        schema,
    }),
    socialProviders: {
        google: {
            clientId: config.googleClientId,
            clientSecret: config.googleClientSecret,
            prompt: 'select_account',
        },
    },
})
