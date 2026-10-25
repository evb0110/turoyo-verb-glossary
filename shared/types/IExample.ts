import type { IRef } from '#shared/types/IRef'

export interface IExample {
    id: string
    sense: string | null
    turoyo: string
    translation: string | null
    refs: IRef[]
    note: string | null
    raw: string
}
