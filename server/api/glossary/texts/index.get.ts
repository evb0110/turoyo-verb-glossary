import { getTextIndex } from '~~/server/repositories/glossary/getTextIndex'

export default defineEventHandler(async (event) => {
    const texts = await getTextIndex()
    setResponseHeader(event, 'cache-control', 'private, max-age=600')
    return texts
})
