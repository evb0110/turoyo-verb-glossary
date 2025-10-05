export default defineEventHandler(async event => {
  // Return pre-computed statistics (generated at build time)
  const stats = getStatistics()

  setHeader(event, 'content-type', 'application/json; charset=utf-8')
  return stats
})
