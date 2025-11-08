<script setup lang="ts">
import { watchDebounced } from '@vueuse/core'
import { formatDateTime } from '~/utils/formatDateTime'
import type { TActivityEventType } from '#shared/config/activityEventTypes'
import type { IAdminActivityResponse } from '#shared/types/IAdminActivityResponse'
import type { LocationQueryValue } from 'vue-router'
import { activityEventTypes } from '#shared/config/activityEventTypes'

const PAGE_SIZE = 25
const route = useRoute()
const router = useRouter()
const clientPathHeader = useClientPathHeader()

type QueryValue = LocationQueryValue | LocationQueryValue[] | undefined

const toSingleValue = (value: QueryValue) => {
    if (Array.isArray(value)) {
        const first = value.find((entry): entry is string => typeof entry === 'string')
        return first ?? ''
    }
    return typeof value === 'string' ? value : ''
}

const toPageNumber = (value: QueryValue) => {
    const raw = Number(toSingleValue(value))
    return Number.isFinite(raw) && raw > 0 ? Math.floor(raw) : 1
}

const isEventType = (
    value: QueryValue
): value is TActivityEventType => {
    const candidate = toSingleValue(value)
    return activityEventTypes.includes(candidate as TActivityEventType)
}

const eventLabels: Record<TActivityEventType, string> = {
    search_fulltext: 'Full-text search',
    search_roots: 'Root search',
    view_stats: 'Stats view',
    view_verb: 'Verb view',
}

const initialSearch: string = toSingleValue(route.query.search)
const initialEvent: 'all' | TActivityEventType = isEventType(route.query.eventType)
    ? toSingleValue(route.query.eventType) as TActivityEventType
    : 'all'
const initialHost = typeof route.query.host === 'string' ? route.query.host : 'all'
const initialPage = toPageNumber(route.query.page)

const searchInput = ref(initialSearch)
const search = ref(initialSearch)
const selectedEvent = ref<'all' | TActivityEventType>(initialEvent)
const selectedHost = ref(initialHost)
const currentPage = ref(initialPage)

const updateRouteQuery = (updates: Record<string, string | undefined>) => {
    if (import.meta.server) return

    const merged: Record<string, string> = {}
    const next = {
        ...route.query,
        ...updates,
    }

    Object.entries(next).forEach(([key, value]) => {
        if (value === undefined || value === null || value === '') {
            return
        }

        if (Array.isArray(value)) {
            const first = value.find((entry): entry is string => typeof entry === 'string')
            if (first) {
                merged[key] = first
            }
            return
        }

        if (typeof value === 'string') {
            merged[key] = value
        }
    })

    router.replace({ query: merged })
}

if (import.meta.client) {
    watchDebounced(
        searchInput,
        (value) => {
            search.value = (value ?? '').trim()
            currentPage.value = 1
            updateRouteQuery({
                search: search.value || undefined,
                eventType: selectedEvent.value === 'all' ? undefined : selectedEvent.value,
                host: selectedHost.value === 'all' ? undefined : selectedHost.value,
                page: undefined,
            })
        },
        {
            debounce: 400,
            maxWait: 1200,
        }
    )

    watch(selectedEvent, (value) => {
        currentPage.value = 1
        updateRouteQuery({
            search: search.value || undefined,
            eventType: value === 'all' ? undefined : value,
            host: selectedHost.value === 'all' ? undefined : selectedHost.value,
            page: undefined,
        })
    })

    watch(selectedHost, (value) => {
        currentPage.value = 1
        updateRouteQuery({
            search: search.value || undefined,
            eventType: selectedEvent.value === 'all' ? undefined : selectedEvent.value,
            host: value === 'all' ? undefined : value,
            page: undefined,
        })
    })

    watch(currentPage, (page) => {
        updateRouteQuery({
            search: search.value || undefined,
            eventType: selectedEvent.value === 'all' ? undefined : selectedEvent.value,
            host: selectedHost.value === 'all' ? undefined : selectedHost.value,
            page: page > 1 ? String(page) : undefined,
        })
    })

    watch(
        () => route.query.search,
        (value) => {
            const next = toSingleValue(value)
            if (next === searchInput.value) return
            searchInput.value = next
            search.value = next.trim()
        }
    )

    watch(
        () => route.query.eventType,
        (value) => {
            const next = isEventType(value)
                ? toSingleValue(value) as TActivityEventType
                : 'all'
            if (next === selectedEvent.value) return
            selectedEvent.value = next
        }
    )

    watch(
        () => route.query.host,
        (value) => {
            const next = typeof value === 'string' ? value : 'all'
            if (next === selectedHost.value) return
            selectedHost.value = next
        }
    )

    watch(
        () => route.query.page,
        (value) => {
            const next = toPageNumber(value)
            if (next === currentPage.value) return
            currentPage.value = next
        }
    )
}

const activityEndpoint = computed(() => {
    const params = new URLSearchParams()
    if (search.value.trim()) {
        params.set('search', search.value.trim())
    }
    if (selectedEvent.value !== 'all') {
        params.set('eventType', selectedEvent.value)
    }
    if (selectedHost.value !== 'all') {
        params.set('host', selectedHost.value)
    }
    params.set('limit', String(PAGE_SIZE))
    params.set('offset', String((currentPage.value - 1) * PAGE_SIZE))
    const query = params.toString()
    return query ? `/api/admin/activity?${query}` : '/api/admin/activity'
})

const {
    data,
    pending,
    refresh,
} = await useFetch<IAdminActivityResponse>(activityEndpoint, { headers: clientPathHeader.value })

const events = computed(() => data.value?.events ?? [])
const total = computed(() => data.value?.total ?? 0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

const hostOptions = computed(() => {
    const hosts = new Set<string>()
    for (const entry of events.value) {
        if (entry.host) {
            hosts.add(entry.host)
        }
    }

    const sorted = Array.from(hosts).sort((a, b) => a.localeCompare(b))

    if (
        selectedHost.value !== 'all'
        && selectedHost.value
        && !hosts.has(selectedHost.value)
    ) {
        sorted.push(selectedHost.value)
    }

    return [
        {
            label: 'All hosts',
            value: 'all',
        },
        ...sorted.map(host => ({
            label: host,
            value: host,
        })),
    ]
})

watchEffect(() => {
    const maxPage = Math.max(1, Math.ceil((total.value || 0) / PAGE_SIZE))
    if (currentPage.value > maxPage) {
        currentPage.value = maxPage
    }
})

const counts = computed(() => {
    const base = Object.fromEntries(activityEventTypes.map(type => [type, 0])) as Record<TActivityEventType, number>
    const apiCounts = data.value?.counts
    if (apiCounts) {
        for (const type of activityEventTypes) {
            base[type] = apiCounts[type] ?? 0
        }
    }
    return base
})

const eventOptions = computed(() => [
    {
        label: 'All events',
        value: 'all',
    },
    ...activityEventTypes.map(type => ({
        label: eventLabels[type],
        value: type,
    })),
])

const getMetadataString = (
    metadata: Record<string, unknown> | null | undefined,
    key: string
) => {
    const value = metadata?.[key]
    return typeof value === 'string' ? value : null
}

const filterEntries = (filters: Record<string, unknown> | null | undefined) => {
    if (!filters || typeof filters !== 'object') {
        return []
    }
    return Object.entries(filters).filter(([, value]) => Boolean(value))
}

const metadataEntries = (metadata: Record<string, unknown> | null | undefined) => {
    if (!metadata || typeof metadata !== 'object') {
        return []
    }
    return Object.entries(metadata).filter(([key]) => key !== 'apiPath')
}

const statusColor = (status: number) => {
    if (status >= 500) return 'error'
    if (status >= 400) return 'warning'
    return 'success'
}

const goPrev = () => {
    if (currentPage.value > 1) {
        currentPage.value -= 1
    }
}

const goNext = () => {
    if (currentPage.value < totalPages.value) {
        currentPage.value += 1
    }
}

const handleRefresh = () => refresh()
</script>

<template>
    <AdminPageShell description="Activity · Detailed record of requests, filters, and outcomes.">
        <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
            <div
                v-for="type in activityEventTypes"
                :key="type"
                class="rounded-lg border border-gray-100 bg-gray-50/80 p-3 dark:border-gray-800 dark:bg-gray-900/40"
            >
                <p class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                    {{ eventLabels[type] }}
                </p>
                <p class="mt-2 text-xl font-semibold text-gray-900 dark:text-white">
                    {{ Number(counts[type] ?? 0).toLocaleString() }}
                </p>
            </div>
        </div>

        <UCard class="mt-6 space-y-4">
            <div class="grid gap-3 md:grid-cols-4">
                <UInput
                    v-model="searchInput"
                    icon="i-heroicons-magnifying-glass"
                    placeholder="Search by user, query, or route"
                    autocomplete="off"
                />
                <USelect
                    v-model="selectedEvent"
                    :items="eventOptions"
                    option-attribute="label"
                    value-attribute="value"
                />
                <USelect
                    v-model="selectedHost"
                    :items="hostOptions"
                    option-attribute="label"
                    value-attribute="value"
                />
                <div class="flex items-center justify-end gap-2">
                    <UBadge
                        v-if="pending"
                        color="primary"
                        variant="subtle"
                        size="sm"
                    >
                        Refreshing…
                    </UBadge>
                    <UButton
                        color="neutral"
                        variant="soft"
                        icon="i-heroicons-arrow-path"
                        class="w-full md:w-auto"
                        @click="handleRefresh"
                    >
                        Refresh
                    </UButton>
                </div>
            </div>

            <div
                v-if="events.length === 0 && !pending"
                class="rounded-xl border border-dashed px-6 py-12 text-center text-sm text-gray-500
                dark:border-gray-800 dark:text-gray-400"
            >
                No activity has been recorded for this filter.
            </div>

            <div v-else class="mt-4 overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 text-sm dark:divide-gray-800">
                    <thead class="bg-gray-50 dark:bg-gray-900/30">
                        <tr>
                            <th class="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">
                                When
                            </th>
                            <th class="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">
                                User & Event
                            </th>
                            <th class="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">
                                Payload
                            </th>
                            <th class="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">
                                Response
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                        <tr v-for="entry in events" :key="entry.id" class="align-top">
                            <td class="px-4 py-4 text-sm text-gray-900 dark:text-gray-100">
                                <div>{{ formatDateTime(entry.createdAt) }}</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">
                                    Session: {{ entry.sessionId || 'n/a' }}
                                </div>
                            </td>
                            <td class="px-4 py-4">
                                <div class="font-medium text-gray-900 dark:text-gray-100">
                                    {{ entry.userName || 'Unknown user' }}
                                </div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">
                                    {{ entry.userEmail }}
                                </div>
                                <UBadge
                                    class="mt-2"
                                    color="neutral"
                                    variant="soft"
                                    size="xs"
                                >
                                    {{ eventLabels[entry.eventType] }}
                                </UBadge>
                            </td>
                            <td class="space-y-2 px-4 py-4">
                                <div v-if="entry.query" class="text-sm text-gray-900 dark:text-gray-100">
                                    Query: <span class="font-semibold">{{ entry.query }}</span>
                                </div>
                                <div class="flex flex-wrap gap-2">
                                    <UBadge
                                        v-for="[key, value] in filterEntries(entry.filters)"
                                        :key="key"
                                        size="xs"
                                        color="primary"
                                        variant="subtle"
                                    >
                                        {{ key }}: {{ value }}
                                    </UBadge>
                                </div>
                                <div class="flex flex-wrap gap-2">
                                    <UBadge
                                        v-for="[key, value] in metadataEntries(entry.metadata).slice(0, 4)"
                                        :key="`${entry.id}-${key}`"
                                        size="xs"
                                        color="neutral"
                                        variant="soft"
                                    >
                                        {{ key }}: {{ value }}
                                    </UBadge>
                                </div>
                                <p class="text-xs text-gray-500 dark:text-gray-400">
                                    Path: {{ entry.path || '—' }}
                                    <span v-if="getMetadataString(entry.metadata, 'pageQuery')">
                                        {{ getMetadataString(entry.metadata, 'pageQuery') }}
                                    </span>
                                </p>
                                <p class="text-xs text-gray-500 dark:text-gray-400">
                                    Host: {{ entry.host || 'unknown' }}
                                </p>
                            </td>
                            <td class="space-y-1 px-4 py-4">
                                <div class="flex items-center gap-2">
                                    <UBadge :color="statusColor(entry.statusCode)" size="xs">
                                        {{ entry.statusCode }}
                                    </UBadge>
                                    <span class="text-sm text-gray-900 dark:text-gray-100">
                                        {{ entry.resultCount ?? '—' }} results
                                    </span>
                                </div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">
                                    Session: {{ entry.sessionId || 'n/a' }}
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div
                v-if="totalPages > 1"
                class="flex items-center justify-between border-t border-gray-100 pt-4 dark:border-gray-800"
            >
                <span class="text-xs text-gray-500 dark:text-gray-400">
                    Page {{ currentPage }} of {{ totalPages }}
                </span>
                <div class="flex items-center gap-2">
                    <UButton
                        color="neutral"
                        variant="outline"
                        size="xs"
                        :disabled="currentPage === 1"
                        @click="goPrev"
                    >
                        Previous
                    </UButton>
                    <UButton
                        color="neutral"
                        variant="outline"
                        size="xs"
                        :disabled="currentPage === totalPages"
                        @click="goNext"
                    >
                        Next
                    </UButton>
                </div>
            </div>
        </UCard>
    </AdminPageShell>
</template>
