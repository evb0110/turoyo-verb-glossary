export interface ISearchDocument {
    id: string
    type: 'root' | 'form' | 'gloss' | 'example' | 'text'
    title: string
    text: string
    normalized: string
    to: string
}
