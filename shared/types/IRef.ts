export interface IRef {
    raw: string
    kind: 'text' | 'grammar-page' | 'prs' | 'jl' | 'lb' | 'mm' | 'luf' | 'other'
    textId: string | null
    verse: number | null
}
