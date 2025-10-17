export async function getVerbFiles() {
    const storage = useStorage('assets:server')
    const allFiles = await storage.getKeys('verbs')
    return allFiles.filter(f => f.endsWith('.json'))
}
