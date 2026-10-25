export interface ISearchResult {
    id: string
    type: 'root' | 'form' | 'gloss' | 'example' | 'text'
    title: string
    snippet: string
    to: string
    ranges: Array<[number, number]>
}
