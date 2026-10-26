<template>
    <div class="space-y-4">
        <div class="flex flex-col gap-3">
            <div
                class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between"
            >
                <div>
                    <h1>
                        {{ props.title }}
                    </h1>
                    <p
                        v-if="props.description"
                        class="mt-0.5 text-sm text-gray-600 dark:text-gray-400"
                    >
                        {{ props.description }}
                    </p>
                </div>
                <div class="flex items-center gap-3">
                    <slot name="header-actions"></slot>
                </div>
            </div>

            <nav
                class="flex flex-wrap gap-1 border-b border-gray-200 dark:border-gray-800"
            >
                <NuxtLink
                    v-for="link in links"
                    :key="link.to"
                    :to="link.to"
                    class="px-3 py-1 text-sm font-medium"
                    :class="
                        route.path === link.to
                            ? 'border-b-2 border-(--accent) text-(--accent)'
                            : 'text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-100'
                    "
                >
                    {{ link.label }}
                </NuxtLink>
            </nav>
        </div>

        <slot></slot>
    </div>
</template>

<script setup lang="ts">
const props = withDefaults(
    defineProps<{
        title?: string
        description?: string
    }>(),
    { title: 'Admin' }
)

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
