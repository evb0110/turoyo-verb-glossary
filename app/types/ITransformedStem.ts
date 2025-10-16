import type { IStem } from '~/types/IStem'
import type { IConjugationGroup } from '~/types/IConjugationGroup'
import type { IGlossToken } from '~/types/IGlossToken'

export interface ITransformedStem extends IStem {
    exampleCount: number
    conjugationGroups: IConjugationGroup[]
    glossTokens: IGlossToken[]
    hasGlossInfo: boolean
    stemLabel: string
    formsListDisplay: string
    hasExamples: boolean
}
