<script setup lang="ts">
const props = withDefaults(defineProps<{
    title?: string
    description?: string
}>(), { title: 'Admin' })

const route = useRoute()

const links = [
    {
        label: 'Users',
        to: '/admin',
    },
    {
        label: 'Sessions',
        to: '/admin/sessions',
    },
    {
        label: 'Activity',
        to: '/admin/activity',
    },
]
</script>

<template>
    <div class="container mx-auto max-w-6xl space-y-6 px-4 py-6">
        <div class="flex flex-col gap-4">
            <div
                class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between"
            >
                <div>
                    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
                        {{ props.title }}
                    </h1>
                    <p
                        v-if="props.description"
                        class="mt-1 text-gray-600 dark:text-gray-400"
                    >
                        {{ props.description }}
                    </p>
                </div>
                <div class="flex items-center gap-3">
                    <slot name="header-actions"></slot>
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

            <nav
                class="flex flex-wrap gap-1 rounded-xl border border-gray-200
                bg-white p-1 dark:border-gray-800 dark:bg-gray-900"
            >
                <NuxtLink
                    v-for="link in links"
                    :key="link.to"
                    :to="link.to"
                    class="flex-1 rounded-lg px-4 py-2 text-center text-sm font-medium
                    transition"
                    :class="route.path === link.to
                        ? 'bg-primary-100 text-primary-900 dark:bg-primary-500/20 dark:text-primary-50'
                        : 'text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-100'"
                >
                    {{ link.label }}
                </NuxtLink>
            </nav>
        </div>

        <slot></slot>
    </div>
</template>
