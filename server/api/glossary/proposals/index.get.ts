import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'

export default defineEventHandler(async () => (await getGlossaryCatalog()).proposals
    .toSorted((a, b) => a.priority - b.priority || a.id.localeCompare(b.id)))
