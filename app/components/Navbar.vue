<script setup lang="ts">
const {
    isAdmin,
    sessionStatus,
} = useAuth()

const { data: stats } = await useAsyncData('layout-stats', () =>
    $fetch('/api/stats')
)

const isAuthenticated = computed(() => sessionStatus.value === 'authenticated')

const displayStats = computed(() => {
    return stats.value || {
        total_verbs: '—',
        total_stems: '—',
        total_examples: '—',
    }
})

const shouldFetchPending = computed(() => isAuthenticated.value && isAdmin.value)

const {
    data: pendingData,
    refresh: refreshPendingCount,
} = await useAsyncData(
    'admin-pending-count',
    async () => {
        if (!isAdmin.value) return { count: 0 }
        try {
            return await $fetch<{ count: number }>('/api/admin/pending-count')
        }
        catch {
            return { count: 0 }
        }
    }
)

const pendingCount = computed(() => pendingData.value?.count || 0)

if (import.meta.client) {
    const hasHydrated = ref(false)
    onMounted(() => {
        hasHydrated.value = true
    })

    watch(shouldFetchPending, (should, wasShould) => {
        if (hasHydrated.value && should && !wasShould) {
            refreshPendingCount()
        }
    })

    watch(pendingCount, (newCount, oldCount) => {
        if (isAdmin.value && newCount > 0 && oldCount === 0) {
            const toast = useToast()
            toast.add({
                title: 'Pending Users',
                description: `You have ${newCount} user${newCount > 1 ? 's' : ''} waiting for approval`,
                color: 'warning',
                icon: 'i-heroicons-bell',
            })
        }
    })
}
</script>

<template>
    <header
        class="sticky top-0 z-40 border-b border-gray-200/60 bg-white/70 backdrop-blur
            dark:border-gray-800/60 dark:bg-gray-950/70"
    >
        <UContainer class="flex items-center justify-between gap-4 py-4 max-w-5xl mx-auto ">
            <NuxtLink to="/" class="flex items-center gap-2 font-semibold text-lg whitespace-nowrap">
                <UIcon name="i-heroicons-book-open" class="h-6 w-6 text-primary"/>
                <span>Turoyo Verb Glossary</span>
            </NuxtLink>
            <div v-if="isAuthenticated" class="flex items-center gap-4">
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
                    color="primary"
                    variant="soft"
                    icon="i-heroicons-cog-6-tooth"
                >
                    Admin
                    <template v-if="pendingCount > 0" #trailing>
                        <UBadge color="warning" variant="solid" size="xs">
                            {{ pendingCount }}
                        </UBadge>
                    </template>
                </UButton>
                <UserAuth/>
            </div>
        </UContainer>
    </header>
</template>
