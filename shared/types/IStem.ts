import type { IExample } from '~/types/IExample'

export interface IStem {
    stem: string
    forms: string[]
    conjugations: {
        [key: string]: IExample[]
    }

    label_raw?: string
    label_gloss_tokens?: Array<{
        italic: boolean
        text: string
    }>
}
