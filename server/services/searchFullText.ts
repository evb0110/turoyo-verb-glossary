import { generateVerbMetadata } from '~~/server/services/generateVerbMetadata'
import type { IFullTextSearchResult } from '~~/server/types/IFullTextSearchResult'
import type { ISearchOptions } from '~~/server/types/ISearchOptions'
import { matchesPattern } from '~~/server/utils/matchesPattern'
import type { IVerb } from '#shared/types/IVerb'
import type { IVerbMetadataWithPreview } from '#shared/types/IVerbMetadataWithPreview'

function mergeVerbMetadata(
    existing: IVerbMetadataWithPreview | undefined,
    newMetadata: IVerbMetadataWithPreview
): IVerbMetadataWithPreview {
    if (!existing) {
        return newMetadata
    }

    return {
        ...existing,
        excerpts: [
            ...(existing.excerpts ?? []),
            ...(newMetadata.excerpts ?? []),
        ],
    }
}

function exampleMatches(
    example: IVerb['stems'][number]['conjugations'][string][number],
    query: string,
    opts: ISearchOptions
): boolean {
    if (example.turoyo && matchesPattern(example.turoyo, query, opts)) {
        return true
    }

    if (example.translations?.some(translation => matchesPattern(translation, query, opts))) {
        return true
    }

    return example.references?.some(reference => matchesPattern(reference, query, opts))
}

function stemMatches(
    stem: IVerb['stems'][number],
    query: string,
    opts: ISearchOptions
): boolean {
    if (stem.forms?.some(f => matchesPattern(f, query, opts))) {
        return true
    }

    if (stem.label_gloss_tokens?.some(token => matchesPattern(token.text, query, opts))) {
        return true
    }

    for (const examples of Object.values(stem.conjugations)) {
        for (const example of examples) {
            if (exampleMatches(example, query, opts)) {
                return true
            }
        }
    }

    return false
}

function etymologyMatches(
    etymology: IVerb['etymology'],
    query: string,
    opts: ISearchOptions
): boolean {
    return etymology?.etymons?.some(etymon =>
        (etymon.meaning && matchesPattern(etymon.meaning, query, opts))
        || (etymon.notes && matchesPattern(etymon.notes, query, opts))
        || (etymon.raw && matchesPattern(etymon.raw, query, opts))
        || (etymon.source_root && matchesPattern(etymon.source_root, query, opts))
    ) ?? false
}

function idiomsMatch(
    idioms: IVerb['idioms'],
    query: string,
    opts: ISearchOptions
): boolean {
    return idioms?.some(idiom => matchesPattern(idiom, query, opts)) ?? false
}

function verbMatches(
    verb: IVerb,
    query: string,
    opts: ISearchOptions
): boolean {
    return (
        matchesPattern(verb.root, query, opts)
        || verb.lemma_header_tokens?.some(token => matchesPattern(token.text, query, opts)) === true
        || verb.stems.some(stem => stemMatches(stem, query, opts))
        || etymologyMatches(verb.etymology, query, opts)
        || idiomsMatch(verb.idioms, query, opts)
    )
}

function processVerbFile(
    verb: IVerb,
    query: string,
    opts: ISearchOptions
): { root: string
    metadata: IVerbMetadataWithPreview } | null {
    if (!verbMatches(verb, query, opts)) {
        return null
    }

    return {
        root: verb.root,
        metadata: generateVerbMetadata(verb, 'all', query, opts),
    }
}

export async function searchFullText(
    query: string,
    opts: ISearchOptions
): Promise<IFullTextSearchResult> {
    const storage = useStorage('assets:server')
    const verbMetadata: Record<string, IVerbMetadataWithPreview> = {}

    const allFiles = await storage.getKeys('verbs')
    const verbFiles = allFiles.filter(f => f.endsWith('.json'))

    const BATCH_SIZE = 100
    for (let i = 0; i < verbFiles.length; i += BATCH_SIZE) {
        const batch = verbFiles.slice(i, i + BATCH_SIZE)

        const batchPromises = batch.map(async (filePath: string) => {
            try {
                const verb = await storage.getItem<IVerb>(filePath)
                if (!verb) return null
                return processVerbFile(verb, query, opts)
            }
            catch (e) {
                console.warn(`[Full-text Search] Failed to load ${filePath}:`, e)
                return null
            }
        })

        const batchResults = await Promise.all(batchPromises)
        for (const result of batchResults) {
            if (result !== null) {
                verbMetadata[result.root] = mergeVerbMetadata(
                    verbMetadata[result.root],
                    result.metadata
                )
            }
        }
    }

    const matchingRoots = Object.keys(verbMetadata)
    console.log(`[Full-text Search] Found ${matchingRoots.length} matches`)

    return {
        total: matchingRoots.length,
        roots: matchingRoots,
        verbMetadata,
    }
}
