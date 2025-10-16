import type { IEtymology } from '~/types/IEtymology'
import type { IStem } from '~/types/IStem'

export interface IVerb {
    root: string
    etymology: IEtymology | null
    cross_reference: string | null
    stems: IStem[]
    uncertain: boolean

    lemma_header_raw?: string

    lemma_header_tokens?: { italic: boolean
        text: string }[]
}
