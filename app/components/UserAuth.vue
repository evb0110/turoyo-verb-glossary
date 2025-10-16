<script setup lang="ts">
const { user: authUser, signOut } = useAuth()
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
    <div
        v-if="sessionUser"
        class="flex items-center gap-2 rounded-lg bg-white/70 dark:bg-white/10 border
            border-black/5 dark:border-white/10 px-3 h-12 min-w-[200px] shadow-sm backdrop-blur-md"
    >
        <UAvatar
            v-if="sessionUser.image"
            size="sm"
            :src="sessionUser.image"
            :alt="sessionUser.name || sessionUser.email || 'User'"
            referrerpolicy="no-referrer"
        />
        <UAvatar
            v-else
            size="sm"
            icon="i-heroicons-user-circle"
        />
        <div class="flex min-w-0 flex-1 flex-col leading-tight">
            <span class="text-sm font-medium text-gray-900 dark:text-white truncate">
                {{ sessionUser.name || sessionUser.email }}
            </span>
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
</template>
