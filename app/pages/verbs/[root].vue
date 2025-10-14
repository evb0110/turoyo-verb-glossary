<template>
    <div class="space-y-6 p-6">
        <div class="flex justify-end">
            <UButton icon="i-heroicons-arrow-left-circle" :to="toBack" variant="ghost">
                Back to verb list
            </UButton>
        </div>

        <UCard>
            <template #header>
                <VerbHeader :verb="verb!" />
            </template>

            <VerbEtymology :etymology="verb?.etymology ?? null" />
        </UCard>

        <div class="space-y-4">
            <div class="flex items-center justify-between">
                <h2 class="text-xl font-semibold">
                    Stems
                </h2>
            </div>

            <div class="space-y-4">
                <VerbStemCard
                    v-for="stem in verb?.stems"
                    :key="stem.stem"
                    :stem="stem"
                />
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
/**
 * Verb detail page
 * Displays a single verb with etymology, stems, conjugations, and examples
 */
import type { Verb } from '~/types/verb'
import { slugToRoot } from '~/utils/slugify'

const route = useRoute()

const toBack = computed(() => {
    return {
        path: '/',
        query: route.query
    }
})

const root = computed(() => {
    const raw = route.params.root as string
    try {
        return decodeURIComponent(raw)
    }
    catch {
        return raw
    }
})

const { data: verb, error } = await useAsyncData(
    () => `verb-${root.value}`,
    () => {
        const decodedRoot = slugToRoot(root.value)
        const encodedRoot = encodeURIComponent(decodedRoot)
        return $fetch<Verb>(`/api/verbs/${encodedRoot}`)
    }
)

if (error.value) {
    throw createError({
        statusCode: 404,
        statusMessage: 'Verb not found'
    })
}

useHead({
    title: () => (verb.value ? `${verb.value.root}` : undefined),
    meta: [
        {
            name: 'description',
            content: verb.value?.etymology?.etymons?.[0]?.meaning || 'Detailed view of a Turoyo verb'
        }
    ]
})
</script>
