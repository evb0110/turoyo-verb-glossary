import PDFDocument from 'pdfkit'
import { createBreather } from '~~/server/services/export/createBreather'
import type { IDocHeading } from '~~/server/types/export/IDocHeading'
import type { IDocRun } from '~~/server/types/export/IDocRun'
import type { IDocVerseTable } from '~~/server/types/export/IDocVerseTable'
import type { IExportDocument } from '~~/server/types/export/IExportDocument'
import type { IExportFonts } from '~~/server/types/export/IExportFonts'
import type { TDocParagraphStyle } from '~~/server/types/export/TDocParagraphStyle'

interface IOutlineItem {
    addItem: (title: string, options?: Record<string, unknown>) => IOutlineItem
}

interface IParagraphLook {
    size: number
    indent: number
    before: number
    after: number
    color: string
    features?: PDFKit.Mixins.OpenTypeFeatures[]
}

interface IPageNote {
    carried: string
    started: string[]
    opensWithSection: boolean
}

const INK = '#1c211e'
const MUTED = '#4b524d'
const LINK = '#1d5e4a'
const MARGIN = 62
const LINE_GAP = 1.6
const HEADINGS = [
    {
        size: 17,
        before: 18,
        after: 6,
    },
    {
        size: 13.5,
        before: 14,
        after: 4,
    },
    {
        size: 11.5,
        before: 9,
        after: 3,
    },
    {
        size: 10.5,
        before: 7,
        after: 2,
    },
] as const
const LOOKS: Record<TDocParagraphStyle, IParagraphLook> = {
    body: {
        size: 10.5,
        indent: 0,
        before: 0,
        after: 3,
        color: INK,
    },
    example: {
        size: 10.5,
        indent: 28,
        before: 0,
        after: 2.5,
        color: INK,
    },
    label: {
        size: 9.5,
        indent: 14,
        before: 4,
        after: 1,
        color: MUTED,
        features: ['smcp'],
    },
    note: {
        size: 9,
        indent: 0,
        before: 0,
        after: 2.5,
        color: MUTED,
    },
    exampleNote: {
        size: 9,
        indent: 28,
        before: 0,
        after: 2.5,
        color: MUTED,
    },
    suggestionHead: {
        size: 9.5,
        indent: 48,
        before: 4,
        after: 2,
        color: INK,
    },
    suggestion: {
        size: 9.5,
        indent: 48,
        before: 0,
        after: 2,
        color: INK,
    },
    title: {
        size: 20,
        indent: 0,
        before: 0,
        after: 8,
        color: INK,
    },
    subtitle: {
        size: 13,
        indent: 0,
        before: 0,
        after: 8,
        color: INK,
    },
    meta: {
        size: 9.5,
        indent: 0,
        before: 0,
        after: 2,
        color: MUTED,
    },
}

function plain(runs: IDocRun[]) {
    return runs.map(run => run.text).join('').replace(/\s+/gu, ' ').trim()
}

// Writes the document model as a tagged PDF with Gentium Plus embedded: a nested outline mirroring the headings,
// named destinations and internal links, a linked table of contents with page numbers, a running header with
// the current section, page numbers and document metadata.
export async function renderPdf(doc: IExportDocument, fonts: IExportFonts): Promise<Buffer> {
    const pdf = new PDFDocument({
        size: 'A4',
        margins: {
            top: MARGIN,
            bottom: MARGIN,
            left: MARGIN,
            right: MARGIN,
        },
        // No standard font: everything is set in the embedded Gentium Plus.
        font: '',
        bufferPages: true,
        autoFirstPage: false,
        tagged: true,
        lang: 'en',
        displayTitle: true,
        pdfVersion: '1.7',
        info: {
            Title: doc.title,
            Subject: doc.subject,
            Author: 'Turoyo Verb Glossary',
            Creator: 'Turoyo Verb Glossary',
            Keywords: doc.keywords.join(', '),
            CreationDate: new Date(),
            ModDate: new Date(),
        },
    })
    const chunks: Buffer[] = []
    pdf.on('data', (chunk: Buffer) => chunks.push(chunk))
    const finished = new Promise<void>((resolve, reject) => {
        pdf.on('end', () => resolve())
        pdf.on('error', reject)
    })
    pdf.registerFont('regular', Buffer.from(fonts.regular))
    pdf.registerFont('italic', Buffer.from(fonts.italic))

    const width = () => pdf.page.width - pdf.page.margins.left - pdf.page.margins.right
    const left = () => pdf.page.margins.left
    const bottom = () => pdf.page.height - pdf.page.margins.bottom
    // Named destinations for the headings that the contents or a link point to; a link to a heading
    // not in the document is written as plain text. The outline points at pages directly.
    const targets = new Set<string>()
    for (const block of doc.blocks)
        if (block.type !== 'verses') for (const run of block.runs) if (run.link) targets.add(run.link)
    // Each such heading has its own destination; a link goes to the first heading with its id.
    const destinationOf = new Map<IDocHeading, string>()
    const destinations = new Map<string, string>()
    for (const block of doc.blocks) {
        if (block.type !== 'heading') continue
        const linked = targets.has(block.id) && !destinations.has(block.id)
        if (!linked && block.level > doc.contentsDepth) continue
        destinationOf.set(block, `h${destinationOf.size + 1}`)
        if (linked) destinations.set(block.id, destinationOf.get(block)!)
    }
    const pages: IPageNote[] = []
    let section = ''
    pdf.on('pageAdded', () => pages.push({
        carried: section,
        started: [],
        opensWithSection: false,
    }))

    // Yields every ~40 ms, between blocks, verse rows, contents lines and pages.
    const breathe = createBreather()

    const root = pdf.struct('Document')
    pdf.addStructure(root)

    function setFont(run: IDocRun | null, size: number, color: string) {
        pdf.font(run?.italic ? 'italic' : 'regular').fontSize(size).fillColor(run?.link && destinations.has(run.link)
            ? LINK
            : color)
    }

    // One paragraph of styled runs at the current position, wrapping onto new pages as needed.
    function writeRuns(runs: IDocRun[], look: IParagraphLook, x: number, w: number) {
        const items = runs.filter(run => run.text)
        items.forEach((run, i) => {
            setFont(run, look.size, look.color)
            const options: PDFKit.Mixins.TextOptions = {
                width: w,
                continued: i < items.length - 1,
                lineGap: LINE_GAP,
                features: look.features,
                goTo: run.link ? destinations.get(run.link) : undefined,
            }
            if (i === 0) pdf.text(run.text, x, pdf.y, options)
            else pdf.text(run.text, options)
        })
    }

    function ensureSpace(height: number) {
        if (pdf.y + height > bottom()) pdf.addPage()
    }

    function paragraph(runs: IDocRun[], style: TDocParagraphStyle) {
        if (!runs.some(run => run.text)) return
        const look = LOOKS[style]
        pdf.y += look.before
        // A form label stays with the first example below it.
        if (style === 'label') ensureSpace(look.size * 1.3 + 2 * 10.5 * 1.3)
        const startPage = pages.length - 1
        // The rule beside a suggestion runs on through the gaps between its lines.
        const startY = style === 'suggestion' ? pdf.y - LOOKS.suggestion.after : pdf.y
        root.add(pdf.struct('P', {}, () => writeRuns(runs, look, left() + look.indent, width() - look.indent)))
        if (style === 'suggestion' || style === 'suggestionHead') rule(startPage, startY, pdf.y)
        pdf.y += look.after
    }

    // The thin rule beside a machine suggestion, across the pages the paragraph runs over.
    function rule(startPage: number, startY: number, endY: number) {
        const endPage = pages.length - 1
        const x = left() + LOOKS.suggestion.indent - 7
        for (let n = startPage; n <= endPage; n++) {
            pdf.switchToPage(n)
            pdf.markContent('Artifact', { type: 'Layout' })
            pdf.save().lineWidth(0.6).strokeColor('#8a8f8b')
                .moveTo(x, n === startPage ? Math.max(startY, pdf.page.margins.top) + 1 : pdf.page.margins.top)
                .lineTo(x, n === endPage ? endY - 1 : bottom())
                .stroke().restore()
            pdf.endMarkedContent()
        }
        pdf.switchToPage(endPage)
        pdf.y = endY
    }

    function heading(block: IDocHeading, outline: IOutlineItem[]) {
        const look = HEADINGS[block.level - 1]!
        if (pdf.y > pdf.page.margins.top) pdf.y += look.before
        ensureSpace(look.size * 1.4 + 3 * 10.5 * 1.3)
        const text = plain(block.runs)
        const destination = destinationOf.get(block)
        if (destination) pdf.addNamedDestination(destination, 'XYZ', left(), pdf.y, null)
        const parent = outline[block.level - 1] || outline[0]!
        outline[block.level] = parent.addItem(text, {
            fit: false,
            top: pdf.y,
            left: pdf.page.width,
            zoom: 0,
            expanded: block.level === 1 && singleTop,
        })
        outline.length = block.level + 1
        if (block.level === doc.headerLevel) {
            const page = pages.at(-1)!
            if (!page.started.length && pdf.y <= pdf.page.margins.top + 1) page.opensWithSection = true
            page.started.push(text)
            section = text
        }
        headingPages.set(block, pages.length)
        root.add(pdf.struct(`H${block.level}`, {}, () => writeRuns(block.runs, {
            size: look.size,
            indent: 0,
            before: 0,
            after: 0,
            color: INK,
        }, left(), width())))
        pdf.y += look.after
    }

    async function verses(block: IDocVerseTable) {
        const numberWidth = 24
        const gap = 12
        const turoyoWidth = (width() - numberWidth - 2 * gap) * 0.52
        const translationWidth = width() - numberWidth - 2 * gap - turoyoWidth
        const x1 = left() + numberWidth + gap
        const x2 = x1 + turoyoWidth + gap
        const size = 10
        const table = pdf.struct('Table')
        root.add(table)
        function header() {
            const y = pdf.y
            const row = pdf.struct('TR')
            table.add(row)
            pdf.font('regular').fontSize(8.5).fillColor(MUTED)
            row.add(pdf.struct('TH', {}, () => pdf.text(block.columns[0], x1, y, { width: turoyoWidth })))
            row.add(pdf.struct('TH', {}, () => pdf.text(block.columns[1], x2, y, { width: translationWidth })))
            row.end()
            pdf.y = Math.max(pdf.y, y + 11) + 2
            pdf.markContent('Artifact', { type: 'Layout' })
            pdf.save().lineWidth(0.5).strokeColor('#8a8f8b').moveTo(left(), pdf.y).lineTo(left() + width(), pdf.y)
                .stroke().restore()
            pdf.endMarkedContent()
            pdf.y += 3
        }
        ensureSpace(40)
        header()
        for (const verse of block.rows) {
            await breathe()
            pdf.font('italic').fontSize(size)
            const turoyoHeight = pdf.heightOfString(verse.turoyo || ' ', {
                width: turoyoWidth,
                lineGap: LINE_GAP,
            })
            pdf.font('regular').fontSize(size)
            let translationHeight = pdf.heightOfString(verse.translation || ' ', {
                width: translationWidth,
                lineGap: LINE_GAP,
            })
            if (verse.note) {
                pdf.fontSize(8.5)
                translationHeight += pdf.heightOfString(verse.note, {
                    width: translationWidth,
                    lineGap: LINE_GAP,
                })
            }
            const height = Math.max(turoyoHeight, translationHeight)
            const row = pdf.struct('TR')
            table.add(row)
            if (height <= bottom() - pdf.page.margins.top - 20) {
                if (pdf.y + height > bottom()) {
                    pdf.addPage()
                    header()
                }
                const y = pdf.y
                row.add(pdf.struct('TD', {}, () => {
                    pdf.font('regular').fontSize(8.5).fillColor(MUTED)
                    pdf.text(verse.n, left(), y + 1.2, {
                        width: numberWidth,
                        align: 'right',
                        lineBreak: false,
                    })
                }))
                row.add(pdf.struct('TD', {}, () => {
                    pdf.font('italic').fontSize(size).fillColor(INK)
                    if (verse.turoyo) pdf.text(verse.turoyo, x1, y, {
                        width: turoyoWidth,
                        lineGap: LINE_GAP,
                    })
                }))
                row.add(pdf.struct('TD', {}, () => {
                    pdf.font('regular').fontSize(size).fillColor(INK)
                    pdf.y = y
                    if (verse.translation) pdf.text(verse.translation, x2, y, {
                        width: translationWidth,
                        lineGap: LINE_GAP,
                    })
                    if (verse.note) pdf.fontSize(8.5).fillColor(MUTED).text(verse.note, x2, pdf.y, {
                        width: translationWidth,
                        lineGap: LINE_GAP,
                    })
                }))
                pdf.y = y + height + 3
            }
            else {
                // A verse longer than a page: its Turoyo, then its translation, each across pages.
                row.add(pdf.struct('TD', {}, () => {
                    pdf.font('regular').fontSize(8.5).fillColor(MUTED).text(verse.n, left(), pdf.y, { width: width() })
                }))
                row.add(pdf.struct('TD', {}, () => {
                    pdf.font('italic').fontSize(size).fillColor(INK).text(verse.turoyo, x1, pdf.y, {
                        width: width() - numberWidth - gap,
                        lineGap: LINE_GAP,
                    })
                }))
                row.add(pdf.struct('TD', {}, () => {
                    pdf.font('regular').fontSize(size).fillColor(INK).text(verse.translation, x1, pdf.y + 3, {
                        width: width() - numberWidth - gap,
                        lineGap: LINE_GAP,
                    })
                }))
                pdf.y += 4
            }
            row.end()
        }
        table.end()
        pdf.y += 4
    }

    const singleTop = doc.blocks.filter(block => block.type === 'heading' && block.level === 1).length <= 3
    const headingPages = new Map<IDocHeading, number>()
    pdf.addPage()
    for (const item of doc.front) paragraph(item.runs, item.style)

    // The table of contents is laid out once the body has its page numbers; its pages are kept free for it here.
    const entries = doc.contentsDepth
        ? doc.blocks.filter((block): block is IDocHeading => block.type === 'heading' && block.level <= doc.contentsDepth)
        : []
    const contentsLine = 13
    let contents: { page: number
        y: number } | null = null
    if (entries.length) {
        pdf.y += 14
        contents = {
            page: pages.length - 1,
            y: pdf.y,
        }
        const firstPageLines = Math.floor((bottom() - pdf.y - 24) / contentsLine)
        const perPage = Math.floor((bottom() - pdf.page.margins.top) / contentsLine)
        const extraPages = Math.max(0, Math.ceil((entries.length - firstPageLines) / perPage))
        for (let n = 0; n < extraPages; n++) pdf.addPage()
    }
    const contentsStruct = entries.length ? pdf.struct('TOC') : null
    if (contentsStruct) root.add(contentsStruct)
    if (entries.length) pdf.addPage()
    else pdf.y += 12

    const outline: IOutlineItem[] = [pdf.outline as unknown as IOutlineItem]
    for (const block of doc.blocks) {
        if (block.type === 'heading') heading(block, outline)
        else if (block.type === 'paragraph') paragraph(block.runs, block.style)
        else await verses(block)
        await breathe()
    }

    if (contents && contentsStruct) {
        pdf.switchToPage(contents.page)
        pdf.font('regular').fontSize(13).fillColor(INK)
        contentsStruct.add(pdf.struct('Caption', {}, () => pdf.text('Contents', left(), contents.y, { width: width() })))
        let y = pdf.y + 6
        let page = contents.page
        for (const entry of entries) {
            await breathe()
            if (y + contentsLine > bottom()) {
                page++
                pdf.switchToPage(page)
                y = pdf.page.margins.top
            }
            const indent = (entry.level - 1) * 14
            const number = String(headingPages.get(entry) || '')
            const destination = destinationOf.get(entry)
            const lineY = y
            contentsStruct.add(pdf.struct('TOCI', {}, () => {
                pdf.font('regular').fontSize(entry.level === 1 ? 10.5 : 9.5).fillColor(INK)
                pdf.text(plain(entry.runs), left() + indent, lineY, {
                    width: width() - indent - 36,
                    height: contentsLine,
                    ellipsis: true,
                    goTo: destination,
                })
                pdf.text(number, left() + width() - 34, lineY, {
                    width: 34,
                    align: 'right',
                    lineBreak: false,
                    goTo: destination,
                })
            }))
            y += contentsLine
        }
        contentsStruct.end()
    }
    root.end()

    // Running header (title and the sections on the page) and page numbers, as layout artifacts.
    const range = pdf.bufferedPageRange()
    for (let n = range.start; n < range.start + range.count; n++) {
        await breathe()
        if (n === 0) continue
        pdf.switchToPage(n)
        const note = pages[n]!
        const first = note.opensWithSection || !note.carried ? note.started[0] : note.carried
        const last = note.started.at(-1)
        const running = first && last && first !== last ? `${first} – ${last}` : first || last || ''
        const saved = pdf.page.margins.bottom
        pdf.page.margins.bottom = 0
        pdf.markContent('Artifact', { type: 'Pagination' })
        pdf.font('regular').fontSize(8.5).fillColor(MUTED)
        pdf.text(doc.title, left(), MARGIN - 26, {
            width: width() / 2 - 6,
            height: 13,
            ellipsis: true,
        })
        if (running) pdf.text(running, left() + width() / 2 + 6, MARGIN - 26, {
            width: width() / 2 - 6,
            height: 13,
            ellipsis: true,
            align: 'right',
        })
        pdf.text(`${n + 1} / ${range.count}`, left(), pdf.page.height - MARGIN + 18, {
            width: width(),
            align: 'center',
            lineBreak: false,
        })
        pdf.endMarkedContent()
        pdf.page.margins.bottom = saved
    }
    // pdfkit's end() would compress every buffered page in one go; ending them one by one first keeps each slice
    // of work short. `_pageBuffer`/`_pageBufferStart` are pdfkit 0.20 internals (the version is pinned).
    const buffered = pdf as unknown as { _pageBuffer: PDFKit.PDFPage[]
        _pageBufferStart: number }
    while (buffered._pageBuffer.length) {
        const page = buffered._pageBuffer.shift()!
        buffered._pageBufferStart++
        pdf.endPageMarkings(page)
        page.end()
        await breathe()
    }
    pdf.end()
    await finished
    return Buffer.concat(chunks)
}
