import { sql } from 'drizzle-orm'
import { getDatabase } from '~~/server/db'
import { databaseSchemaSql } from '~~/server/db/databaseSchemaSql'

let ready: Promise<void> | null = null

// One transaction and a database advisory lock make concurrent cold starts safe.
// A version function created last makes an already-applied check a cheap no-op.
export function ensureDatabaseSchema(): Promise<void> {
    ready ||= getDatabase().execute(sql.raw(databaseSchemaSql)).then(() => {}).catch((error) => {
        ready = null
        throw error
    })
    return ready
}
