<template>
    <UCard
        :ui="{ body: 'space-y-3' }"
        class="border-l-4 border-primary/40"
        variant="soft"
    >
        <div class="text-lg font-medium turoyo-text">
            {{ example.turoyo || '—' }}
        </div>

        <VerbTranslationList :translations="example.translations" />

        <VerbReferenceBadges :references="example.references" />
    </UCard>
</template>

<script lang="ts" setup>
import type { Example } from '~/types/verb'

defineProps<{
    example: Example
}>()
</script>
