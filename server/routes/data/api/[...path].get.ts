import { join } from 'node:path'
import { stat, readFile } from 'node:fs/promises'

// Do NOT include this file in production (Vercel serves /public directly)
// Keep only for local dev if needed; removing for deployment.
export default defineEventHandler(async event => {
  const segments = event.context.params?.path

  if (!segments || (Array.isArray(segments) && segments.length === 0)) {
    throw createError({ statusCode: 400, statusMessage: 'Missing data path' })
  }

  const decodedSegments = Array.isArray(segments)
    ? segments.map(s => decodeURIComponent(s))
    : [decodeURIComponent(segments)]

  const relativePath = decodedSegments.join('/')
  const filePath = join(process.cwd(), 'public', 'data', 'api', relativePath)

  try {
    const info = await stat(filePath)
    if (!info.isFile()) {
      throw createError({ statusCode: 404, statusMessage: 'Data file not found' })
    }

    const buffer = await readFile(filePath)
    const extension = relativePath.split('.').pop()
    if (extension === 'json') setHeader(event, 'content-type', 'application/json; charset=utf-8')
    return buffer
  } catch (error) {
    if ((error as any)?.code === 'ENOENT') {
      throw createError({ statusCode: 404, statusMessage: 'Data file not found' })
    }
    throw createError({ statusCode: 500, statusMessage: 'Failed to load data file' })
  }
})


