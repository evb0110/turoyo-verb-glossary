import { getVerbFiles } from '~~/server/repositories/getVerbFiles'
import { getVerbRoots } from '~~/server/repositories/getVerbRoots'
import { searchFullText } from '~~/server/services/searchFullText'
import { searchRoots } from '~~/server/services/searchRoots'

export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const {
        query, useRegex, caseSensitive, searchType,
    } = body

    if (!query) {
        throw createError({
            statusCode: 400,
            message: 'Invalid request: query required',
        })
    }

    console.log(`[Verb Search] Query: "${query}", Mode: ${searchType}, Regex: ${useRegex}, Case: ${caseSensitive}`)

    if (searchType === 'roots') {
        console.log('[Verb Search] Roots-only mode: searching filenames...')
        const allRoots = await getVerbRoots()

        console.log(`[Verb Search] Total roots: ${allRoots.length}`)
        if (allRoots.length > 0) {
            console.log(`[Verb Search] First 3 roots:`, allRoots.slice(0, 3))
        }

        return searchRoots(allRoots, query, {
            useRegex,
            caseSensitive,
        })
    }

    console.log('[Verb Search] Everything mode: scanning all verb content...')
    const verbFiles = await getVerbFiles()

    console.log(`[Verb Search] Total verb files: ${verbFiles.length}`)
    if (verbFiles.length > 0) {
        console.log(`[Verb Search] First 3 file paths:`, verbFiles.slice(0, 3))
    }

    return searchFullText(verbFiles, query, {
        useRegex,
        caseSensitive,
        searchType,
    })
})
