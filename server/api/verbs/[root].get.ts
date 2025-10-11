import type { Verb } from '../../utils/verbs'

/**
 * Get a single verb by root
 * Serves from server assets (works in both dev and production)
 */
export default defineEventHandler(async (event) => {
    const root = getRouterParam(event, 'root')

    if (!root) {
        throw createError({
            statusCode: 400,
            message: 'Verb root is required'
        })
    }

    // Decode URL-encoded root (handles spaces and special characters)
    const decodedRoot = decodeURIComponent(root)

    // Load from server assets
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
