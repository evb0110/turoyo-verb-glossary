<script setup lang="ts">
const { user: authUser, loading: authLoading, isSessionKnown, signIn, signOut } = useAuth()
const sessionUser = computed(() => authUser.value)
const loggingOut = ref(false)

const handleSignOut = async () => {
    loggingOut.value = true
    try {
        await signOut()
    }
    finally {
        loggingOut.value = false
    }
}
</script>

<template>
    <ClientOnly>
        <template #fallback>
            <div class="h-12 w-[200px] rounded-lg bg-gray-300 dark:bg-gray-600 animate-pulse" />
        </template>
        <div class="flex items-center">
            <div v-if="!isSessionKnown" class="h-12 w-[200px] rounded-lg bg-gray-300 dark:bg-gray-600 animate-pulse" />
            <div v-else-if="sessionUser" class="flex items-center gap-2 rounded-lg bg-white/70 dark:bg-white/10 border border-black/5 dark:border-white/10 px-3 h-12 min-w-[200px] shadow-sm backdrop-blur-md">
                <UAvatar
                    size="sm"
                    :src="sessionUser.image || ''"
                    :alt="sessionUser.name || sessionUser.email || 'User'"
                    referrerpolicy="no-referrer"
                />
                <div class="flex min-w-0 flex-1 flex-col leading-tight">
                    <span class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ sessionUser.name || sessionUser.email }}</span>
                </div>
                <UButton
                    size="xs"
                    color="neutral"
                    variant="soft"
                    icon="i-heroicons-arrow-right-on-rectangle"
                    :loading="loggingOut"
                    @click="handleSignOut"
                />
            </div>
            <UButton
                v-else
                size="sm"
                color="neutral"
                variant="soft"
                :loading="authLoading"
                trailing-icon="i-heroicons-arrow-right-on-rectangle"
                class="h-12 min-w-[200px] text-sm font-medium text-gray-900 dark:text-white flex items-center justify-center gap-6"
                @click="signIn"
            >
                Sign in
            </UButton>
        </div>
    </ClientOnly>
</template>
