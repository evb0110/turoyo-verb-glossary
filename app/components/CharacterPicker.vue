<template>
    <UPopover v-model:open="isOpen">
        <UButton
            color="primary"
            variant="soft"
            size="lg"
            icon="i-heroicons-language"
        >
            Virtual keyboard
        </UButton>

        <template #content>
            <div class="p-4 space-y-3 w-80">
                <div class="flex items-center justify-between">
                    <h3 class="text-sm font-medium text-gray-900 dark:text-white">
                        Special Characters
                    </h3>
                    <UButton
                        color="neutral"
                        variant="ghost"
                        size="xs"
                        icon="i-heroicons-x-mark"
                        aria-label="Close"
                        @click="isOpen = false"
                    />
                </div>

                <div>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
                        Turoyo
                    </p>
                    <div class="flex flex-wrap gap-1">
                        <UButton
                            v-for="char in turoyoChars"
                            :key="char"
                            size="sm"
                            variant="outline"
                            color="neutral"
                            @click.stop="handleCharClick(char)"
                        >
                            {{ char }}
                        </UButton>
                    </div>
                </div>

                <div>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
                        German
                    </p>
                    <div class="flex flex-wrap gap-1">
                        <UButton
                            v-for="char in germanChars"
                            :key="char"
                            size="sm"
                            variant="outline"
                            color="neutral"
                            @click.stop="handleCharClick(char)"
                        >
                            {{ char }}
                        </UButton>
                    </div>
                </div>
            </div>
        </template>
    </UPopover>
</template>

<script setup lang="ts">
const isOpen = defineModel<boolean>('open', { default: false })

const emit = defineEmits<{
    select: [char: string]
}>()

const turoyoChars = ['ʔ', 'ʕ', 'č', 'ḏ', 'ə', 'ġ', 'ǧ', 'ḥ', 'ṣ', 'š', 'ṭ', 'ṯ', 'ž']
const germanChars = ['ä', 'ö', 'ü', 'ß']

function handleCharClick(char: string) {
    emit('select', char)
}
</script>
