import { db } from '~~/server/db'
import { user } from '~~/server/db/schema'
import { eq } from 'drizzle-orm'
import type { TUserRole } from '~/composables/TUserRole'

export async function updateUserRole(userId: string, role: TUserRole) {
    const updated = await db.update(user)
        .set({ role })
        .where(eq(user.id, userId))
        .returning()

    return updated[0] || null
}
