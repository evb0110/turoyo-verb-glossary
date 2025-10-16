import type { IVerb } from '~/types/IVerb'
import type { IVerbMetadataWithPreview } from '~/types/IVerbMetadataWithPreview'
import { extractMetadata } from '~~/server/services/extractMetadata'
import { extractVerbPreview } from '~~/server/services/extractVerbPreview'
import type { ISearchOptions } from '~~/server/types/ISearchOptions'
import { generateExcerpts } from '~~/server/utils/verbExcerpts'

export function generateVerbMetadata(
    verb: IVerb,
    searchType: 'roots' | 'all',
    query: string,
    opts: ISearchOptions
): IVerbMetadataWithPreview {
    const metadata = extractMetadata(verb)

    if (searchType === 'roots') {
        return {
            ...metadata,
            verbPreview: extractVerbPreview(verb),
        }
    }

    return {
        ...metadata,
        excerpts: generateExcerpts(verb, query, {
            useRegex: opts.useRegex ?? false,
            caseSensitive: opts.caseSensitive ?? false,
        }),
    }
}
