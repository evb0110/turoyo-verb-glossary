import type { IDocParagraph } from '~~/server/types/export/IDocParagraph'
import type { IDocRun } from '~~/server/types/export/IDocRun'
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalEdit } from '#shared/types/IProposalEdit'
import type { IProposalReview } from '#shared/types/IProposalReview'
import { formatReviewDate } from '#shared/utils/formatReviewDate'
import { plainProposalText } from '#shared/utils/plainProposalText'
import { plainValue } from '#shared/utils/plainValue'
import { proposalContext } from '#shared/utils/proposalContext'
import { proposalKindLabels } from '#shared/utils/proposalKindLabels'
import { proposalTarget } from '#shared/utils/proposalTarget'
import { verdictLabel } from '#shared/utils/verdictLabel'

const TUROYO_KINDS = ['add-example', 'new-form', 'new-idiom']

function wordingRuns(label: string, wording: IProposalEdit, turoyo: boolean): IDocRun[] {
    return [
        { text: `${label}: ` },
        ...(wording.headword
            ? [{
                    text: `${wording.headword} `,
                    italic: true,
                    bold: true,
                }]
            : []),
        {
            text: wording.text,
            italic: turoyo,
        },
        ...(wording.translation ? [{ text: ` ‘${wording.translation}’` }] : []),
    ]
}

// A machine suggestion as it appears beside the glossary text: kind, place and the team's decision,
// then the suggested wording, any accepted wording, the comment and the cited passages.
export function proposalBlocks(
    proposal: IProposal,
    entry: IEntry | null,
    review: IProposalReview | null
): IDocParagraph[] {
    const question = proposal.kind === 'note' || proposal.kind === 'question'
    const target = proposalTarget(proposalContext(entry, proposal), proposal)
    const status = review
        ? `${verdictLabel(review.verdict, question, !!review.edited)} by ${review.userName}, ${formatReviewDate(review.createdAt)}`
        : 'Undecided'
    const field = proposal.target.field || ''
    const turoyoField = ['turoyo', 'forms'].includes(field)
    const turoyoAddition = TUROYO_KINDS.includes(proposal.kind) || (!proposal.after && !!proposal.data.turoyo)
    const rows: IDocRun[][] = [[
        {
            text: 'Machine suggestion',
            bold: true,
        },
        { text: ` · ${proposalKindLabels[proposal.kind]}${target ? ` · ${target}` : ''} · ${status}` },
    ]]
    const summary = plainProposalText(proposal.summary)
    const before = proposal.before === null ? null : plainValue(proposal.before)
    const after = proposal.after === null ? null : plainValue(proposal.after)
    const data = (key: string) => plainValue(proposal.data[key])
    if (!question && before !== null && after !== null) {
        rows.push([{ text: summary }])
        rows.push([
            { text: 'Now: ' },
            {
                text: before,
                italic: turoyoField,
            },
        ])
        rows.push(after
            ? [
                    { text: 'Suggested: ' },
                    {
                        text: after,
                        italic: turoyoField,
                    },
                    ...(data('translation') ? [{ text: ` ‘${data('translation')}’` }] : []),
                ]
            : [{ text: 'Suggested: remove this text.' }])
    }
    else if (question || ['move-example', 'duplicate-entry'].includes(proposal.kind)) rows.push([{ text: summary }])
    else {
        const wording: IProposalEdit | null = after
            ? {
                    text: after,
                    translation: data('translation'),
                    headword: data('headword') || undefined,
                }
            : data('turoyo') || data('forms')
                ? {
                        text: data('turoyo') || data('forms'),
                        translation: data('gloss') || data('translation'),
                    }
                : data('gloss') ? { text: data('gloss') } : null
        // A summary that only repeats the proposed wording is left out.
        if (!wording || !summary.includes(wording.text)) rows.push([{ text: summary }])
        if (wording) rows.push(wordingRuns('Suggested', wording, turoyoAddition))
    }
    const gate = proposal.data.gate as { ok?: boolean
        reason?: string
        machineTranslation?: boolean } | undefined
    if (gate?.machineTranslation)
        rows.push([{ text: 'The translation of the cited passage is a machine translation made for this project.' }])
    if (gate?.ok === false)
        rows.push([{ text: `The cited text could not be verified. ${gate.reason || 'Check the printed source.'}` }])
    if (review?.edited)
        rows.push(wordingRuns(`Accepted wording (${review.userName})`, review.edited, turoyoAddition || turoyoField))
    if (review?.comment) rows.push([{ text: `Comment (${review.userName}): ${review.comment}` }])
    const cited = proposal.evidence.map(ref => ref.cite)
    if (!cited.length && data('ref')) cited.push(data('ref'))
    if (cited.length) rows.push([{ text: `Cited: ${[...new Set(cited)].join('; ')}` }])
    return rows.filter(runs => runs.some(run => run.text.trim())).map((runs, n) => ({
        type: 'paragraph',
        style: n ? 'suggestion' : 'suggestionHead',
        runs,
    }))
}
