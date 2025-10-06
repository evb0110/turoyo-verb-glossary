<template>
    <div class="space-y-6 p-6">
        <div class="flex justify-end">
            <UButton icon="i-heroicons-arrow-left-circle" to="/" variant="ghost">
                Back to verb list
            </UButton>
        </div>
        <UCard>
            <template #header>
                <div class="flex flex-col gap-4">
                    <div class="flex flex-wrap items-start justify-between gap-4">
                        <div class="space-y-1">
                            <h1 class="text-3xl font-semibold tracking-tight turoyo-text">
                                {{ verb?.root }}
                            </h1>
                        </div>

                        <div class="flex flex-wrap items-center gap-2">
                            <UBadge v-if="verb?.uncertain" variant="soft">
                                Uncertain
                            </UBadge>
                            <UBadge v-if="verb?.cross_reference" variant="soft">
                                Cross-reference
                            </UBadge>
                        </div>
                    </div>

                    <div v-if="verb?.cross_reference" class="rounded-lg border px-4 py-3 text-sm">
                        See related entry
                        <NuxtLink :to="`/verbs/${rootToSlug(verb.cross_reference)}`" class="font-medium">
                            {{ verb.cross_reference }}
                        </NuxtLink>
                    </div>
                </div>
            </template>

            <div v-if="verb?.etymology?.etymons?.length" class="space-y-3">
                <h2 class="text-xs font-semibold uppercase tracking-wider text-muted">
                    Etymology
                </h2>

                <div v-for="(group, idx) in groupedEtymons" :key="idx" class="space-y-2">
                    <div class="flex items-baseline gap-2">
                        <span class="font-medium text-sm">{{ group.source }}:</span>
                        <span
                            v-if="verb.etymology.relationship && idx > 0"
                            class="text-xs text-muted italic"
                        >
                            ({{ verb.etymology.relationship }})
                        </span>
                    </div>

                    <div v-for="(etymon, eIdx) in group.etymons" :key="eIdx" class="pl-4 space-y-1 text-sm">
                        <div class="flex items-baseline gap-2">
                            <span>{{ etymon.source_root }}</span>
                            <span>{{ etymon.stem }}</span>
                        </div>
                        <p v-if="etymon.meaning" class="text-muted">
                            {{ etymon.meaning }}
                        </p>
                        <p v-if="etymon.reference" class="text-xs text-muted">
                            Ref: {{ etymon.reference }}
                        </p>
                        <p v-if="etymon.raw" class="text-xs text-muted italic">
                            {{ etymon.raw }}
                        </p>
                    </div>
                </div>
            </div>
        </UCard>

        <div class="space-y-4">
            <div class="flex items-center justify-between">
                <h2 class="text-xl font-semibold">
                    Stems
                </h2>
            </div>

            <div class="space-y-4">
                <UCard
                    v-for="item in stemItems"
                    :key="item.stem"
                    :ui="{ body: 'space-y-4' }"
                    class="border border-transparent transition hover:border-primary/40"
                >
                    <template v-if="item.label_gloss_tokens?.length || item.label_raw">
                        <div class="prose max-w-none text-sm">
                            <div class="font-semibold">
                                {{ `${item.stem}: ${item.forms?.length ? item.forms.join('/') : 'No recorded forms'}` }}
                            </div>
                            <div v-if="item.label_gloss_tokens?.length">
                                <span
                                    v-for="(t, i) in item.glossTokens"
                                    :key="i"
                                    :class="{ italic: t.italic }"
                                >
                                    {{ t.text }}
                                </span>
                            </div>
                            <div v-else-if="item.label_raw" v-html="item.label_raw" />
                        </div>
                    </template>
                    <template v-else>
                        <div class="flex flex-wrap items-center justify-between gap-3">
                            <div>
                                <h3 class="text-lg font-semibold">
                                    Stem {{ item.stem }}
                                </h3>
                                <p class="text-sm text-muted">
                                    {{ item.forms.join(', ') || 'No recorded forms' }}
                                </p>
                            </div>
                        </div>
                    </template>

                    <div v-if="item.conjugationGroups.length" class="space-y-4">
                        <div
                            v-for="group in item.conjugationGroups"
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
                                <UCard
                                    v-for="(example, index) in group.examples"
                                    :key="`${group.name}-${index}`"
                                    :ui="{ body: 'space-y-3' }"
                                    class="border-l-4 border-primary/40"
                                    variant="soft"
                                >
                                    <div class="text-lg font-medium turoyo-text">
                                        {{ example.turoyo || '—' }}
                                    </div>

                                    <div v-if="example.translations?.length" class="space-y-1 text-sm">
                                        <ul class="list-disc space-y-1 pl-4">
                                            <li v-for="(translation, tIndex) in example.translations" :key="tIndex">
                                                {{ translation }}
                                            </li>
                                        </ul>
                                    </div>

                                    <div v-if="example.references?.length" class="space-y-1 text-xs">
                                        <div class="flex flex-wrap gap-1">
                                            <UBadge
                                                v-for="(ref, rIndex) in example.references.filter(r => r && r.trim().length)"
                                                :key="rIndex"
                                                variant="soft"
                                            >
                                                {{ ref }}
                                            </UBadge>
                                        </div>
                                    </div>
                                </UCard>
                            </div>
                        </div>
                    </div>
                    <p v-else class="text-sm text-muted">
                        No examples available.
                    </p>
                </UCard>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import type { Etymon } from '~/composables/useVerbs'

const route = useRoute()
const { getVerbWithCrossRef, rootToSlug } = useVerbs()

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
    `verb-${root.value}`,
    () => getVerbWithCrossRef(root.value)
)

if (error.value) {
    throw createError({
        statusCode: 404,
        statusMessage: 'Verb not found'
    })
}

const groupedEtymons = computed(() => {
    if (!verb.value?.etymology?.etymons) return []

    const groups = new Map<string, Etymon[]>()
    for (const etymon of verb.value.etymology.etymons) {
        const source = etymon.source
        if (!groups.has(source)) {
            groups.set(source, [])
        }
        groups.get(source)!.push(etymon)
    }

    return Array.from(groups.entries()).map(([source, etymons]) => ({
        source,
        etymons
    }))
})

const stemItems = computed(() => {
    if (!verb.value) return []

    return verb.value.stems.map((stem) => {
        const conjugationGroups = Object.entries(stem.conjugations || {}).map(([name, examples]) => ({
            name,
            examples
        }))

        interface GlossToken {
            italic: boolean
            text: string
        }

        return {
            ...stem,
            exampleCount: conjugationGroups.reduce((count, group) => count + group.examples.length, 0),
            conjugationGroups,
            glossTokens: Array.isArray(stem.label_gloss_tokens)
                ? stem.label_gloss_tokens.filter((t: GlossToken, idx: number, arr: GlossToken[]) => {
                        const first = arr[0]?.text?.trim?.() || ''
                        if (idx === 0 && /^[IVX]+\s*:/.test(first)) return false
                        return true
                    })
                : []
        }
    })
})

useHead({
    title: () => (verb.value ? `${verb.value.root}` : undefined),
    meta: [
        {
            name: 'description',
            content: verb.value?.etymology?.meaning || 'Detailed view of a Turoyo verb'
        }
    ]
})
</script>
