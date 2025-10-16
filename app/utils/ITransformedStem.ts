import type { IStem } from '~/types/IStem'
import type { IConjugationGroup } from '~/utils/IConjugationGroup'
import type { IGlossToken } from '~/utils/IGlossToken'

export interface ITransformedStem extends IStem {
    exampleCount: number
    conjugationGroups: IConjugationGroup[]
    glossTokens: IGlossToken[]
}
