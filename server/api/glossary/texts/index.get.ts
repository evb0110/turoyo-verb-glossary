import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'

export default defineEventHandler(async () => (await getGlossaryCatalog()).textIndex)
