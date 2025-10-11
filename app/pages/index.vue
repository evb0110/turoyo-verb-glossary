<template>
    <div class="space-y-6 px-6 py-4">
        <UCard>
            <div class="space-y-4">
                <div class="flex flex-col gap-3">
                    <div class="flex items-center gap-3 flex-wrap">
                        <span class="text-sm text-gray-600 dark:text-gray-400">Search type:</span>
                        <span
                            :class="!searchEverything ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                            class="text-sm cursor-pointer transition-all"
                            @click="searchEverything = false"
                        >
                            Roots only
                        </span>
                        <USwitch v-model="searchEverything" />
                        <span
                            :class="searchEverything ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                            class="text-sm cursor-pointer transition-all"
                            @click="searchEverything = true"
                        >
                            Everything
                        </span>

                        <span class="text-sm text-gray-400 dark:text-gray-600">|</span>

                        <span class="text-sm text-gray-600 dark:text-gray-400">Regex:</span>
                        <span
                            :class="!useRegex ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                            class="text-sm cursor-pointer transition-all"
                            @click="useRegex = false"
                        >
                            Off
                        </span>
                        <USwitch v-model="useRegex" />
                        <span
                            :class="useRegex ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                            class="text-sm cursor-pointer transition-all"
                            @click="useRegex = true"
                        >
                            On
                        </span>

                        <UButton
                            color="neutral"
                            variant="ghost"
                            size="xs"
                            icon="i-heroicons-question-mark-circle"
                            :class="useRegex ? '' : 'invisible pointer-events-none'"
                            :aria-hidden="!useRegex"
                            tabindex="-1"
                            @click="showRegexHelp = true"
                        >
                            Help
                        </UButton>

                        <span class="text-sm text-gray-400 dark:text-gray-600">|</span>

                        <span class="text-sm text-gray-600 dark:text-gray-400">Case sensitive:</span>
                        <span
                            :class="!caseSensitive ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                            class="text-sm cursor-pointer transition-all"
                            @click="caseSensitive = false"
                        >
                            Off
                        </span>
                        <USwitch v-model="caseSensitive" />
                        <span
                            :class="caseSensitive ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                            class="text-sm cursor-pointer transition-all"
                            @click="caseSensitive = true"
                        >
                            On
                        </span>
                    </div>

                    <div class="flex gap-2">
                        <UInput
                            v-model="q"
                            :placeholder="getSearchPlaceholder()"
                            class="flex-1"
                            clearable
                            icon="i-heroicons-magnifying-glass"
                            @keydown.enter="performSearch"
                            @update:model-value="(value) => { if (!value) clearSearch() }"
                        />
                        <UButton
                            :disabled="!q || q.trim().length < 2"
                            color="neutral"
                            icon="i-heroicons-magnifying-glass"
                            variant="outline"
                            @click="performSearch"
                        >
                            Search
                        </UButton>
                    </div>
                </div>

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

                <div v-if="searchQuery.length >= 2" class="flex flex-wrap items-center gap-3 pt-4 text-sm text-muted">
                    <span>
                        {{ displayed.length }} {{ displayed.length === 1 ? 'match' : 'matches' }}
                    </span>
                    <UBadge v-if="searchQuery.length" variant="soft">
                        Query: {{ searchQuery }}
                    </UBadge>
                    <UBadge v-if="filters.letter" color="primary" variant="soft">
                        Letter: {{ filters.letter }}
                    </UBadge>
                    <UBadge v-if="filters.etymology" color="success" variant="soft">
                        Etymology: {{ filters.etymology }}
                    </UBadge>
                    <UBadge v-if="filters.stem" color="info" variant="soft">
                        Stem: {{ filters.stem }}
                    </UBadge>
                </div>

                <UTable
                    v-if="searchQuery.length >= 2"
                    :columns="columns"
                    :data="displayed"
                    :loading="pending"
                    ref="resultsTableRef"
                >
                    <template #root-cell="{ row }">
                        <NuxtLink
                            :to="`/verbs/${rootToSlug(row.original.root)}`"
                            class="font-semibold text-primary hover:underline turoyo-text"
                        >
                            {{ row.original.root }}
                        </NuxtLink>
                    </template>

                    <template #etymology_source-cell="{ row }">
                        <span class="text-sm">{{ row.original.etymology_sources?.join(', ') || '—' }}</span>
                    </template>

                    <template #preview-cell="{ row }">
                        <div v-if="verbDetails.has(row.original.root)" class="verb-preview">
                            <template v-if="searchType === 'roots'">
                                <!-- Full article preview for "roots only" mode -->
                                <div
                                    class="preview-content"
                                    v-html="generateFullPreview(verbDetails.get(row.original.root)!)"
                                />
                            </template>
                            <template v-else>
                                <!-- Try to show excerpts for "everything" mode -->
                                <div
                                    v-if="generateExcerpts(
                                        verbDetails.get(row.original.root)!,
                                        searchQuery,
                                        { useRegex: regexMode === 'on', caseSensitive: caseParam === 'on', maxExcerpts: 5 }
                                    ).length > 0"
                                    class="preview-excerpts"
                                >
                                    <div
                                        v-for="(excerpt, i) in generateExcerpts(
                                            verbDetails.get(row.original.root)!,
                                            searchQuery,
                                            { useRegex: regexMode === 'on', caseSensitive: caseParam === 'on', maxExcerpts: 5 }
                                        )"
                                        :key="i"
                                        class="preview-excerpt"
                                    >
                                        <span class="excerpt-label">{{ excerpt.label }}</span>
                                        <span class="excerpt-text">{{ excerpt.text }}</span>
                                    </div>
                                </div>
                                <!-- Fallback to full preview if no excerpts found -->
                                <div
                                    v-else
                                    class="preview-content"
                                    v-html="generateFullPreview(verbDetails.get(row.original.root)!)"
                                />
                            </template>
                        </div>
                        <div v-else class="text-sm text-gray-400">
                            {{ loadingDetails ? 'Loading...' : '—' }}
                        </div>
                    </template>
                </UTable>

                <div
                    v-if="searchQuery.length >= 2 && filtered.length === 0 && !pending"
                    class="rounded-lg border border-dashed px-4 py-6 text-center text-sm text-muted"
                >
                    No matches found. Try another keyword or broaden your search.
                </div>
            </div>
        </UCard>

        <!-- Regex Help Modal -->
        <UModal v-model:open="showRegexHelp" :ui="{ content: 'sm:max-w-2xl' }" title="Regex Search Help">
            <template #body>
                <div class="space-y-4">
                    <div>
                        <h4 class="font-medium text-sm mb-2">Turoyo-Specific Shortcuts</h4>
                        <div class="space-y-2 text-sm">
                            <div class="flex gap-3">
                                <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">\c</code>
                                <span class="text-gray-600 dark:text-gray-400">Matches any Turoyo consonant (b, d, f, g, h, k, l, m, n, p, q, r, s, t, v, w, x, y, z, č, ġ, š, ž, ǧ, ʔ, ʕ, ḏ, ḥ, ṣ, ṭ, etc.)</span>
                            </div>
                            <div class="flex gap-3">
                                <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">\v</code>
                                <span class="text-gray-600 dark:text-gray-400">Matches any Turoyo vowel (a, e, i, o, u, ə, ǝ, é, ī, á, etc.)</span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h4 class="font-medium text-sm mb-2">Standard Regex Syntax</h4>
                        <div class="grid grid-cols-2 gap-2 text-sm">
                            <div class="flex gap-2">
                                <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">^</code>
                                <span class="text-gray-600 dark:text-gray-400">Start of string</span>
                            </div>
                            <div class="flex gap-2">
                                <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">$</code>
                                <span class="text-gray-600 dark:text-gray-400">End of string</span>
                            </div>
                            <div class="flex gap-2">
                                <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">.</code>
                                <span class="text-gray-600 dark:text-gray-400">Any character</span>
                            </div>
                            <div class="flex gap-2">
                                <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">*</code>
                                <span class="text-gray-600 dark:text-gray-400">0 or more times</span>
                            </div>
                            <div class="flex gap-2">
                                <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">+</code>
                                <span class="text-gray-600 dark:text-gray-400">1 or more times</span>
                            </div>
                            <div class="flex gap-2">
                                <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">?</code>
                                <span class="text-gray-600 dark:text-gray-400">0 or 1 time</span>
                            </div>
                            <div class="flex gap-2">
                                <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">[abc]</code>
                                <span class="text-gray-600 dark:text-gray-400">Any of a, b, or c</span>
                            </div>
                            <div class="flex gap-2">
                                <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">|</code>
                                <span class="text-gray-600 dark:text-gray-400">OR operator</span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h4 class="font-medium text-sm mb-2">Examples</h4>
                        <div class="space-y-2 text-sm">
                            <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                                <code class="font-mono text-primary">b\vd</code>
                                <p class="text-gray-600 dark:text-gray-400 mt-1">Finds: b + vowel + d (e.g., "bdl", "bdy")</p>
                            </div>
                            <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                                <code class="font-mono text-primary">\c\c\c</code>
                                <p class="text-gray-600 dark:text-gray-400 mt-1">Finds: Any sequence of 3 consonants</p>
                            </div>
                            <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                                <code class="font-mono text-primary">^\c\c\c$</code>
                                <p class="text-gray-600 dark:text-gray-400 mt-1">Finds: Roots that are exactly 3 consonants</p>
                            </div>
                            <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                                <code class="font-mono text-primary">^ʕ</code>
                                <p class="text-gray-600 dark:text-gray-400 mt-1">Finds: Roots starting with ʕ</p>
                            </div>
                            <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                                <code class="font-mono text-primary">le$</code>
                                <p class="text-gray-600 dark:text-gray-400 mt-1">Finds: Forms ending with "le"</p>
                            </div>
                            <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                                <code class="font-mono text-primary">^m\c\v</code>
                                <p class="text-gray-600 dark:text-gray-400 mt-1">Finds: Forms starting with m + consonant + vowel</p>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </UModal>
    </div>
</template>

<script lang="ts" setup>
import { useRouteQuery } from '@vueuse/router'
import type { Filters } from '~/types/types/search'
import type { Verb } from '~/composables/useVerbs'
import { clearHighlights, findTextRanges, findRegexRanges, setHighlights } from '~/utils/highlight'
import { createSearchRegex } from '~/utils/regexSearch'
import { loadVerbsForResults, generateExcerpts, generateFullPreview } from '~/utils/verbPreview'

const { loadIndex, search, rootToSlug } = useVerbs()

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
    set: (value) => {
        searchType.value = value ? 'all' : 'roots'
    }
})

const useRegex = computed({
    get: () => regexMode.value === 'on',
    set: (value) => {
        regexMode.value = value ? 'on' : 'off'
    }
})

const caseSensitive = computed({
    get: () => caseParam.value === 'on',
    set: (value) => {
        caseParam.value = value ? 'on' : 'off'
    }
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
const filters = computed<Filters>(() => ({
    letter: filterLetter.value,
    etymology: filterEtymology.value,
    stem: filterStem.value
}))

// Initialize searchQuery from URL on mount, then sync with q
const searchQuery = ref<string>(q.value)
const results = ref<string[]>([])
const resultsTableRef = ref()

// Store full verb data for previews
const verbDetails = ref<Map<string, Verb>>(new Map())
const loadingDetails = ref(false)

// Perform initial search from URL during SSR (index only, translation search happens client-side)
if (searchQuery.value && searchQuery.value.trim().length >= 2) {
    const isSearchingEverything = searchType.value === 'all'
    const isUsingRegex = regexMode.value === 'on'
    const isCaseSensitive = caseParam.value === 'on'

    const initialResults = await search(searchQuery.value, {
        rootsOnly: !isSearchingEverything,
        searchTranslations: false, // Translation search is client-side only
        useRegex: isUsingRegex,
        caseSensitive: isCaseSensitive
    })
    results.value = initialResults
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

const baseResults = computed(() => {
    const all = index.value?.roots || []
    if (!searchQuery.value || searchQuery.value.trim().length < 2 || results.value.length === 0) {
        return []
    }
    const matches = new Set(results.value)
    return all.filter(v => matches.has(v.root))
})

const letterOptions = computed(() => {
    const currentResults = baseResults.value

    if (currentResults.length === 0) {
        return [{ label: 'All letters', value: null }]
    }

    const letterCounts = new Map<string, number>()
    currentResults.forEach((v) => {
        const letter = v.root?.[0]
        if (letter) {
            letterCounts.set(letter, (letterCounts.get(letter) || 0) + 1)
        }
    })

    return [
        { label: 'All letters', value: null },
        ...Array.from(letterCounts.entries())
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([letter, count]) => ({ label: `${letter} (${count})`, value: letter }))
    ]
})

const etymologyOptions = computed(() => {
    const currentResults = baseResults.value

    if (currentResults.length === 0) {
        return [{ label: 'All etymologies', value: null }]
    }

    const etymCounts = new Map<string, number>()
    currentResults.forEach((v) => {
        const sources = v.etymology_sources?.length ? v.etymology_sources : ['Unknown']
        sources.forEach((source) => {
            etymCounts.set(source, (etymCounts.get(source) || 0) + 1)
        })
    })

    return [
        { label: 'All etymologies', value: null },
        ...Array.from(etymCounts.entries())
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([source, count]) => ({ label: `${source} (${count})`, value: source }))
    ]
})

const stemOptions = computed(() => {
    const currentResults = baseResults.value

    if (currentResults.length === 0) {
        return [{ label: 'All stems', value: null }]
    }

    const stemCounts = new Map<string, number>()
    currentResults.forEach((v) => {
        v.stems.forEach((stem) => {
            stemCounts.set(stem, (stemCounts.get(stem) || 0) + 1)
        })
    })

    return [
        { label: 'All stems', value: null },
        ...Array.from(stemCounts.entries())
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([stem, count]) => ({ label: `${stem} (${count})`, value: stem }))
    ]
})

function resetFilters() {
    filterLetter.value = null
    filterEtymology.value = null
    filterStem.value = null
}

watch(
    [searchQuery, searchType, regexMode, caseParam],
    async () => {
        const value = searchQuery.value
        const isSearchingEverything = searchType.value === 'all'
        const isUsingRegex = regexMode.value === 'on'
        const isCaseSensitive = caseParam.value === 'on'
        console.log('[Index] Watch triggered with value:', value, 'searchEverything:', isSearchingEverything, 'useRegex:', isUsingRegex)

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
            pending.value = false
            return
        }

        pending.value = true

        if (isSearchingEverything) {
            // Search everything: roots, forms, translations
            // First try fast index search (roots + forms)
            const primary = await search(value, {
                rootsOnly: false,
                searchTranslations: false,
                useRegex: isUsingRegex,
                caseSensitive: isCaseSensitive
            })

            console.log('[Index] Primary search returned:', primary.length, 'results')

            // If no results, do server-side translation search
            if (primary.length === 0) {
                console.log('[Index] No results in index, searching translations on server...')
                const all = index.value?.roots || []
                const allRootNames = all.map(v => v.root)

                try {
                    const response = await $fetch<{ total: number, roots: string[] }>('/api/verbs-translation-search', {
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
                }
                catch (e) {
                    console.error('[Index] Translation search failed:', e)
                    results.value = []
                }
            }
            else {
                results.value = primary
            }
        }
        else {
            // Search roots only (not forms or translations)
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
)

const filtered = computed(() => {
    let result = baseResults.value

    if (result.length === 0) {
        return []
    }

    if (filters.value.letter) {
        result = result.filter(v => v.root.startsWith(filters.value.letter as string))
    }

    if (filters.value.etymology) {
        result = result.filter(v =>
            v.etymology_sources?.includes(filters.value.etymology as string)
            || (!v.etymology_sources?.length && filters.value.etymology === 'Unknown')
        )
    }

    if (filters.value.stem) {
        result = result.filter(v => v.stems.includes(filters.value.stem as string))
    }

    console.log('[Index] Filtered result count:', result.length)
    return result
})

const displayed = computed(() => {
    const result = filtered.value
    console.log('[Index] Displayed count:', result.length)
    if (result.length > 0) {
        console.log('[Index] First displayed item:', result[0])
    }
    return result
})

// Load full verb data for previews when results change
watch(filtered, async (newFiltered) => {
    if (newFiltered.length === 0) {
        verbDetails.value.clear()
        return
    }

    // Load verb details for all displayed results
    loadingDetails.value = true
    try {
        const details = await loadVerbsForResults(newFiltered)
        verbDetails.value = details
    }
    catch (e) {
        console.error('[Index] Failed to load verb details:', e)
    }
    finally {
        loadingDetails.value = false
    }
}, { immediate: true })

// Apply custom highlights on the client for non-regex search
if (import.meta.client) {
    const applyHighlights = () => {
        try {
            const container: HTMLElement | undefined = (resultsTableRef as any).value?.$el || (resultsTableRef as any).value?.$refs?.table || (resultsTableRef as any).value
            const qText = searchQuery.value?.trim() || ''
            if (!container || !qText || qText.length < 2) {
                clearHighlights('search-match')
                return
            }
            // Choose plain or regex-based highlighting
            let ranges
            const isUsingRegex = regexMode.value === 'on'
            const isCaseSensitive = caseParam.value === 'on'

            if (isUsingRegex) {
                try {
                    const re = createSearchRegex(qText, { caseSensitive: isCaseSensitive })
                    // Force global matching; helper will add 'g' anyway
                    ranges = findRegexRanges(container, re)
                }
                catch {
                    clearHighlights('search-match')
                    return
                }
            } else {
                ranges = findTextRanges(container, qText, { caseSensitive: isCaseSensitive })
            }
            setHighlights('search-match', container, ranges)
        }
        catch {
            // ignore
        }
    }

    watch([displayed, searchQuery, caseParam, regexMode, verbDetails], async () => {
        await nextTick()
        applyHighlights()
    })

    onMounted(() => applyHighlights())
    onBeforeUnmount(() => clearHighlights('search-match'))
}

const columns = [
    {
        accessorKey: 'root',
        header: 'Root',
        size: 150
    },
    {
        accessorKey: 'etymology_source',
        header: 'Etymology',
        size: 120
    },
    {
        accessorKey: 'preview',
        header: 'Article Preview'
    }
]

// Intentionally not setting a page title here so the global
// default site title is used in the tab.
</script>
