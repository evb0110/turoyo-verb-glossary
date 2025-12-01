import type { IEtymon } from '~/types/IEtymon'

export interface IEtymology {
    etymons: IEtymon[]
    relationship?: 'also' | 'or' | 'and'
    uncertain?: boolean
}
