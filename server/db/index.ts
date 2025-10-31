import { neon } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-http'
import type { H3Event } from 'h3'

let _db: ReturnType<typeof drizzle> | null = null

export function getDatabase(event?: H3Event) {
    if (_db) return _db

    const config = useRuntimeConfig(event)

    if (!config.databaseUrl) {
        console.error('[DB] NUXT_DATABASE_URL is missing!')
        throw new Error('Database URL not configured')
    }

    const sql = neon(config.databaseUrl)
    _db = drizzle(sql)
    return _db
}

export const db = new Proxy({} as ReturnType<typeof drizzle>, {
    get(target, prop) {
        const database = getDatabase()
        return database[prop as keyof typeof database]
    },
})
