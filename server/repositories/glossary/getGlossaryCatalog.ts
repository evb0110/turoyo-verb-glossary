import { readGlossaryAsset } from '~~/server/repositories/glossary/readGlossaryAsset'
import { buildSearchIndex } from '~~/server/services/glossary/buildSearchIndex'
import type { IEntry } from '#shared/types/IEntry'
import type { IEntryIndex } from '#shared/types/IEntryIndex'
import type { IGlossaryCatalog } from '#shared/types/IGlossaryCatalog'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalIndex } from '#shared/types/IProposalIndex'
import type { IText } from '#shared/types/IText'
import type { ITextIndex } from '#shared/types/ITextIndex'
import { textHeading } from '#shared/utils/textHeading'

let catalog: Promise<IGlossaryCatalog> | null = null
let loadedAt = 0
let loading = false
export function getGlossaryCatalog(): Promise<IGlossaryCatalog> {
    // Production assets are immutable per deploy. In dev, coalesce requests and
    // refresh completed snapshots after two seconds, including the search index.
    if (import.meta.dev && !loading && Date.now() - loadedAt >= 2000) catalog = null
    if (!catalog) {
        loading = true
        catalog = load()
            .then((result) => {
                loadedAt = Date.now()
                return result
            })
            .catch((error) => {
                catalog = null
                throw error
            })
            .finally(() => {
                loading = false
            })
    }
    return catalog
}
async function load(): Promise<IGlossaryCatalog> {
    const index
        = (await readGlossaryAsset<IEntryIndex[]>('index.json'))
            || (await readGlossaryAsset<IEntryIndex[]>('entries/index.json'))
            || []
    const textIndex = (await readGlossaryAsset<ITextIndex[]>('texts/index.json')) || []
    const entries = (
        await Promise.all(index.map(row => readGlossaryAsset<IEntry>(`entries/${row.id}.json`)))
    ).filter((entry): entry is IEntry => entry !== null)
    const texts = (
        await Promise.all(textIndex.map(row => readGlossaryAsset<IText>(`texts/${row.id}.json`)))
    )
        .filter((item): item is IText => item !== null)
        .map(text => ({
            ...text,
            ...textHeading(text.title, text.cite),
        }))
    // File names are entry IDs. Reading actual files also covers proposed new roots absent from the entry index.
    const proposalIndex = (await readGlossaryAsset<IProposalIndex[]>('proposals/index.json')) || []
    const storageKeys = import.meta.dev
        ? []
        : await useStorage('assets:server').getKeys('glossary:proposals')
    const ids = new Set(index.map(row => row.id))
    for (const row of proposalIndex) ids.add(row.entryId)
    for (const key of storageKeys) {
        const name = key.split(/[:/]/u).at(-1)
        if (name && name !== 'index.json' && name.endsWith('.json')) ids.add(name.slice(0, -5))
    }
    if (import.meta.dev) {
        const { readdir } = await import('node:fs/promises')
        const directory
            = process.env.NUXT_SITE_FIXTURE === '1'
                ? '.devkit/site-fixture/proposals'
                : 'server/assets/glossary/proposals'
        for (const file of await readdir(directory).catch((error: NodeJS.ErrnoException) => {
            if (error.code === 'ENOENT') return []
            throw error
        })) {
            if (file !== 'index.json' && file.endsWith('.json')) ids.add(file.slice(0, -5))
        }
    }
    const proposals = (
        await Promise.all(
            [...ids].map(id => readGlossaryAsset<IProposal[]>(`proposals/${id}.json`))
        )
    ).flatMap(items => items || [])
    const byId = new Map(texts.map(item => [item.id, item]))
    return {
        entries,
        index,
        texts,
        proposals,
        textIndex: textIndex.map(row => ({
            ...row,
            ...textHeading(row.title, row.cite),
            reading:
                row.reading
                || byId.get(row.id)?.reading
                || (byId.get(row.id)?.occurrences !== undefined ? 'read' : 'unread'),
            occurrenceCount: byId.get(row.id)?.occurrences?.length || 0,
        })),
        search: buildSearchIndex(entries, texts),
    }
}
