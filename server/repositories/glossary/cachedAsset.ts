// Production assets are immutable per deploy, so a load is kept for the life of the instance.
// In dev, concurrent requests share a load and a completed one is refreshed after two seconds.
export function cachedAsset<T>(load: () => Promise<T>): () => Promise<T> {
    let value: Promise<T> | null = null
    let loadedAt = 0
    return () => {
        if (value && import.meta.dev && loadedAt && Date.now() - loadedAt >= 2000) value = null
        if (!value) {
            loadedAt = 0
            value = load()
                .then((result) => {
                    loadedAt = Date.now()
                    return result
                })
                .catch((error) => {
                    value = null
                    throw error
                })
        }
        return value
    }
}
