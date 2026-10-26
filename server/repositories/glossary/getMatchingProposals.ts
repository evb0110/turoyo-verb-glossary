import { getAllProposals } from '~~/server/repositories/glossary/getAllProposals'
import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import { filterProposals } from '~~/server/services/glossary/filterProposals'
import { matchProposalText } from '~~/server/services/glossary/matchProposalText'
import type { IProposalFilters } from '#shared/types/IProposalFilters'
import type { IProposalIndex } from '#shared/types/IProposalIndex'

export async function getMatchingProposals(filters: IProposalFilters): Promise<IProposalIndex[]> {
    const text = filters.text.trim()
    return filterProposals(
        await getProposalIndex(),
        await getEntryIndex(),
        filters.root,
        text ? matchProposalText(await getAllProposals(), text) : null
    )
}
