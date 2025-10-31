import { eq } from 'drizzle-orm'
import { getDatabase } from '~~/server/db'
import { user } from '~~/server/db/schema'
import type { H3Event } from 'h3'

export async function getUserById(userId: string, event?: H3Event) {
    const db = getDatabase(event)
    const result = await db.select().from(user).where(eq(user.id, userId)).limit(1)
    return result[0] || null
}
