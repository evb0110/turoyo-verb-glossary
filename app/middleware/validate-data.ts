export default defineNuxtRouteMiddleware(async () => {
  if (process.client) return

  try {
    await $fetch('/data/api/index.json')
  } catch (error) {
    console.error('Failed to load data index', error)
    throw createError({
      statusCode: 503,
      statusMessage: 'Verb data is temporarily unavailable'
    })
  }
})


