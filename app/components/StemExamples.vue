<script lang="ts" setup>
import type { ITransformedStem } from '~/types/ITransformedStem'

defineProps<{
    stem: ITransformedStem
}>()
</script>

<template>
    <div v-if="stem.hasExamples" class="space-y-4">
        <div
            v-for="group in stem.conjugationGroups"
            :key="group.name"
            class="space-y-3"
        >
            <div class="flex items-center gap-2">
                <UIcon class="h-4 w-4" name="i-heroicons-book-open"/>
                <h4 class="font-medium">
                    {{ group.name }}
                </h4>
            </div>

            <div class="grid gap-3">
                <VerbExample
                    v-for="(example, index) in group.examples"
                    :key="`${group.name}-${index}`"
                    :example="example"
                />
            </div>
        </div>
    </div>
    <p v-else class="text-sm text-muted">
        No examples available.
    </p>
</template>
