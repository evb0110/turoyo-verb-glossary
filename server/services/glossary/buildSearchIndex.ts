import type { IEntry } from '#shared/types/IEntry'
import type { ISearchDocument } from '#shared/types/ISearchDocument'
import type { IText } from '#shared/types/IText'
import { entryHref } from '#shared/utils/entryHref'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

export function buildSearchIndex(entries: IEntry[], texts: IText[]): ISearchDocument[] {
    const documents: ISearchDocument[] = []
    function add(type: ISearchDocument['type'], id: string, title: string, text: string, to: string) {
        if (text) documents.push({
            id,
            type,
            title,
            text,
            normalized: normalizeTuroyo(text),
            to,
        })
    }
    for (const entry of entries) {
        const to = entryHref(entry.id)
        add('root', entry.id, entry.root, `${entry.root} ${entry.head}`, to)
        for (const stem of entry.stems) {
            const stemTo = entryHref(entry.id, stem.id)
            add('form', stem.id, `${entry.root} · Stem ${stem.stem}`, stem.forms, stemTo)
            for (const sense of [...stem.senses, ...stem.detransitiveSenses]) {
                const n = stem.detransitiveSenses.includes(sense) ? `D${sense.n}` : sense.n
                add('gloss', `${stem.id}:${n}`, `${entry.root} · ${n}`, sense.gloss, entryHref(entry.id, stem.id, n))
            }
            for (const box of stem.boxes) for (const example of box.examples) {
                const href = `${to}#${encodeURIComponent(example.id)}`
                add('form', example.id, `${entry.root} · ${box.label}`, example.turoyo, href)
                add('example', example.id, `${entry.root} · ${box.label}`, example.raw, href)
            }
        }
        for (const idiom of entry.idioms) add('example', idiom.id, `${entry.root} · Idiom`, idiom.raw, to)
    }
    for (const text of texts) {
        for (const verse of text.verses) {
            const href = `/texts/${encodeURIComponent(text.id)}?v=${verse.v}`
            add('text', `${text.id}:${verse.v}`, `${text.cite}/${verse.v} · ${text.title}`,
                `${verse.tur} ${verse.tr || ''}`, href)
        }
        for (const occurrence of text.occurrences || []) {
            if (!occurrence.entryId) continue
            add('form', `${text.id}:${occurrence.v}:${occurrence.form}`,
                `${occurrence.root} · ${occurrence.box}`, `${occurrence.form} · ${occurrence.meaning}`,
                entryHref(occurrence.entryId, `${occurrence.entryId}.${occurrence.stem}`, occurrence.sense))
        }
    }
    return documents
}
