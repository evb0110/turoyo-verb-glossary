<script setup lang="ts">
const { signOut, user } = useAuth()

definePageMeta({
    layout: false
})

const handleSignOut = async () => {
    await signOut()
}
</script>

<template>
    <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div class="max-w-md w-full mx-4">
            <UCard>
                <template #header>
                    <div class="text-center">
                        <div class="mx-auto w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-4">
                            <Icon name="i-heroicons-no-symbol" class="w-8 h-8 text-red-600 dark:text-red-400" />
                        </div>
                        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                            Access Blocked
                        </h1>
                    </div>
                </template>

                <div class="py-6 text-center">
                    <p class="text-gray-600 dark:text-gray-400 mb-4">
                        Your account has been blocked by an administrator.
                    </p>
                    <p class="text-sm text-gray-500 dark:text-gray-500 mb-6">
                        If you believe this is a mistake, please contact the site administrator.
                    </p>
                    <p class="text-xs text-gray-400 dark:text-gray-600">
                        Logged in as: {{ user?.email }}
                    </p>
                </div>

                <template #footer>
                    <UButton
                        block
                        color="neutral"
                        variant="soft"
                        @click="handleSignOut"
                    >
                        Sign out
                    </UButton>
                </template>
            </UCard>
        </div>
    </div>
</template>
