import type { Verb } from '../../utils/verbs'

export default defineEventHandler(async (event) => {
    const root = getRouterParam(event, 'root')

    if (!root) {
        throw createError({
            statusCode: 400,
            message: 'Verb root is required'
        })
    }

    const decodedRoot = decodeURIComponent(root)

    const storage = useStorage('assets:server')
    const verb = await storage.getItem<Verb>(`appdata/api/verbs/${decodedRoot}.json`)

    if (!verb) {
        throw createError({
            statusCode: 404,
            message: `Verb not found: ${decodedRoot}`
        })
    }

    return verb
})
