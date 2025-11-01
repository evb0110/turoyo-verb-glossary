export interface IStructuredExampleItem {
    turoyo: string
    translation: string
    references: string[]
}

export interface IStructuredExample {
    number?: string
    items: IStructuredExampleItem[]
}
