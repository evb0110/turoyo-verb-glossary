import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'
import { collectResearchNotes } from '~~/server/services/glossary/collectResearchNotes'

export default defineEventHandler(async () => collectResearchNotes((await getGlossaryCatalog()).texts))
