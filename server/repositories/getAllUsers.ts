import { db } from '~~/server/db'
import { user } from '~~/server/db/schema'
import { desc } from 'drizzle-orm'

export async function getAllUsers() {
    return db.select({
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
        image: user.image,
        createdAt: user.createdAt
    }).from(user).orderBy(desc(user.createdAt))
}
