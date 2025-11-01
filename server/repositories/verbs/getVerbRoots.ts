import { getVerbDatabase } from '~~/server/db/verbs'

export async function getVerbRoots() {
    const db = getVerbDatabase()
    return db.getRoots()
}
