<template>
    <header
        class="sticky top-0 z-40 border-b border-gray-200/60 bg-white/70 backdrop-blur dark:border-gray-800/60 dark:bg-gray-950/70"
    >
        <UContainer class="flex items-center justify-between gap-4 py-4 max-w-5xl mx-auto ">
            <NuxtLink to="/" class="flex items-center gap-2 font-semibold text-lg whitespace-nowrap">
                <UIcon name="i-heroicons-book-open" class="h-6 w-6 text-primary" />
                <span>Turoyo Verb Glossary</span>
            </NuxtLink>
            <ClientOnly>
                <div v-if="sessionStatus === 'authenticated'" class="flex items-center gap-4">
                    <div class="flex gap-3 text-xs text-muted whitespace-nowrap">
                        <span>{{ displayStats.total_verbs }} verbs</span>
                        <span>•</span>
                        <span>{{ displayStats.total_stems }} stems</span>
                        <span>•</span>
                        <span>{{ displayStats.total_examples }} examples</span>
                    </div>
                    <UButton
                        v-if="isAdmin"
                        to="/admin"
                        size="sm"
                        color="purple"
                        variant="soft"
                        icon="i-heroicons-cog-6-tooth"
                    >
                        Admin
                        <template v-if="pendingCount > 0" #trailing>
                            <UBadge color="orange" variant="solid" size="xs">
                                {{ pendingCount }}
                            </UBadge>
                        </template>
                    </UButton>
                    <UserAuth />
                </div>
            </ClientOnly>
        </UContainer>
    </header>
</template>

<script setup lang="ts">
const { isAdmin, sessionStatus } = useAuth()

// Load pre-computed stats from /api/stats (generated at build time)
const { data: stats } = await useAsyncData('layout-stats', () =>
    $fetch('/api/stats')
)

const displayStats = computed(() => {
    return stats.value || { total_verbs: '—', total_stems: '—', total_examples: '—' }
})

// Fetch pending users count for admin (only when authenticated AND admin)
const shouldFetchPending = computed(() => sessionStatus.value === 'authenticated' && isAdmin.value)

const { data: pendingData, refresh: refreshPendingCount } = await useFetch<{ count: number }>('/api/admin/pending-count', {
    watch: false,
    server: false,
    lazy: true,
    immediate: false // Don't fetch immediately, wait for auth check
})

const pendingCount = computed(() => pendingData.value?.count || 0)

// Fetch pending count when user becomes authenticated admin
if (import.meta.client) {
    watch(shouldFetchPending, (should) => {
        if (should) {
            refreshPendingCount()
        }
    }, { immediate: true })

    // Show toast notification on login if there are pending users
    watch(pendingCount, (newCount, oldCount) => {
        if (isAdmin.value && newCount > 0 && oldCount === 0) {
            const toast = useToast()
            toast.add({
                title: 'Pending Users',
                description: `You have ${newCount} user${newCount > 1 ? 's' : ''} waiting for approval`,
                color: 'orange',
                icon: 'i-heroicons-bell'
            })
        }
    })
}
</script>
