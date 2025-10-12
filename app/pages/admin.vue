<script setup lang="ts">
import type { AuthUser } from '~/composables/useAuth'

const { user } = useAuth()

// Fetch users list
// Note: Auth redirects are handled by app/plugins/auth-redirect.client.ts
const { data: users, refresh: refreshUsers } = await useFetch<AuthUser[]>('/api/admin/users', {
    watch: false
})

const loading = ref<string | null>(null)
const toastStore = useToast()

const approveUser = async (userId: string) => {
    loading.value = userId
    try {
        await $fetch(`/api/admin/users/${userId}/approve`, {
            method: 'PATCH'
        })
        await refreshUsers()
        toastStore.add({
            title: 'User approved',
            description: 'User has been approved successfully',
            color: 'success'
        })
    }
    catch (error) {
        console.error('Error approving user:', error)
        toastStore.add({
            title: 'Error',
            description: 'Failed to approve user',
            color: 'error'
        })
    }
    finally {
        loading.value = null
    }
}

const blockUser = async (userId: string) => {
    loading.value = userId
    try {
        await $fetch(`/api/admin/users/${userId}/block`, {
            method: 'PATCH'
        })
        await refreshUsers()
        toastStore.add({
            title: 'User blocked',
            description: 'User has been blocked successfully',
            color: 'warning'
        })
    }
    catch (error) {
        console.error('Error blocking user:', error)
        toastStore.add({
            title: 'Error',
            description: 'Failed to block user',
            color: 'error'
        })
    }
    finally {
        loading.value = null
    }
}

const unblockUser = async (userId: string) => {
    loading.value = userId
    try {
        await $fetch(`/api/admin/users/${userId}/unblock`, {
            method: 'PATCH'
        })
        await refreshUsers()
        toastStore.add({
            title: 'User unblocked',
            description: 'User has been unblocked successfully',
            color: 'success'
        })
    }
    catch (error) {
        console.error('Error unblocking user:', error)
        toastStore.add({
            title: 'Error',
            description: 'Failed to unblock user',
            color: 'error'
        })
    }
    finally {
        loading.value = null
    }
}

const getRoleBadgeColor = (role: string) => {
    switch (role) {
        case 'admin':
            return 'primary'
        case 'user':
            return 'success'
        case 'pending':
            return 'warning'
        case 'blocked':
            return 'error'
        default:
            return 'neutral'
    }
}

const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}
</script>

<template>
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <div class="mb-8">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
                        User Management
                    </h1>
                    <p class="mt-2 text-gray-600 dark:text-gray-400">
                        Manage user access and permissions
                    </p>
                </div>
                <UButton
                    to="/"
                    color="neutral"
                    variant="soft"
                    icon="i-heroicons-arrow-left"
                >
                    Back to Glossary
                </UButton>
            </div>
        </div>

        <UCard>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead>
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                User
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                Email
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                Role
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                Joined
                            </th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                        <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <UAvatar
                                        :src="u.image || ''"
                                        :alt="u.name"
                                        size="sm"
                                        class="mr-3"
                                    />
                                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ u.name }}
                                        <span v-if="u.id === user?.id" class="ml-2 text-xs text-gray-500 dark:text-gray-400">(You)</span>
                                    </div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                                {{ u.email }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <UBadge :color="getRoleBadgeColor(u.role)" variant="subtle">
                                    {{ u.role }}
                                </UBadge>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                                {{ formatDate(u.createdAt) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <div class="flex justify-end gap-2">
                                    <UButton
                                        v-if="u.role === 'pending'"
                                        size="xs"
                                        color="success"
                                        variant="outline"
                                        :loading="loading === u.id"
                                        @click="approveUser(u.id)"
                                    >
                                        Approve
                                    </UButton>
                                    <UButton
                                        v-if="u.role === 'user' && u.id !== user?.id"
                                        size="xs"
                                        color="error"
                                        variant="outline"
                                        :loading="loading === u.id"
                                        @click="blockUser(u.id)"
                                    >
                                        Block
                                    </UButton>
                                    <UButton
                                        v-if="u.role === 'blocked'"
                                        size="xs"
                                        color="success"
                                        variant="outline"
                                        :loading="loading === u.id"
                                        @click="unblockUser(u.id)"
                                    >
                                        Unblock
                                    </UButton>
                                    <span v-if="u.id === user?.id" class="text-xs text-gray-400 dark:text-gray-600 px-2 py-1" />
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </UCard>

        <div v-if="!users || users.length === 0" class="text-center py-12">
            <p class="text-gray-500 dark:text-gray-400">
                No users found
            </p>
        </div>
    </div>
</template>
