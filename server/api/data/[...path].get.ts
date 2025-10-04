export default defineEventHandler(async event => {
  const segments = event.context.params?.path

  if (!segments || (Array.isArray(segments) && segments.length === 0)) {
    throw createError({ statusCode: 400, statusMessage: 'Missing data path' })
  }

  const parts = Array.isArray(segments) ? segments : [segments]
  const relativePath = parts.map(s => decodeURIComponent(s)).join('/')

  if (relativePath.includes('..')) {
    throw createError({ statusCode: 400, statusMessage: 'Invalid path' })
  }

  // Prefer Nitro assets storage (works on serverless platforms)
  const storage = useStorage('assets:public')
  const key = `/appdata/api/${relativePath}`
  let raw = await storage.getItemRaw(key)
  if (!raw) {
    const alt = key.startsWith('/') ? key.slice(1) : key
    raw = await storage.getItemRaw(alt)
  }

  if (!raw) {
    // Dev fallback: read from filesystem
    try {
      const { join } = await import('node:path')
      const { promises: fsp } = await import('node:fs')
      const filePath = join(process.cwd(), 'public', 'appdata', 'api', relativePath)
      const ext = relativePath.split('.').pop()
      if (ext === 'json') {
        setHeader(event, 'content-type', 'application/json; charset=utf-8')
        return await fsp.readFile(filePath, 'utf-8')
      }
      return await fsp.readFile(filePath)
    } catch {
      throw createError({ statusCode: 404, statusMessage: 'Data file not found' })
    }
  }

  const ext = relativePath.split('.').pop()
  if (ext === 'json') {
    setHeader(event, 'content-type', 'application/json; charset=utf-8')
  }

  return raw
})


