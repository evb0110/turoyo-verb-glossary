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

  // Read directly from the public directory to ensure availability in dev
  const { join } = await import('node:path')
  const { promises: fsp } = await import('node:fs')

  const filePath = join(process.cwd(), 'public', 'appdata', 'api', relativePath)

  try {
    const ext = relativePath.split('.').pop()
    if (ext === 'json') {
      setHeader(event, 'content-type', 'application/json; charset=utf-8')
      const data = await fsp.readFile(filePath, 'utf-8')
      return data
    }
    const buffer = await fsp.readFile(filePath)
    return buffer
  } catch {
    throw createError({ statusCode: 404, statusMessage: 'Data file not found' })
  }
})


