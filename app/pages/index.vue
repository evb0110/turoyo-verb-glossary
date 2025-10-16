<script lang="ts" setup>
import type { IVerbMetadataWithPreview } from '~/types/IVerbMetadataWithPreview'
import { applyFilters } from '~/utils/applyFilters'
import { generateEtymologyOptions } from '~/utils/generateEtymologyOptions'
import { generateLetterOptions } from '~/utils/generateLetterOptions'
import { generateStemOptions } from '~/utils/generateStemOptions'

const showRegexHelp = ref(false)

const q = useQuery('q', '')
const searchEverything = useQuery('type', false, 'all', 'roots')
const useRegex = useQuery('regex', true)
const caseSensitive = useQuery('case', false)
const filterLetter = useQuery('letter')
const filterEtymology = useQuery('etymology')
const filterStem = useQuery('stem')

const searchPlaceholder = computed(() => {
    if (useRegex.value) {
        return 'Regex search (use \\c for consonants, \\v for vowels)…'
    }
    return searchEverything.value
        ? 'Search for roots, forms, translations, or etymology keywords…'
        : 'Search for verb roots…'
})

const filters = computed(() => ({
    letter: filterLetter.value,
    etymology: filterEtymology.value,
    stem: filterStem.value,
}))

const searchQuery = ref(q.value)

const searchKey = computed(() => {
    return [
        'search',
        searchQuery.value,
        searchEverything.value,
        useRegex.value,
        caseSensitive.value,
    ].join('-')
})
const {
    data: searchResults,
    pending,
} = await useAsyncData(
    searchKey,
    async () => {
        const query = (searchQuery.value || '').trim()
        if (query.length < 2) {
            return null
        }

        const endpoint = searchEverything.value ? '/api/search/fulltext' : '/api/search/roots'
        return await $fetch<{
            total: number
            roots: string[]
            verbMetadata?: Record<string, IVerbMetadataWithPreview>
        }>(endpoint, {
            method: 'POST',
            body: {
                query,
                useRegex: useRegex.value,
                caseSensitive: caseSensitive.value,
            },
        })
    }
)

const verbMetadata = computed(() =>
    new Map(Object.entries(searchResults.value?.verbMetadata || {}))
)

function performSearch() {
    searchQuery.value = q.value
}

function clearSearch() {
    q.value = ''
    searchQuery.value = ''
    filterLetter.value = null
    filterEtymology.value = null
    filterStem.value = null
}

watch(q, (newQ) => {
    searchQuery.value = newQ
})

const baseResults = computed(() => {
    if (!searchResults.value?.roots || searchResults.value.roots.length === 0) {
        return []
    }

    const metadata = verbMetadata.value
    return searchResults.value.roots
        .map(root => metadata.get(root))
        .filter((m): m is IVerbMetadataWithPreview => m !== undefined)
})

const letterOptions = computed(() => generateLetterOptions(baseResults.value))
const etymologyOptions = computed(() => generateEtymologyOptions(baseResults.value))
const stemOptions = computed(() => generateStemOptions(baseResults.value))

function resetFilters() {
    filterLetter.value = null
    filterEtymology.value = null
    filterStem.value = null
}

const filtered = computed(() => {
    const result = baseResults.value
    if (result.length === 0) {
        return []
    }

    return applyFilters(result, filters.value)
})
</script>

<template>
    <div class="space-y-6 py-4">
        <UCard>
            <div class="space-y-4">
                <SearchControls
                    v-model:query="q"
                    v-model:search-everything="searchEverything"
                    v-model:use-regex="useRegex"
                    v-model:case-sensitive="caseSensitive"
                    :placeholder="searchPlaceholder"
                    @search="performSearch"
                    @clear="clearSearch"
                    @show-help="showRegexHelp = true"
                />

                <div class="pt-2">
                    <VerbFilters
                        v-model:etymology="filterEtymology"
                        v-model:letter="filterLetter"
                        v-model:stem="filterStem"
                        :etymologies="etymologyOptions"
                        :letters="letterOptions"
                        :stems="stemOptions"
                        @reset="resetFilters"
                    />
                </div>

                <SearchResultsMetadata
                    :search-query="searchQuery"
                    :displayed-count="filtered.length"
                    :filters="filters"
                />

                <VerbSearchResults
                    :search-query="searchQuery"
                    :displayed="filtered"
                    :pending="pending"
                    :use-regex="useRegex"
                    :case-sensitive="caseSensitive"
                />

                <div
                    v-if="searchQuery.length >= 2 && filtered.length === 0 && !pending"
                    class="rounded-lg border border-dashed px-4 py-6 text-center text-sm text-muted"
                >
                    No matches found. Try another keyword or broaden your search.
                </div>
            </div>
        </UCard>

        <RegexHelpModal v-model:open="showRegexHelp"/>
    </div>
</template>
