import type { Verb } from '../../utils/verbs'
import { slugToRoot } from '~/utils/slugify'

export default defineEventHandler(async (event) => {
    const slug = getRouterParam(event, 'root')

    if (!slug) {
        throw createError({
            statusCode: 400,
            message: 'Verb slug is required'
        })
    }

    const root = slugToRoot(slug)

    const storage = useStorage('assets:server')
    const verb = await storage.getItem<Verb>(`appdata/api/verbs/${root}.json`)

    if (!verb) {
        throw createError({
            statusCode: 404,
            message: `Verb not found: ${root}`
        })
    }

    return verb
})
