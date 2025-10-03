export default defineNuxtRouteMiddleware(async () => {
  const dataPath = '/data/api/index.json'

  try {
    await $fetch(dataPath)
  } catch (error) {
    console.error('Failed to load data index', error)
    throw createError({
      statusCode: 503,
      statusMessage: 'Verb data is temporarily unavailable'
    })
  }
})


