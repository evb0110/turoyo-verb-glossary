import type { IVerb } from '#shared/types/IVerb'

export async function getAllVerbs() {
    const storage = useStorage('assets:server')
    const allFiles = await storage.getKeys('verbs')
    const verbFiles = allFiles.filter(f => f.endsWith('.json'))

    const verbs = await Promise.all(
        verbFiles.map(async (filePath) => {
            try {
                return await storage.getItem<IVerb>(filePath)
            }
            catch (e) {
                console.warn(`Failed to load ${filePath}:`, e)
                return null
            }
        })
    )

    return verbs.filter((v): v is IVerb => v !== null)
}
