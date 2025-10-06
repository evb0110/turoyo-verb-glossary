export default defineEventHandler(async (event) => {
    // Get cross-refs from static file (generated at build time)
    const crossRefs = await getCrossReferences()

    setHeader(event, 'content-type', 'application/json; charset=utf-8')
    return crossRefs
})
