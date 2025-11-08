<script setup lang="ts">
import { watchDebounced } from '@vueuse/core'
import { formatDateTime } from '~/utils/formatDateTime'
import type { IAdminSessionsResponse } from '#shared/types/IAdminSessionsResponse'
import type { IUserSessionActivity } from '#shared/types/IUserSessionActivity'
import type { LocationQueryValue } from 'vue-router'

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

const initialSearch: string = toSingleValue(route.query.search)
const initialPage = toPageNumber(route.query.page)

const searchInput = ref(initialSearch)
const search = ref(initialSearch)
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
                page: undefined,
            })
        },
        {
            debounce: 400,
            maxWait: 1200,
        }
    )

    watch(currentPage, (page) => {
        updateRouteQuery({
            search: search.value || undefined,
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
        () => route.query.page,
        (value) => {
            const next = toPageNumber(value)
            if (next === currentPage.value) return
            currentPage.value = next
        }
    )
}

const sessionsEndpoint = computed(() => {
    const params = new URLSearchParams()
    if (search.value.trim()) {
        params.set('search', search.value.trim())
    }
    params.set('limit', String(PAGE_SIZE))
    params.set('offset', String((currentPage.value - 1) * PAGE_SIZE))
    const query = params.toString()
    return query ? `/api/admin/sessions?${query}` : '/api/admin/sessions'
})

const {
    data,
    pending,
    refresh,
} = await useFetch<IAdminSessionsResponse>(sessionsEndpoint, { headers: clientPathHeader.value })

const sessions = computed(() => data.value?.sessions ?? [])
const total = computed(() => data.value?.total ?? 0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

watchEffect(() => {
    const maxPage = Math.max(1, Math.ceil((total.value || 0) / PAGE_SIZE))
    if (currentPage.value > maxPage) {
        currentPage.value = maxPage
    }
})

const summary = computed(() => {
    const now = Date.now()
    const activeInDay = sessions.value.filter((session) => {
        const last = new Date(session.lastActivityAt).getTime()
        return now - last <= 86_400_000
    })

    const totalRequests = sessions.value.reduce((sum, session) => sum + (session.totalRequests ?? 0), 0)
    const searchRequests = sessions.value.reduce((sum, session) => sum + (session.searchRequests ?? 0), 0)

    return {
        tracked: total.value,
        activeInDay: activeInDay.length,
        avgRequests: sessions.value.length
            ? Math.round(totalRequests / sessions.value.length)
            : 0,
        searchRequests,
    }
})

const summaryCards = computed(() => [
    {
        label: 'Tracked sessions',
        value: summary.value.tracked,
    },
    {
        label: 'Active (24h)',
        value: summary.value.activeInDay,
    },
    {
        label: 'Average requests',
        value: summary.value.avgRequests,
    },
    {
        label: 'Searches on page',
        value: summary.value.searchRequests,
    },
])

const filterEntries = (filters: IUserSessionActivity['lastFilters']) => {
    if (!filters || typeof filters !== 'object') {
        return []
    }

    return Object.entries(filters).filter(([, value]) => Boolean(value))
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
    <AdminPageShell description="Sessions · Inspect devices, requests, and filters.">
        <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
            <div
                v-for="card in summaryCards"
                :key="card.label"
                class="rounded-lg border border-gray-100 bg-gray-50/80 p-3 dark:border-gray-800 dark:bg-gray-900/40"
            >
                <p class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                    {{ card.label }}
                </p>
                <p class="mt-2 text-xl font-semibold text-gray-900 dark:text-white">
                    {{ card.value.toLocaleString() }}
                </p>
            </div>
        </div>

        <UCard class="mt-6 space-y-4">
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <UInput
                    v-model="searchInput"
                    icon="i-heroicons-magnifying-glass"
                    placeholder="Filter by user, email, IP"
                    class="md:max-w-md"
                    autocomplete="off"
                />
                <div class="flex items-center gap-2">
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
                        @click="handleRefresh"
                    >
                        Refresh
                    </UButton>
                </div>
            </div>

            <div
                v-if="sessions.length === 0 && !pending"
                class="rounded-xl border border-dashed px-6 py-12 text-center text-sm text-gray-500
                dark:border-gray-800 dark:text-gray-400"
            >
                No sessions have been recorded yet.
            </div>

            <div v-else class="mt-4 overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 text-sm dark:divide-gray-800">
                    <thead class="bg-gray-50 dark:bg-gray-900/30">
                        <tr>
                            <th class="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">
                                User
                            </th>
                            <th class="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">
                                Device
                            </th>
                            <th class="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">
                                Activity
                            </th>
                            <th class="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">
                                Requests
                            </th>
                            <th class="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">
                                Last search
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                        <tr v-for="session in sessions" :key="session.id" class="align-top">
                            <td class="px-4 py-4">
                                <div class="font-medium text-gray-900 dark:text-gray-100">
                                    {{ session.userName || 'Unknown user' }}
                                </div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">
                                    {{ session.userEmail }}
                                </div>
                                <div class="text-xs text-gray-400 dark:text-gray-500">
                                    Session ID: {{ session.sessionId }}
                                </div>
                            </td>
                            <td class="space-y-1 px-4 py-4">
                                <p class="text-sm text-gray-700 dark:text-gray-200">
                                    {{ session.ipAddress || 'Unknown IP' }}
                                </p>
                                <p class="max-w-xs break-words text-xs text-gray-500 dark:text-gray-400">
                                    {{ session.userAgent || '—' }}
                                </p>
                            </td>
                            <td class="space-y-1 px-4 py-4">
                                <div class="text-sm text-gray-900 dark:text-gray-100">
                                    Last: {{ formatDateTime(session.lastActivityAt) }}
                                </div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">
                                    Started: {{ formatDateTime(session.createdAt) }}
                                </div>
                            </td>
                            <td class="px-4 py-4">
                                <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">
                                    {{ session.totalRequests.toLocaleString() }} total
                                </div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">
                                    {{ session.searchRequests.toLocaleString() }} searches ·
                                    {{ session.statsRequests.toLocaleString() }} stats
                                </div>
                            </td>
                            <td class="px-4 py-4">
                                <div class="text-sm text-gray-900 dark:text-gray-100">
                                    {{ session.lastSearchQuery || '—' }}
                                </div>
                                <div class="mt-2 flex flex-wrap gap-2">
                                    <UBadge
                                        v-for="[key, value] in filterEntries(session.lastFilters)"
                                        :key="key"
                                        color="neutral"
                                        variant="soft"
                                        size="xs"
                                    >
                                        {{ key }}: {{ value }}
                                    </UBadge>
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
