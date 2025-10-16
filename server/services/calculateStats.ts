import type { IVerb } from '~/types/IVerb'
import type { IVerbStats } from '~~/server/types/IVerbStats'

export function calculateStats(verbs: Array<IVerb | null>) {
    const stats: IVerbStats = {
        total_verbs: 0,
        total_stems: 0,
        total_examples: 0,
        stem_counts: {},
        etymology_sources: {},
        cross_references: 0,
        uncertain_entries: 0,
        homonyms: 0,
    }

    for (const verb of verbs) {
        if (!verb) continue

        stats.total_verbs++

        if (verb.cross_reference) {
            stats.cross_references++
        }

        if (verb.uncertain) {
            stats.uncertain_entries++
        }

        if (/\s+\d+$/.test(verb.root)) {
            stats.homonyms++
        }

        for (const stem of verb.stems) {
            stats.total_stems++

            const stemType = stem.stem
            stats.stem_counts[stemType] = (stats.stem_counts[stemType] || 0) + 1

            for (const conjugationType in stem.conjugations) {
                const examples = stem.conjugations[conjugationType]
                if (examples) {
                    stats.total_examples += examples.length
                }
            }
        }

        if (verb.etymology?.etymons) {
            for (const etymon of verb.etymology.etymons) {
                const source = etymon.source || 'Unknown'
                stats.etymology_sources[source] = (stats.etymology_sources[source] || 0) + 1
            }
        }
    }

    return stats
}
