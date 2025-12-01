import type { IEtymology } from '#shared/types/IEtymology'
import type { IStem } from '#shared/types/IStem'

export interface IVerb {
    root: string
    etymology: IEtymology | null
    root_gloss?: string | null
    cross_reference: string | null
    stems: IStem[]
    idioms?: string[] | null

    lemma_header_raw?: string

    lemma_header_tokens?: Array<{
        italic: boolean
        text: string
    }>
}
