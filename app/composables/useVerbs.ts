import type { Verb } from '~/types/verb'
import { rootToSlug, slugToRoot } from '~/utils/slugify'

/**
 * Composable for working with Turoyo verb data
 * Provides efficient loading and access to verb information
 */
export const useVerbs = () => {
    /**
   * Get a single verb by root (lazy loaded, ~2-5KB per verb)
   * @param rootOrSlug - The root or slugified root of the verb to fetch
   *
   * Note: Cross-references are handled by verb JSON files themselves.
   * If a verb is a cross-reference stub, it will contain a `cross_reference` field
   * that VerbHeader component displays with a link to the canonical entry.
   */
    const getVerb = async (rootOrSlug: string): Promise<Verb> => {
        // Convert slug back to root if needed
        const root = slugToRoot(rootOrSlug)
        // URL-encode the root to handle Unicode characters (ṣ, š, ǧ, etc.)
        const encodedRoot = encodeURIComponent(root)
        // Use API endpoint that serves from server assets (works in SSR and client)
        return await $fetch<Verb>(`/api/verbs/${encodedRoot}`)
    }

    return {
        // Slugs
        rootToSlug,
        slugToRoot,

        // Single verb access
        getVerb
    }
}
