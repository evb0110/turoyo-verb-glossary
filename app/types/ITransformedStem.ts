import type { IConjugationGroup } from '~/types/IConjugationGroup'
import type { IGlossToken } from '~/types/IGlossToken'
import type { IStem } from '#shared/types/IStem'

export interface ITransformedStem extends IStem {
    exampleCount: number
    conjugationGroups: IConjugationGroup[]
    glossTokens: IGlossToken[]
    hasGlossInfo: boolean
    stemLabel: string
    formsListDisplay: string
    hasExamples: boolean
}
