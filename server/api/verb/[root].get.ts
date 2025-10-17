import { getVerbByRoot } from '~~/server/repositories/verbs/getVerbByRoot'
import { slugToRoot } from '#shared/utils/slugToRoot'

export default defineEventHandler(async (event) => {
    const slug = getRouterParam(event, 'root')

    if (!slug) {
        throw createError({
            statusCode: 400,
            message: 'Verb slug is required',
        })
    }

    const root = slugToRoot(decodeURIComponent(slug))
    const verb = await getVerbByRoot(root)

    if (!verb) {
        throw createError({
            statusCode: 404,
            message: `Verb not found: ${root}`,
        })
    }

    return verb
})
