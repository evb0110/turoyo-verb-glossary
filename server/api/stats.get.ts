export default defineEventHandler(async (event) => {
    const stats = getStatistics()

    setHeader(event, 'content-type', 'application/json; charset=utf-8')
    return stats
})
