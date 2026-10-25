import type { IExample } from '#shared/types/IExample'

export interface IBox {
    id: string
    label: string
    rawLabel: string
    detransitive: boolean
    examples: IExample[]
}
