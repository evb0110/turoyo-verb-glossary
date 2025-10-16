<template>
    <UCard
        :ui="{ body: 'space-y-4' }"
        class="border border-transparent transition hover:border-primary/40"
    >
        <template v-if="transformedStem.label_gloss_tokens?.length || transformedStem.label_raw">
            <div class="prose max-w-none text-sm">
                <div class="font-semibold">
                    {{ `${transformedStem.stem}: ${transformedStem.forms?.length ? transformedStem.forms.join('/') : 'No recorded forms'}` }}
                </div>
                <div v-if="transformedStem.label_gloss_tokens?.length">
                    <span
                        v-for="(t, i) in transformedStem.glossTokens"
                        :key="i"
                        :class="{ italic: t.italic }"
                    >
                        {{ t.text }}
                    </span>
                </div>
                <div v-else-if="transformedStem.label_raw" v-html="transformedStem.label_raw" />
            </div>
        </template>
        <template v-else>
            <div class="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <h3 class="text-lg font-semibold">
                        Stem {{ transformedStem.stem }}
                    </h3>
                    <p class="text-sm text-muted">
                        {{ transformedStem.forms.join(', ') || 'No recorded forms' }}
                    </p>
                </div>
            </div>
        </template>

        <div v-if="transformedStem.conjugationGroups.length" class="space-y-4">
            <div
                v-for="group in transformedStem.conjugationGroups"
                :key="group.name"
                class="space-y-3"
            >
                <div class="flex items-center gap-2">
                    <UIcon class="h-4 w-4" name="i-heroicons-book-open" />
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
    </UCard>
</template>

<script lang="ts" setup>
import type { IStem } from '~/types/IStem'
import { transformStemForDisplay } from '~/utils/transformStemForDisplay'

const props = defineProps<{
    stem: IStem
}>()

const transformedStem = computed(() => transformStemForDisplay(props.stem))
</script>
