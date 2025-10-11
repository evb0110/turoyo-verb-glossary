<template>
    <div class="space-y-6 px-6 py-4">
        <UCard>
            <div class="space-y-4">
                <SearchControls
                    v-model:query="q"
                    v-model:search-everything="searchEverything"
                    v-model:use-regex="useRegex"
                    v-model:case-sensitive="caseSensitive"
                    :placeholder="getSearchPlaceholder()"
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
                    :displayed-count="displayed.length"
                    :filters="filters"
                />

                <VerbSearchResults
                    :search-query="searchQuery"
                    :search-type="searchType"
                    :regex-mode="regexMode"
                    :case-param="caseParam"
                    :displayed="displayed"
                    :verb-details="verbDetails"
                    :loading-details="loadingDetails"
                    :pending="pending"
                />

                <div
                    v-if="searchQuery.length >= 2 && filtered.length === 0 && !pending"
                    class="rounded-lg border border-dashed px-4 py-6 text-center text-sm text-muted"
                >
                    No matches found. Try another keyword or broaden your search.
                </div>
            </div>
        </UCard>

        <RegexHelpModal v-model:open="showRegexHelp" />
    </div>
</template>

<script lang="ts" setup>
import { useRouteQuery } from '@vueuse/router'
import type { Filters } from '~/types/types/search'
import type { Verb } from '~/types/verb'
import { loadVerbsForResults } from '~/utils/verbPreview'
import { generateLetterOptions, generateEtymologyOptions, generateStemOptions, applyFilters } from '~/utils/searchFilters'

const { loadIndex } = useVerbs()
const { search } = useVerbSearch()

const pending = ref(false)
const showRegexHelp = ref(false)

const { data: index } = await useAsyncData('index-list', loadIndex)

// Sync search state with URL query params
const q = useRouteQuery<string>('q', '')
const searchType = useRouteQuery<'roots' | 'all'>('type', 'roots')
const regexMode = useRouteQuery<'on' | 'off'>('regex', 'on')
const caseParam = useRouteQuery<'on' | 'off'>('case', 'off')
const filterLetter = useRouteQuery<string | null>('letter', null)
const filterEtymology = useRouteQuery<string | null>('etymology', null)
const filterStem = useRouteQuery<string | null>('stem', null)

// Derived state
const searchEverything = computed({
    get: () => searchType.value === 'all',
    set: (value) => { searchType.value = value ? 'all' : 'roots' }
})

const useRegex = computed({
    get: () => regexMode.value === 'on',
    set: (value) => { regexMode.value = value ? 'on' : 'off' }
})

const caseSensitive = computed({
    get: () => caseParam.value === 'on',
    set: (value) => { caseParam.value = value ? 'on' : 'off' }
})

function getSearchPlaceholder() {
    if (regexMode.value === 'on') {
        return 'Regex search (use \\c for consonants, \\v for vowels)…'
    }
    return searchType.value === 'all'
        ? 'Search for roots, forms, translations, or etymology keywords…'
        : 'Search for verb roots…'
}

// Filters as computed getter for reactive access
const filters = computed(() => ({
    letter: filterLetter.value ?? null,
    etymology: filterEtymology.value ?? null,
    stem: filterStem.value ?? null
}))

// Initialize searchQuery from URL on mount, then sync with q
const searchQuery = ref<string>(q.value)
const results = ref<string[]>([])

// Store full verb data for previews
const verbDetails = ref<Map<string, Verb>>(new Map())
const loadingDetails = ref(false)

// Perform initial search from URL during SSR
if (searchQuery.value && searchQuery.value.trim().length >= 2) {
    const isSearchingEverything = searchType.value === 'all'
    const isUsingRegex = regexMode.value === 'on'
    const isCaseSensitive = caseParam.value === 'on'

    if (isSearchingEverything) {
    // In "everything" mode, always do comprehensive translation search
        console.log('[SSR] Searching everything (comprehensive translation search)...')
        const all = index.value?.roots || []
        const allRootNames = all.map(v => v.root)

        try {
            const response = await $fetch<{ total: number, roots: string[], verbData?: Record<string, Verb> }>('/api/verbs-translation-search', {
                method: 'POST',
                body: {
                    roots: allRootNames,
                    query: searchQuery.value,
                    useRegex: isUsingRegex,
                    caseSensitive: isCaseSensitive
                }
            })
            console.log('[SSR] Translation search found:', response.total, 'matches')
            results.value = response.roots

            // Use cached verb data from server to avoid client-side reload
            if (response.verbData) {
                console.log('[SSR] Using cached verb data from server:', Object.keys(response.verbData).length, 'verbs')
                verbDetails.value = new Map(Object.entries(response.verbData))
            }
        }
        catch (e) {
            console.error('[SSR] Translation search failed:', e)
            results.value = [] // Empty on error
        }
    }
    else {
    // In "roots only" mode, use fast index search
        const initialResults = await search(searchQuery.value, {
            rootsOnly: true,
            searchTranslations: false,
            useRegex: isUsingRegex,
            caseSensitive: isCaseSensitive
        })
        results.value = initialResults

        // Load verb details for SSR preview generation
        if (results.value.length > 0 && index.value?.roots) {
            console.log('[SSR] Loading verb details for', results.value.length, 'results...')
            const all = index.value.roots
            const matches = new Set(results.value)
            const matchedEntries = all.filter(v => matches.has(v.root))

            try {
                const details = await loadVerbsForResults(matchedEntries)
                verbDetails.value = details
                console.log('[SSR] Loaded', details.size, 'verb details for SSR')
            }
            catch (e) {
                console.error('[SSR] Failed to load verb details:', e)
            }
        }
    }
}

function performSearch() {
    searchQuery.value = q.value
}

function clearSearch() {
    q.value = ''
    searchQuery.value = ''
    results.value = []
    filterLetter.value = null
    filterEtymology.value = null
    filterStem.value = null
}

async function runSearch(value: string) {
    const isSearchingEverything = searchType.value === 'all'
    const isUsingRegex = regexMode.value === 'on'
    const isCaseSensitive = caseParam.value === 'on'
    console.log('[Index] Run search with value:', value, 'searchEverything:', isSearchingEverything, 'useRegex:', isUsingRegex)

    if (!index.value?.roots?.length) {
        try {
            const loaded = await loadIndex()
            index.value = loaded
        }
        catch (e) {
            console.error('[Index] Index not ready', e)
        }
    }

    if (!value || value.trim().length < 2) {
        console.log('[Index] Query too short, clearing results')
        results.value = []
        verbDetails.value.clear()
        pending.value = false
        return
    }

    results.value = []
    verbDetails.value.clear()
    pending.value = true

    if (isSearchingEverything) {
        // In "everything" mode, always do comprehensive translation search
        console.log('[Index] Searching everything (comprehensive translation search)...')
        const all = index.value?.roots || []
        const allRootNames = all.map(v => v.root)

        try {
            const response = await $fetch<{ total: number, roots: string[], verbData?: Record<string, Verb> }>('/api/verbs-translation-search', {
                method: 'POST',
                body: {
                    roots: allRootNames,
                    query: value,
                    useRegex: isUsingRegex,
                    caseSensitive: isCaseSensitive
                }
            })

            console.log('[Index] Translation search found:', response.total, 'matches')
            results.value = response.roots

            if (response.verbData) {
                console.log('[Index] Using cached verb data from server:', Object.keys(response.verbData).length, 'verbs')
                verbDetails.value = new Map(Object.entries(response.verbData))
            }
        }
        catch (e) {
            console.error('[Index] Translation search failed:', e)
            results.value = []
        }
    }
    else {
        // In "roots only" mode, use fast index search
        const primary = await search(value, {
            rootsOnly: true,
            searchTranslations: false,
            useRegex: isUsingRegex,
            caseSensitive: isCaseSensitive
        })

        console.log('[Index] Roots-only search returned:', primary.length, 'results')

        if (primary.length === 0 && !isUsingRegex) {
            console.log('[Index] No primary results, using fallback root search')
            const lower = value.toLowerCase()
            const all = index.value?.roots || []
            const alt = all
                .filter(v => v.root.toLowerCase().includes(lower))
                .map(v => v.root)

            console.log('[Index] Fallback found:', alt.length, 'results')
            results.value = alt
        }
        else {
            results.value = primary
        }
    }

    console.log('[Index] Final results.value:', results.value.length, 'results')
    pending.value = false
}

const baseResults = computed(() => {
    const all = index.value?.roots || []
    if (!searchQuery.value || searchQuery.value.trim().length < 2 || results.value.length === 0) {
        return []
    }
    const matches = new Set(results.value)
    return all.filter(v => matches.has(v.root))
})

const letterOptions = computed(() => generateLetterOptions(baseResults.value))
const etymologyOptions = computed(() => generateEtymologyOptions(baseResults.value))
const stemOptions = computed(() => generateStemOptions(baseResults.value))

function resetFilters() {
    filterLetter.value = null
    filterEtymology.value = null
    filterStem.value = null
}

watch(
    [searchQuery, searchType, regexMode, caseParam],
    () => {
        runSearch(searchQuery.value)
    }
)

// Keep searchQuery in sync when q changes (e.g., via Cmd/Ctrl+K global search)
watch(q, (newQ) => {
    searchQuery.value = newQ
})

const filtered = computed(() => {
    const result = baseResults.value
    if (result.length === 0) return []

    const applied = applyFilters(result, filters.value)
    console.log('[Index] Filtered result count:', applied.length)
    return applied
})

const displayed = computed(() => {
    const result = filtered.value
    console.log('[Index] Displayed count:', result.length)
    if (result.length > 0) {
        console.log('[Index] First displayed item:', result[0])
    }
    return result
})

// Load full verb data for previews when results change (client-side only)
watch(filtered, async (newFiltered) => {
    if (newFiltered.length === 0) {
        verbDetails.value.clear()
        return
    }

    // Check if we already have verb data (from SSR or translation search cache)
    const missingRoots = newFiltered.filter(v => !verbDetails.value.has(v.root))

    if (missingRoots.length === 0) {
        console.log('[Index] All verb details already cached, skipping load')
        return
    }

    // Load only missing verb details
    console.log(`[Index] Loading ${missingRoots.length} missing verb details...`)
    loadingDetails.value = true
    try {
        const details = await loadVerbsForResults(missingRoots)
        // Merge with existing details
        for (const [root, verb] of details.entries()) {
            verbDetails.value.set(root, verb)
        }
    }
    catch (e) {
        console.error('[Index] Failed to load verb details:', e)
    }
    finally {
        loadingDetails.value = false
    }
})
</script>
