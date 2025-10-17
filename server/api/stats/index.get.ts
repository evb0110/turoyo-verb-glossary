import { getAllVerbs } from '~~/server/repositories/verbs/getAllVerbs'
import { calculateStats } from '~~/server/services/calculateStats'

export default defineEventHandler(async (event) => {
    const verbs = await getAllVerbs()
    const stats = calculateStats(verbs)

    setHeader(event, 'content-type', 'application/json; charset=utf-8')
    return stats
})
