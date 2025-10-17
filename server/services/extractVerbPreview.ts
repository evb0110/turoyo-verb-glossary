import type { IEtymology } from '#shared/types/IEtymology'
import type { IStem } from '#shared/types/IStem'
import type { IVerb } from '#shared/types/IVerb'

export interface IVerbPreview {
    root: string
    etymology: IEtymology | null
    lemma_header_tokens?: Array<{
        italic: boolean
        text: string
    }>
    stems: IStem[]
}

export function extractVerbPreview(verb: IVerb): IVerbPreview {
    return {
        root: verb.root,
        etymology: verb.etymology,
        lemma_header_tokens: verb.lemma_header_tokens,
        stems: verb.stems,
    }
}
