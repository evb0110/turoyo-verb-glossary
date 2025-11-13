export interface IExcerpt {
    type: 'form' | 'example' | 'translation' | 'etymology' | 'gloss' | 'idiom'
    stem?: string
    conjugationType?: string
    text: string
    html: string
    label: string
}
