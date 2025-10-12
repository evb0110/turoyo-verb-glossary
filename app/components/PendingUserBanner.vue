<script setup lang="ts">
const { isPending } = useAuth()
</script>

<template>
    <div v-if="isPending" class="bg-orange-50 dark:bg-orange-900/20 border-b border-orange-200 dark:border-orange-800">
        <div class="container mx-auto px-4 py-4 max-w-5xl">
            <div class="flex items-center gap-3">
                <div class="flex-shrink-0">
                    <Icon name="i-heroicons-clock" class="w-6 h-6 text-orange-600 dark:text-orange-400" />
                </div>
                <div class="flex-1">
                    <h3 class="text-sm font-semibold text-orange-900 dark:text-orange-200">
                        Account Pending Approval
                    </h3>
                    <p class="text-sm text-orange-700 dark:text-orange-300">
                        Your account is pending approval. An admin will review your request shortly.
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>
