import { join } from 'node:path'
import { readFile } from 'node:fs/promises'

export default defineEventHandler(async event => {
  try {
    const filePath = join(process.cwd(), 'public', 'data', 'api', 'statistics.json')
    const buffer = await readFile(filePath)
    setHeader(event, 'content-type', 'application/json')
    return buffer
  } catch (error) {
    throw createError({ statusCode: 404, statusMessage: 'Statistics not found' })
  }
})


