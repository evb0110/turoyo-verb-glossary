import { join } from 'node:path'
import { stat, readFile } from 'node:fs/promises'

export default defineEventHandler(async event => {
  const segments = event.context.params?.path

  if (!segments || segments.length === 0) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing data path'
    })
  }

  const relativePath = Array.isArray(segments) ? segments.join('/') : segments
  const filePath = join(process.cwd(), 'data', 'api', relativePath)

  try {
    const info = await stat(filePath)
    if (!info.isFile()) {
      throw createError({ statusCode: 404, statusMessage: 'Not found' })
    }

    const buffer = await readFile(filePath)
    const extension = relativePath.split('.').pop()

    if (extension === 'json') {
      setHeader(event, 'content-type', 'application/json')
    }

    return buffer
  } catch (error) {
    if (error instanceof Error && 'code' in error && (error as NodeJS.ErrnoException).code === 'ENOENT') {
      throw createError({ statusCode: 404, statusMessage: 'Data file not found' })
    }

    throw createError({ statusCode: 500, statusMessage: 'Failed to load data file' })
  }
})

