export default defineNuxtRouteMiddleware(async () => {
  if (process.client) return

  try {
    await $fetch('/api/data/index.json')
  } catch (error) {
    console.warn('[validate-data] Data index unavailable, continuing without hard fail')
    return
  }
})


