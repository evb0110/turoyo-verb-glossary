import type { IEntry } from '#shared/types/IEntry'
import type { IEntryIndex } from '#shared/types/IEntryIndex'
import type { IProposal } from '#shared/types/IProposal'
import type { ISearchDocument } from '#shared/types/ISearchDocument'
import type { IText } from '#shared/types/IText'
import type { ITextIndex } from '#shared/types/ITextIndex'

export interface IGlossaryCatalog {
    entries: IEntry[]
    index: IEntryIndex[]
    texts: IText[]
    textIndex: ITextIndex[]
    proposals: IProposal[]
    search: ISearchDocument[]
}
