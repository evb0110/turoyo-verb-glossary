// Not needed per Nuxt 4 server routing model for static files.
export default defineEventHandler(() => {
  throw createError({ statusCode: 404, statusMessage: 'Route removed' })
})
