import { getAllTexts } from '~~/server/repositories/glossary/getAllTexts'
import { collectResearchNotes } from '~~/server/services/glossary/collectResearchNotes'

export default defineEventHandler(async () => collectResearchNotes(await getAllTexts()))
