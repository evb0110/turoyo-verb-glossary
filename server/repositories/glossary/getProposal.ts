import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'
import type { IProposal } from '#shared/types/IProposal'

export async function getProposal(id: string): Promise<IProposal | null> {
    return (await getGlossaryCatalog()).proposals.find(item => item.id === id) || null
}
