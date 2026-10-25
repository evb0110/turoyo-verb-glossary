import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'
import type { IText } from '#shared/types/IText'

export async function getText(id: string): Promise<IText | null> {
    return (await getGlossaryCatalog()).texts.find(text => text.id === id) || null
}
