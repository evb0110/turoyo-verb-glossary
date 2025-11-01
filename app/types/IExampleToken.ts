export type TExampleTokenKind = 'turoyo' | 'translation' | 'ref' | 'text' | 'punct' | 'note'

export interface IExampleToken {
    kind: TExampleTokenKind
    value: string
}
