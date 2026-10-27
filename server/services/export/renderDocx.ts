import { AlignmentType,
    Bookmark,
    BorderStyle,
    Document,
    Footer,
    Header,
    HeadingLevel,
    InternalHyperlink,
    Packer,
    PageBreak,
    PageNumber,
    Paragraph,
    SimpleField,
    Table,
    TableCell,
    TableLayoutType,
    TableOfContents,
    TableRow,
    TabStopType,
    TextRun,
    WidthType } from 'docx'
import { createBreather } from '~~/server/services/export/createBreather'
import type { IDocHeading } from '~~/server/types/export/IDocHeading'
import type { IDocRun } from '~~/server/types/export/IDocRun'
import type { IDocVerseTable } from '~~/server/types/export/IDocVerseTable'
import type { IExportDocument } from '~~/server/types/export/IExportDocument'
import type { TDocParagraphStyle } from '~~/server/types/export/TDocParagraphStyle'

const FONT = 'Gentium Plus'
// A4 with 2 cm margins, in twentieths of a point.
const PAGE_WIDTH = 11906
const PAGE_HEIGHT = 16838
const MARGIN = 1134
const TEXT_WIDTH = PAGE_WIDTH - 2 * MARGIN
const HEADINGS = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4]
const STYLE_IDS: Record<TDocParagraphStyle, string | undefined> = {
    body: undefined,
    example: 'Example',
    label: 'FormLabel',
    note: 'Note',
    exampleNote: 'ExampleNote',
    suggestionHead: 'SuggestionHead',
    suggestion: 'Suggestion',
    title: 'Title',
    subtitle: 'Subtitle',
    meta: 'Meta',
}
const NO_BORDER = {
    style: BorderStyle.NONE,
    size: 0,
    color: 'auto',
}

function heading(size: number, before: number) {
    return {
        run: {
            font: FONT,
            size,
            bold: true,
            italics: false,
            color: '000000',
        },
        paragraph: {
            spacing: {
                before,
                after: 80,
            },
            keepNext: true,
            keepLines: true,
        },
    }
}

// Writes the document model as Word: built-in Heading 1–4 styles for the Navigation pane, a TOC field,
// a bookmark on every heading, internal hyperlinks, the current section in the header and page numbers.
export async function renderDocx(doc: IExportDocument): Promise<Buffer> {
    // Word bookmark names allow only ASCII letters, digits and underscores, up to 40 characters. Every heading
    // gets its own name; a link goes to the first heading with its id.
    const names = new Map<IDocHeading, string>()
    const bookmarks = new Map<string, string>()
    for (const block of doc.blocks)
        if (block.type === 'heading') {
            names.set(block, `h${names.size + 1}`)
            if (!bookmarks.has(block.id)) bookmarks.set(block.id, names.get(block)!)
        }

    function runs(items: IDocRun[]) {
        return items.map((item) => {
            const text = new TextRun({
                text: item.text,
                italics: item.italic,
                bold: item.bold,
                style: item.link && bookmarks.has(item.link) ? 'Hyperlink' : undefined,
            })
            const anchor = item.link && bookmarks.get(item.link)
            return anchor
                ? new InternalHyperlink({
                        anchor,
                        children: [text],
                    })
                : text
        })
    }

    function verseTable(block: IDocVerseTable) {
        const widths = [640, Math.round((TEXT_WIDTH - 640) * 0.52), 0]
        widths[2] = TEXT_WIDTH - widths[0]! - widths[1]!
        const cell = (children: Paragraph[], width: number, header = false) => new TableCell({
            children,
            width: {
                size: width,
                type: WidthType.DXA,
            },
            margins: {
                top: 30,
                bottom: 30,
                left: 60,
                right: 120,
            },
            borders: {
                top: NO_BORDER,
                left: NO_BORDER,
                right: NO_BORDER,
                bottom: header
                    ? {
                            style: BorderStyle.SINGLE,
                            size: 4,
                            color: '000000',
                        }
                    : NO_BORDER,
            },
        })
        const header = new TableRow({
            tableHeader: true,
            cantSplit: true,
            children: [
                cell([new Paragraph({ style: 'Note' })], widths[0]!, true),
                cell([new Paragraph({
                    style: 'Note',
                    text: block.columns[0],
                })], widths[1]!, true),
                cell([new Paragraph({
                    style: 'Note',
                    text: block.columns[1],
                })], widths[2]!, true),
            ],
        })
        return new Table({
            layout: TableLayoutType.FIXED,
            width: {
                size: TEXT_WIDTH,
                type: WidthType.DXA,
            },
            columnWidths: widths,
            rows: [header, ...block.rows.map(row => new TableRow({
                children: [
                    cell([new Paragraph({
                        style: 'VerseNumber',
                        text: row.n,
                    })], widths[0]!),
                    cell([new Paragraph({
                        style: 'Verse',
                        children: [new TextRun({
                            text: row.turoyo,
                            italics: true,
                        })],
                    })], widths[1]!),
                    cell([
                        new Paragraph({
                            style: 'Verse',
                            text: row.translation,
                        }),
                        ...(row.note
                            ? [new Paragraph({
                                    style: 'Note',
                                    text: row.note,
                                })]
                            : []),
                    ], widths[2]!),
                ],
            }))],
        })
    }

    const body: Array<Paragraph | Table | TableOfContents> = doc.front.map(paragraph => new Paragraph({
        style: STYLE_IDS[paragraph.style],
        children: runs(paragraph.runs),
    }))
    if (doc.contentsDepth) {
        body.push(new Paragraph({
            style: 'ContentsHeading',
            text: 'Contents',
        }))
        body.push(new TableOfContents('Contents', {
            hyperlink: true,
            headingStyleRange: `1-${doc.contentsDepth}`,
        }))
        body.push(new Paragraph({ children: [new PageBreak()] }))
    }
    // Yields every ~40 ms between blocks, and before the docx package lays out and zips the document.
    const breathe = createBreather()
    for (const block of doc.blocks) {
        await breathe()
        if (block.type === 'heading') {
            body.push(new Paragraph({
                heading: HEADINGS[block.level - 1],
                children: [new Bookmark({
                    id: names.get(block)!,
                    children: runs(block.runs),
                })],
            }))
        }
        else if (block.type === 'paragraph') {
            body.push(new Paragraph({
                style: STYLE_IDS[block.style],
                keepNext: block.style === 'label',
                children: runs(block.runs),
            }))
        }
        else body.push(verseTable(block))
    }

    const document = new Document({
        title: doc.title,
        subject: doc.subject,
        keywords: doc.keywords.join(', '),
        creator: 'Turoyo Verb Glossary',
        lastModifiedBy: 'Turoyo Verb Glossary',
        description: doc.front.map(paragraph => paragraph.runs.map(run => run.text).join('')).join('\n'),
        styles: {
            default: {
                document: {
                    run: {
                        font: FONT,
                        size: 21,
                    },
                    paragraph: {
                        spacing: {
                            after: 60,
                            line: 252,
                        },
                    },
                },
                title: {
                    run: {
                        font: FONT,
                        size: 36,
                        bold: true,
                        color: '000000',
                    },
                    paragraph: {
                        spacing: {
                            before: 0,
                            after: 120,
                        },
                    },
                },
                heading1: heading(32, 360),
                heading2: heading(27, 280),
                heading3: heading(23, 200),
                heading4: heading(21, 140),
                hyperlink: {
                    run: {
                        color: '1D5E4A',
                        underline: {},
                    },
                },
            },
            paragraphStyles: [
                {
                    id: 'Subtitle',
                    name: 'Subtitle',
                    basedOn: 'Normal',
                    next: 'Normal',
                    quickFormat: true,
                    run: { size: 26 },
                    paragraph: { spacing: { after: 120 } },
                },
                {
                    id: 'Meta',
                    name: 'Export details',
                    basedOn: 'Normal',
                    next: 'Normal',
                    run: { size: 19 },
                    paragraph: { spacing: { after: 40 } },
                },
                {
                    id: 'ContentsHeading',
                    name: 'Contents Heading',
                    basedOn: 'Normal',
                    next: 'Normal',
                    run: {
                        size: 26,
                        bold: true,
                    },
                    paragraph: {
                        spacing: {
                            before: 360,
                            after: 120,
                        },
                    },
                },
                {
                    id: 'Example',
                    name: 'Glossary Example',
                    basedOn: 'Normal',
                    next: 'Example',
                    quickFormat: true,
                    paragraph: {
                        indent: {
                            left: 567,
                            hanging: 0,
                        },
                        spacing: { after: 40 },
                    },
                },
                {
                    id: 'FormLabel',
                    name: 'Form Label',
                    basedOn: 'Normal',
                    next: 'Example',
                    quickFormat: true,
                    run: {
                        size: 19,
                        smallCaps: true,
                        color: '444444',
                    },
                    paragraph: {
                        indent: { left: 284 },
                        spacing: {
                            before: 100,
                            after: 20,
                        },
                        keepNext: true,
                    },
                },
                {
                    id: 'Note',
                    name: 'Glossary Note',
                    basedOn: 'Normal',
                    next: 'Normal',
                    run: {
                        size: 18,
                        color: '444444',
                    },
                    paragraph: { spacing: { after: 40 } },
                },
                {
                    id: 'ExampleNote',
                    name: 'Glossary Example Note',
                    basedOn: 'Note',
                    next: 'Example',
                    paragraph: { indent: { left: 567 } },
                },
                {
                    id: 'SuggestionHead',
                    name: 'Machine Suggestion Heading',
                    basedOn: 'Suggestion',
                    next: 'Suggestion',
                    quickFormat: true,
                    paragraph: {
                        spacing: {
                            before: 100,
                            after: 30,
                        },
                        keepNext: true,
                    },
                },
                {
                    id: 'Suggestion',
                    name: 'Machine Suggestion',
                    basedOn: 'Normal',
                    next: 'Suggestion',
                    quickFormat: true,
                    run: { size: 19 },
                    paragraph: {
                        indent: { left: 851 },
                        spacing: { after: 30 },
                        border: {
                            left: {
                                style: BorderStyle.SINGLE,
                                size: 6,
                                color: '888888',
                                space: 6,
                            },
                        },
                    },
                },
                {
                    id: 'RunningHead',
                    name: 'Running Head',
                    basedOn: 'Normal',
                    run: {
                        size: 18,
                        color: '444444',
                    },
                    paragraph: { spacing: { after: 0 } },
                },
                {
                    id: 'Verse',
                    name: 'Verse',
                    basedOn: 'Normal',
                    next: 'Verse',
                    paragraph: { spacing: { after: 0 } },
                },
                {
                    id: 'VerseNumber',
                    name: 'Verse Number',
                    basedOn: 'Normal',
                    next: 'Verse',
                    run: {
                        size: 18,
                        color: '555555',
                    },
                    paragraph: {
                        alignment: AlignmentType.RIGHT,
                        spacing: { after: 0 },
                    },
                },
            ],
        },
        sections: [{
            properties: {
                page: {
                    size: {
                        width: PAGE_WIDTH,
                        height: PAGE_HEIGHT,
                    },
                    margin: {
                        top: MARGIN,
                        bottom: MARGIN,
                        left: MARGIN,
                        right: MARGIN,
                        header: 567,
                        footer: 567,
                    },
                },
            },
            headers: {
                default: new Header({
                    children: [new Paragraph({
                        style: 'RunningHead',
                        tabStops: [{
                            type: TabStopType.RIGHT,
                            position: TEXT_WIDTH,
                        }],
                        children: [
                            new TextRun(`${doc.title}\t`),
                            ...(doc.headerLevel ? [new SimpleField(`STYLEREF "Heading ${doc.headerLevel}"`)] : []),
                        ],
                    })],
                }),
            },
            footers: {
                default: new Footer({
                    children: [new Paragraph({
                        style: 'RunningHead',
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun({ children: [PageNumber.CURRENT] })],
                    })],
                }),
            },
            children: body,
        }],
    })
    await new Promise(resolve => setImmediate(resolve))
    return await Packer.toBuffer(document)
}
