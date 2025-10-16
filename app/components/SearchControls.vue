<script setup lang="ts">
const query = defineModel<string>('query', { required: true })
const searchEverything = defineModel<boolean>('searchEverything', { required: true })
const useRegex = defineModel<boolean>('useRegex', { required: true })
const caseSensitive = defineModel<boolean>('caseSensitive', { required: true })

const internalQuery = ref(query.value)

watch(query, (newValue) => {
    internalQuery.value = newValue
})

defineProps<{
    placeholder: string
}>()

const emit = defineEmits<{
    'search': []
    'clear': []
    'show-help': []
}>()

const isCharPickerOpen = ref(false)
const searchInput = ref<{ $el?: { querySelector: (selector: string) => HTMLInputElement | null } } | null>(null)

function insertChar(char: string) {
    const input = searchInput.value?.$el?.querySelector('input')
    if (!input) {
        internalQuery.value += char
        return
    }

    const start = input.selectionStart ?? internalQuery.value.length
    const end = input.selectionEnd ?? internalQuery.value.length
    const text = internalQuery.value

    internalQuery.value = text.slice(0, start) + char + text.slice(end)

    nextTick(() => {
        const newPosition = start + char.length
        input.setSelectionRange(newPosition, newPosition)
    })
}

function handleSearch() {
    query.value = internalQuery.value
    isCharPickerOpen.value = false
    emit('search')
}
</script>

<template>
    <div class="space-y-4">
        <div class="flex flex-col gap-3">
            <div class="flex items-center gap-3 flex-wrap">
                <span class="text-sm text-gray-600 dark:text-gray-400">Search type:</span>
                <span
                    :class="!searchEverything
                        ? 'text-gray-900 dark:text-white underline underline-offset-4'
                        : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="searchEverything = false"
                >
                    Roots only
                </span>
                <USwitch v-model="searchEverything"/>
                <span
                    :class="searchEverything
                        ? 'text-gray-900 dark:text-white underline underline-offset-4'
                        : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="searchEverything = true"
                >
                    Everything
                </span>

                <span class="text-sm text-gray-400 dark:text-gray-600">|</span>

                <span class="text-sm text-gray-600 dark:text-gray-400">Regex:</span>
                <span
                    :class="!useRegex
                        ? 'text-gray-900 dark:text-white underline underline-offset-4'
                        : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="useRegex = false"
                >
                    Off
                </span>
                <USwitch v-model="useRegex"/>
                <span
                    :class="useRegex
                        ? 'text-gray-900 dark:text-white underline underline-offset-4'
                        : 'text-gray-500 dark:text-gray-500'"
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
                    :class="!caseSensitive
                        ? 'text-gray-900 dark:text-white underline underline-offset-4'
                        : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="caseSensitive = false"
                >
                    Off
                </span>
                <USwitch v-model="caseSensitive"/>
                <span
                    :class="caseSensitive
                        ? 'text-gray-900 dark:text-white underline underline-offset-4'
                        : 'text-gray-500 dark:text-gray-500'"
                    class="text-sm cursor-pointer transition-all"
                    @click="caseSensitive = true"
                >
                    On
                </span>
            </div>

            <div class="flex gap-3">
                <UInput
                    ref="searchInput"
                    v-model="internalQuery"
                    :placeholder="placeholder"
                    class="flex-1 text-base"
                    size="lg"
                    icon="i-heroicons-magnifying-glass"
                    @keydown.enter="handleSearch"
                >
                    <template v-if="internalQuery" #trailing>
                        <UButton
                            color="neutral"
                            variant="link"
                            size="xs"
                            icon="i-heroicons-x-mark"
                            aria-label="Clear search"
                            @click="internalQuery = ''"
                        />
                    </template>
                </UInput>
                <UButton
                    :disabled="!internalQuery || internalQuery.trim().length < 2"
                    color="primary"
                    icon="i-heroicons-magnifying-glass"
                    size="lg"
                    variant="solid"
                    @click="handleSearch"
                >
                    Search
                </UButton>

                <CharacterPicker
                    v-model:open="isCharPickerOpen"
                    @select="insertChar"
                />
            </div>
        </div>
    </div>
</template>
