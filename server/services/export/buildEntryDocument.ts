import { entryBlocks } from '~~/server/services/export/entryBlocks'
import { exportFront } from '~~/server/services/export/exportFront'
import type { IExportContext } from '~~/server/types/export/IExportContext'
import type { IExportDocument } from '~~/server/types/export/IExportDocument'
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalReview } from '#shared/types/IProposalReview'
import { volumeLabel } from '#shared/utils/volumeLabel'

interface IEntryDocumentInput {
    id: string
    entry: IEntry | null
    proposals: IProposal[] | null // null: the entry only
    reviews: ReadonlyMap<string, IProposalReview>
    context: IExportContext
}

export function buildEntryDocument(input: IEntryDocumentInput): IExportDocument {
    const {
        id,
        entry,
        proposals,
    } = input
    const root = entry?.root || String(proposals?.find(item => item.kind === 'new-root')?.data.root || id)
    const details = [entry ? `${volumeLabel(entry.source.volume)} of the glossary.` : 'Not in the glossary yet.']
    if (proposals) {
        const decided = proposals.filter(item => input.reviews.has(item.id)).length
        details.push(`${proposals.length} machine suggestions, ${decided} decided by the team. The suggestions come `
            + 'from a machine reading of the texts and proofreading of the glossary; they are not part of the '
            + 'glossary. Each shows the team’s current decision and any accepted wording.')
    }
    const blocks = entryBlocks({
        id,
        root,
        entry,
        proposals,
        reviews: input.reviews,
        level: 1,
    })
    const headings = blocks.filter(block => block.type === 'heading' && block.level <= 3).length
    return {
        fileName: `turoyo-glossary-${id}${proposals ? '-with-suggestions' : ''}`,
        title: `Turoyo Verb Glossary: ${root}`,
        subject: proposals ? `The entry ${root} with machine suggestions and team decisions` : `The entry ${root}`,
        keywords: ['Turoyo', 'verb', 'glossary', root],
        front: exportFront(root, proposals ? 'Glossary entry with machine suggestions' : 'Glossary entry', details,
            input.context),
        contentsDepth: headings > 6 ? 3 : 0,
        headerLevel: 2,
        blocks,
    }
}
