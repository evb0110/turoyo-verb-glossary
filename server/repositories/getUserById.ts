import { db } from '~~/server/db'
import { user } from '~~/server/db/schema'
import { eq } from 'drizzle-orm'

export async function getUserById(userId: string) {
    const result = await db.select().from(user).where(eq(user.id, userId)).limit(1)
    return result[0] || null
}
