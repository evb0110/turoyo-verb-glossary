import { getTextIndex } from '~~/server/repositories/glossary/getTextIndex'
import { readGlossaryAsset } from '~~/server/repositories/glossary/readGlossaryAsset'
import type { IText } from '#shared/types/IText'
import { textHeading } from '#shared/utils/textHeading'

export async function getText(id: string): Promise<IText | null> {
    if (!(await getTextIndex()).some(row => row.id === id)) return null
    const text = await readGlossaryAsset<IText>(`texts/${id}.json`)
    return text
        ? {
                ...text,
                ...textHeading(text.title, text.cite),
            }
        : null
}
