import { getVerbDatabase } from '~~/server/db/verbs'

export async function getVerbFiles() {
    const db = getVerbDatabase()
    const roots = await db.getRoots()
    return roots.map(root => `verbs/${root}.json`)
}
