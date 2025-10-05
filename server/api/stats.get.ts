export default defineEventHandler(async event => {
  // Prefer going through our working data endpoint to mirror prod behavior
  try {
    const stats = await $fetch('/api/data/statistics.json')
    setHeader(event, 'content-type', 'application/json; charset=utf-8')
    return stats
  } catch {}

  try {
    const index: any = await $fetch('/api/data/index.json')
    const roots: any[] = index?.roots || []
    const computed = {
      total_verbs: index?.total_verbs ?? roots.length,
      total_stems: roots.reduce((sum, r) => sum + ((r.stems || []).length), 0),
      total_examples: roots.reduce((sum, r) => sum + (r.example_count || 0), 0)
    }
    setHeader(event, 'content-type', 'application/json; charset=utf-8')
    return computed
  } catch {}

  // Final attempt: read from Nitro public assets (dev or unusual hosts)
  const storage = useStorage('assets:public')
  const raw = await storage.getItemRaw('/appdata/api/index.json')
  if (!raw) {
    throw createError({ statusCode: 404, statusMessage: 'Stats not available' })
  }
  let index: any
  try { index = JSON.parse(raw.toString()) } catch {}
  const roots: any[] = index?.roots || []
  const computed = {
    total_verbs: index?.total_verbs ?? roots.length,
    total_stems: roots.reduce((sum, r) => sum + ((r.stems || []).length), 0),
    total_examples: roots.reduce((sum, r) => sum + (r.example_count || 0), 0)
  }
  setHeader(event, 'content-type', 'application/json; charset=utf-8')
  return computed
})


