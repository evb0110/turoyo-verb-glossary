export default defineNuxtRouteMiddleware(async () => {
    if (import.meta.client) return

    try {
        await $fetch('/api/data/search-index.json')
    }
    catch {
        console.warn('[validate-data] Search index unavailable, continuing without hard fail')
        return
    }
})
