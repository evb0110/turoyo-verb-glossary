import { getEntries } from '~~/server/repositories/glossary/getEntries'
import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { buildGlossaryDocument } from '~~/server/services/export/buildGlossaryDocument'
import { exportContext } from '~~/server/utils/exportContext'
import { readExportFormat } from '~~/server/utils/readExportFormat'
import { sendDocument } from '~~/server/utils/sendDocument'
import { rootLetter } from '#shared/utils/rootLetter'
import { volumeLabel } from '#shared/utils/volumeLabel'

// The whole glossary, one source volume (?volume=1) or one letter (?letter=ʔ).
export default defineEventHandler(async (event) => {
    const format = readExportFormat(event)
    const query = getQuery(event)
    const letter = String(query.letter || '').normalize('NFC')
    const volume = String(query.volume || '')
    const index = await getEntryIndex()
    const rows = index.filter(row => (!letter || rootLetter(row.root) === letter)
        && (!volume || row.volume.startsWith(`${volume}.`)))
    if (!rows.length || (letter && volume))
        throw createError({
            statusCode: 404,
            message: 'No such part of the glossary.',
        })
    const scope = letter ? `Letter ${letter}` : volume ? volumeLabel(rows[0]!.volume) : 'The whole glossary'
    const fileName = letter
        ? `turoyo-glossary-letter-${letter}`
        : volume ? `turoyo-glossary-volume-${volume}` : 'turoyo-glossary'
    return sendDocument(event, format, {
        key: `glossary:${letter}:${volume}`,
        revision: '',
        build: async () => buildGlossaryDocument({
            entries: await getEntries(rows.map(row => row.id)),
            scope,
            fileName,
            totalRoots: index.length,
            context: exportContext(event),
        }),
    })
})
