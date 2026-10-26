import { ensureDatabaseSchema } from '~~/server/db/ensureDatabaseSchema'

// Runs before the auth middleware: sign-in reads the user and session tables, so the schema must exist first.
export default defineEventHandler(async () => {
    if (import.meta.dev && process.env.NUXT_DEV_AUTH_BYPASS === '1') return
    await ensureDatabaseSchema()
})
