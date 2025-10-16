import type { IVerb } from '~/types/IVerb'
import { extractMetadata } from '~~/server/services/extractMetadata'
import type { ISearchOptions } from '~~/server/types/ISearchOptions'
import type { IVerbMetadataWithPreview } from '~~/server/types/IVerbMetadataWithPreview'
import { generateExcerpts } from '~~/server/utils/verbExcerpts'

export function setVerbMetadataWithPreview(
    verb: IVerb,
    searchType: 'roots' | 'all',
    query: string,
    opts: ISearchOptions,
    verbMetadata: Record<string, IVerbMetadataWithPreview>
): void {
    const metadata = extractMetadata(verb)

    if (searchType === 'roots') {
        verbMetadata[verb.root] = {
            ...metadata,
            verbPreview: verb,
        }
    }
    else {
        verbMetadata[verb.root] = {
            ...metadata,
            excerpts: generateExcerpts(verb, query, {
                useRegex: opts.useRegex ?? false,
                caseSensitive: opts.caseSensitive ?? false,
            }),
        }
    }
}
