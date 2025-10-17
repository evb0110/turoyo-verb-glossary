import { eq } from 'drizzle-orm'
import { db } from '~~/server/db'
import { user } from '~~/server/db/schema'
import type { TUserRole } from '~~/types/TUserRole'

export async function updateUserRole(userId: string, role: TUserRole) {
    const updated = await db.update(user)
        .set({ role })
        .where(eq(user.id, userId))
        .returning()

    return updated[0] || null
}
