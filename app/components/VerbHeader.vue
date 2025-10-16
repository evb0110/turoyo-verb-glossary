<template>
    <div class="flex flex-col gap-4">
        <div class="flex flex-wrap items-start justify-between gap-4">
            <div class="space-y-1">
                <h1 class="text-3xl font-semibold tracking-tight turoyo-text">
                    {{ verb.root }}
                </h1>
            </div>

            <div class="flex flex-wrap items-center gap-2">
                <UBadge v-if="verb.uncertain" variant="soft">
                    Uncertain
                </UBadge>
                <UBadge v-if="verb.cross_reference" variant="soft">
                    Cross-reference
                </UBadge>
            </div>
        </div>

        <div v-if="verb.cross_reference" class="rounded-lg border px-4 py-3 text-sm">
            See related entry
            <NuxtLink :to="`/verbs/${rootToSlug(verb.cross_reference)}`" class="font-medium">
                {{ verb.cross_reference }}
            </NuxtLink>
        </div>
    </div>
</template>

<script lang="ts" setup>
import type { IVerb } from '~/types/IVerb'
import { rootToSlug } from '~/utils/rootToSlug'

defineProps<{
    verb: IVerb
}>()
</script>
