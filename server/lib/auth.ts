import { betterAuth } from 'better-auth'
import { drizzleAdapter } from 'better-auth/adapters/drizzle'
import { getDatabase } from '~~/server/db'
import * as schema from '~~/server/db/schema'
import type { H3Event } from 'h3'

let _auth: ReturnType<typeof betterAuth> | null = null

export function getAuth(event?: H3Event) {
    if (_auth) return _auth

    const config = useRuntimeConfig(event)

    if (!config.betterAuthSecret) {
        console.error('[Auth] NUXT_BETTER_AUTH_SECRET is missing!')
    }

    _auth = betterAuth({
        baseURL: config.public.siteUrl,
        secret: config.betterAuthSecret,
        database: drizzleAdapter(getDatabase(event), {
            provider: 'pg',
            schema,
        }),
        session: {
            expiresIn: 60 * 60 * 24 * 7,
            updateAge: 60 * 60 * 24,
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

    return _auth
}

export const auth = new Proxy({} as ReturnType<typeof betterAuth>, {
    get(target, prop) {
        const authInstance = getAuth()
        return authInstance[prop as keyof typeof authInstance]
    },
})
