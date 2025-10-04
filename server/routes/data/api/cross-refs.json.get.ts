import { join } from 'node:path'
import { readFile } from 'node:fs/promises'

export default defineEventHandler(async event => {
  try {
    const filePath = join(process.cwd(), 'public', 'data', 'api', 'cross-refs.json')
    const buffer = await readFile(filePath)
    setHeader(event, 'content-type', 'application/json')
    return buffer
  } catch (error) {
    throw createError({ statusCode: 404, statusMessage: 'Cross refs not found' })
  }
})


