<template>
    <div class="space-y-4">
        <div class="flex flex-col gap-3">
            <div class="flex items-center gap-3 flex-wrap">
                <span class="text-sm text-gray-600 dark:text-gray-400">Search type:</span>
                <span
                    :class="!searchEverything ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="searchEverything = false"
                >
                    Roots only
                </span>
                <USwitch v-model="searchEverything" />
                <span
                    :class="searchEverything ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="searchEverything = true"
                >
                    Everything
                </span>

                <span class="text-sm text-gray-400 dark:text-gray-600">|</span>

                <span class="text-sm text-gray-600 dark:text-gray-400">Regex:</span>
                <span
                    :class="!useRegex ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="useRegex = false"
                >
                    Off
                </span>
                <USwitch v-model="useRegex" />
                <span
                    :class="useRegex ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="useRegex = true"
                >
                    On
                </span>

                <UButton
                    color="neutral"
                    variant="ghost"
                    size="xs"
                    icon="i-heroicons-question-mark-circle"
                    :class="useRegex ? '' : 'invisible pointer-events-none'"
                    :aria-hidden="!useRegex"
                    tabindex="-1"
                    @click="$emit('show-help')"
                >
                    Help
                </UButton>

                <span class="text-sm text-gray-400 dark:text-gray-600">|</span>

                <span class="text-sm text-gray-600 dark:text-gray-400">Case sensitive:</span>
                <span
                    :class="!caseSensitive ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="caseSensitive = false"
                >
                    Off
                </span>
                <USwitch v-model="caseSensitive" />
                <span
                    :class="caseSensitive ? 'text-gray-900 dark:text-white underline underline-offset-4' : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="caseSensitive = true"
                >
                    On
                </span>
            </div>

            <div class="flex gap-2">
                <UInput
                    v-model="query"
                    :placeholder="placeholder"
                    class="flex-1"
                    clearable
                    icon="i-heroicons-magnifying-glass"
                    @keydown.enter="$emit('search')"
                    @update:model-value="(value) => { if (!value) $emit('clear') }"
                />
                <UButton
                    :disabled="!query || query.trim().length < 2"
                    color="neutral"
                    icon="i-heroicons-magnifying-glass"
                    variant="outline"
                    @click="$emit('search')"
                >
                    Search
                </UButton>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
const query = defineModel<string>('query', { required: true })
const searchEverything = defineModel<boolean>('searchEverything', { required: true })
const useRegex = defineModel<boolean>('useRegex', { required: true })
const caseSensitive = defineModel<boolean>('caseSensitive', { required: true })

defineProps<{
    placeholder: string
}>()

defineEmits<{
    'search': []
    'clear': []
    'show-help': []
}>()
</script>
