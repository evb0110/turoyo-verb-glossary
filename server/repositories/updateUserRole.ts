import { db } from '~~/server/db'
import { user } from '~~/server/db/schema'
import { eq } from 'drizzle-orm'

type UserRole = 'admin' | 'user' | 'pending' | 'blocked'

export async function updateUserRole(userId: string, role: UserRole) {
    const updated = await db.update(user)
        .set({ role })
        .where(eq(user.id, userId))
        .returning()

    return updated[0] || null
}
