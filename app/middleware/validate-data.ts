export default defineNuxtRouteMiddleware(async () => {
  if (process.client) return

  try {
    await $fetch('/api/data/search-index.json')
  } catch (error) {
    console.warn('[validate-data] Search index unavailable, continuing without hard fail')
    return
  }
})


