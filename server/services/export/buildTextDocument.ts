import { exportFront } from '~~/server/services/export/exportFront'
import type { IExportContext } from '~~/server/types/export/IExportContext'
import type { IExportDocument } from '~~/server/types/export/IExportDocument'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'
import type { IText } from '#shared/types/IText'

function translationLabel(text: IText) {
    const language = text.lang === 'GERMAN' ? 'German' : text.lang === 'ENGLISH' ? 'English' : ''
    if (!language) return 'No translation available'
    return text.translationSource === 'machine'
        ? `${language} translation (machine, made for this project)`
        : `${language} translation`
}

function textBlocks(text: IText, level: 1 | 2): TDocBlock[] {
    const flags = new Map<number, string[]>()
    for (const flag of text.alignment || []) flags.set(flag.v, [...(flags.get(flag.v) || []), flag.note])
    const details = [
        text.collection,
        `text ${text.cite}`,
        text.speakerPlace ? `speaker/place ${text.speakerPlace}` : '',
        `${text.verses.length} verses`,
        translationLabel(text),
    ].filter(Boolean).join(' · ')
    return [
        {
            type: 'heading',
            level,
            id: `text:${text.id}`,
            runs: [{ text: `${text.cite} · ${text.title || `Text ${text.cite}`}` }],
        },
        {
            type: 'paragraph',
            style: 'note',
            runs: [{ text: details }],
        },
        ...(text.translationSource === 'machine'
            ? [{
                    type: 'paragraph' as const,
                    style: 'body' as const,
                    runs: [{
                        text: 'The translation is a machine translation made for this project, not a published one.',
                        bold: true,
                    }],
                }]
            : []),
        {
            type: 'verses',
            columns: ['Turoyo', translationLabel(text)],
            rows: text.verses.map(verse => ({
                n: String(verse.v),
                turoyo: verse.tur,
                translation: verse.tr || '',
                note: flags.get(verse.v)?.map(note => `Translation note: ${note}`).join(' ') || null,
            })),
        },
    ]
}

// One corpus text, or a whole collection (collection > text > verses), verse by verse beside the translation.
export function buildTextDocument(texts: IText[], collection: string | null, context: IExportContext): IExportDocument {
    const machine = texts.filter(text => text.translationSource === 'machine').length
    const machineNote = machine === texts.length
        ? 'All translations are machine translations made for this project, not published ones.'
        : machine ? `${machine} of the texts have a machine translation made for this project; each is marked.` : ''
    const rights = 'The texts are third-party editions, for use within the project only.'
    if (!collection) {
        const text = texts[0]!
        const blocks = textBlocks(text, 1)
        return {
            fileName: `turoyo-text-${text.id}`,
            title: `${text.cite} · ${text.title}`,
            subject: `Turoyo text ${text.cite} (${text.collection}) with its translation`,
            keywords: ['Turoyo', 'corpus', text.collection, text.cite],
            front: exportFront(text.title || `Text ${text.cite}`, `${text.collection} · text ${text.cite}`,
                [rights], context),
            contentsDepth: 0,
            headerLevel: 0,
            blocks,
        }
    }
    const verses = texts.reduce((sum, text) => sum + text.verses.length, 0)
    return {
        fileName: `turoyo-texts-${collection.replace(/[\s_]+/gu, '-')}`,
        title: `Turoyo texts: ${collection}`,
        subject: `The collection ${collection}: ${texts.length} Turoyo texts with their translations`,
        keywords: ['Turoyo', 'corpus', collection],
        front: exportFront(collection, 'Turoyo texts', [
            `${texts.length} texts, ${verses.toLocaleString('en')} verses.`,
            ...(machineNote ? [machineNote] : []),
            rights,
        ], context),
        contentsDepth: 2,
        headerLevel: 2,
        blocks: [
            {
                type: 'heading',
                level: 1,
                id: `collection:${collection}`,
                runs: [{ text: collection }],
            },
            ...texts.flatMap(text => textBlocks(text, 2)),
        ],
    }
}
