export async function getVerbRoots() {
    const storage = useStorage('assets:server')
    const allFiles = await storage.getKeys('verbs')
    const verbFiles = allFiles.filter(f => f.endsWith('.json'))

    return verbFiles.map((f) => {
        const filename = f.split(':').pop() || f
        return filename.replace(/\.json$/, '')
    })
}
