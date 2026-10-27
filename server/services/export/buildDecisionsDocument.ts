import { exportFront } from '~~/server/services/export/exportFront'
import type { IDocRun } from '~~/server/types/export/IDocRun'
import type { IExportContext } from '~~/server/types/export/IExportContext'
import type { IExportDocument } from '~~/server/types/export/IExportDocument'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalDecisionExport } from '#shared/types/IProposalDecisionExport'
import type { IProposalEdit } from '#shared/types/IProposalEdit'
import { formatReviewDate } from '#shared/utils/formatReviewDate'
import { plainProposalText } from '#shared/utils/plainProposalText'
import { plainValue } from '#shared/utils/plainValue'
import { proposalContext } from '#shared/utils/proposalContext'
import { proposalKindLabels } from '#shared/utils/proposalKindLabels'
import { proposalTarget } from '#shared/utils/proposalTarget'
import { rootLetter } from '#shared/utils/rootLetter'
import { verdictLabel } from '#shared/utils/verdictLabel'

interface IDecisionsDocumentInput {
    rows: IProposalDecisionExport[]
    order: string[] // entry ids in glossary order, then verbs only proposed so far
    entries: ReadonlyMap<string, IEntry>
    proposals: ReadonlyMap<string, IProposal>
    context: IExportContext
}

function wording(label: string, value: IProposalEdit, turoyo: boolean): IDocRun[] {
    return [
        { text: `${label}: ` },
        ...(value.headword
            ? [{
                    text: `${value.headword} `,
                    italic: true,
                    bold: true,
                }]
            : []),
        {
            text: plainValue(value.text),
            italic: turoyo,
        },
        ...(value.translation
            ? [{ text: ` ‘${plainValue(value.translation)}’` }]
            : value.translation === '' ? [{ text: ' (no translation)' }] : []),
    ]
}

// The stem a suggestion belongs to, by its target, as the entry page places it.
function stemOf(entry: IEntry | undefined, proposal: IProposal | undefined, row: IProposalDecisionExport) {
    const target = proposal?.target || row.citationTarget.target
    const stem = entry?.stems.find(item => target.stemId === item.id
        || target.boxId?.startsWith(`${item.id}.`) || target.exampleId?.startsWith(`${item.id}.`))
    if (stem) return {
        key: stem.id,
        label: `Stem ${stem.stem}`,
        position: entry!.stems.indexOf(stem),
    }
    if (target.stemId) return {
        key: target.stemId,
        label: `Stem ${String(proposal?.data.stem || target.stemId.split('.').at(-1))} (suggested)`,
        position: 1000,
    }
    return {
        key: '',
        label: 'The entry as a whole',
        position: 2000,
    }
}

// Every current team decision, letter > root > stem, for the editors who apply them to the Word volumes.
export function buildDecisionsDocument(input: IDecisionsDocumentInput): IExportDocument {
    const position = new Map(input.order.map((id, n) => [id, n]))
    // Within a stem, decisions follow the order of the suggestions in the data.
    const proposalPosition = new Map([...input.proposals.keys()].map((id, n) => [id, n]))
    const byEntry = new Map<string, IProposalDecisionExport[]>()
    for (const row of input.rows) byEntry.set(row.entryId, [...(byEntry.get(row.entryId) || []), row])
    const entryIds = [...byEntry.keys()].toSorted((a, b) =>
        (position.get(a) ?? Infinity) - (position.get(b) ?? Infinity) || a.localeCompare(b))
    const letters = new Map<string, string[]>()
    for (const id of entryIds) {
        const letter = rootLetter(byEntry.get(id)![0]!.verb)
        letters.set(letter, [...(letters.get(letter) || []), id])
    }
    const blocks: TDocBlock[] = []
    const counts = {
        accept: 0,
        reject: 0,
        discuss: 0,
    }
    for (const [letter, ids] of letters) {
        blocks.push({
            type: 'heading',
            level: 1,
            id: `letter:${letter}`,
            runs: [{ text: letter }],
        })
        for (const id of ids) {
            const entry = input.entries.get(id)
            const rows = byEntry.get(id)!
            blocks.push({
                type: 'heading',
                level: 2,
                id: `entry:${id}`,
                runs: [{ text: rows[0]!.verb }],
            })
            if (!entry) blocks.push({
                type: 'paragraph',
                style: 'note',
                runs: [{ text: 'Suggested new verb, not in the glossary yet.' }],
            })
            const stems = new Map<string, {
                label: string
                position: number
                rows: IProposalDecisionExport[]
            }>()
            for (const row of rows) {
                const stem = stemOf(entry, input.proposals.get(row.proposalId), row)
                const group = stems.get(stem.key) || {
                    label: stem.label,
                    position: stem.position,
                    rows: [],
                }
                group.rows.push(row)
                stems.set(stem.key, group)
            }
            for (const [key, group] of [...stems].toSorted((a, b) => a[1].position - b[1].position)) {
                blocks.push({
                    type: 'heading',
                    level: 3,
                    id: `stem:${id}:${key}`,
                    runs: [{ text: group.label }],
                })
                const ordered = group.rows.toSorted((a, b) => (proposalPosition.get(a.proposalId) ?? Infinity)
                    - (proposalPosition.get(b.proposalId) ?? Infinity))
                for (const row of ordered) {
                    counts[row.verdict]++
                    const proposal = input.proposals.get(row.proposalId)
                    const question = row.kind === 'note' || row.kind === 'question'
                    const turoyo = ['add-example', 'new-form', 'new-idiom'].includes(row.kind)
                        || ['turoyo', 'forms'].includes(proposal?.target.field || '')
                    const target = proposal ? proposalTarget(proposalContext(entry || null, proposal), proposal) : ''
                    const kind = proposal ? proposalKindLabels[proposal.kind] : 'Suggestion no longer in the data'
                    blocks.push({
                        type: 'heading',
                        level: 4,
                        id: `decision:${row.proposalId}`,
                        runs: [{ text: [verdictLabel(row.verdict, question, !!row.editedText), kind, target].filter(Boolean).join(' · ') }],
                    })
                    const paragraphs: IDocRun[][] = []
                    // A summary that only repeats the suggested wording is left out.
                    const summary = proposal ? plainProposalText(proposal.summary) : ''
                    const machine = row.machineText && !question ? plainValue(row.machineText.text) : ''
                    if (summary && !(machine && summary.includes(machine))) paragraphs.push([{ text: summary }])
                    if (plainValue(proposal?.before)) paragraphs.push([
                        { text: 'Now: ' },
                        {
                            text: plainValue(proposal?.before),
                            italic: turoyo,
                        },
                    ])
                    if (row.machineText && !question) paragraphs.push(wording('Suggested', row.machineText, turoyo))
                    if (row.editedText) paragraphs.push(wording('Accepted wording', row.editedText, turoyo))
                    if (row.comment) paragraphs.push([{ text: `Comment: ${row.comment}` }])
                    for (const runs of paragraphs) blocks.push({
                        type: 'paragraph',
                        style: 'body',
                        runs,
                    })
                    const cited = row.citationTarget.citations.map(ref => ref.cite)
                    blocks.push({
                        type: 'paragraph',
                        style: 'note',
                        runs: [{
                            text: [
                                `${row.reviewer}, ${formatReviewDate(row.date)}`,
                                cited.length ? `cited ${[...new Set(cited)].join('; ')}` : '',
                                `suggestion ${row.proposalId}`,
                            ].filter(Boolean).join(' · '),
                        }],
                    })
                }
            }
        }
    }
    const total = input.rows.length.toLocaleString('en')
    return {
        fileName: `turoyo-glossary-decisions-${input.context.generated.toISOString().slice(0, 10)}`,
        title: 'Turoyo Verb Glossary: editorial decisions',
        subject: `${total} current team decisions on machine suggestions`,
        keywords: ['Turoyo', 'glossary', 'editorial decisions'],
        front: exportFront('Editorial decisions', 'Current team decisions on the machine suggestions', [
            `${total} decisions: ${counts.accept} accepted or noted, ${counts.reject} rejected or dismissed, `
            + `${counts.discuss} left for discussion. Only the current decision on each suggestion is listed.`,
            'The suggestions come from a machine reading of the texts and proofreading of the glossary. '
            + '“Suggested” is the machine’s wording; “Accepted wording” is the reviewer’s edit, to be applied instead.',
        ], input.context),
        contentsDepth: 2,
        headerLevel: 2,
        blocks,
    }
}
