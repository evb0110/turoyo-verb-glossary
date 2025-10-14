<template>
    <div v-if="etymology?.etymons?.length" class="space-y-3">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-muted">
            Etymology
        </h2>

        <div v-for="(group, idx) in groupedEtymons" :key="idx" class="space-y-2">
            <div v-if="group.source" class="flex items-baseline gap-2">
                <span class="font-medium text-sm">{{ group.source }}:</span>
                <span
                    v-if="etymology.relationship && idx > 0"
                    class="text-xs text-muted italic"
                >
                    ({{ etymology.relationship }})
                </span>
            </div>

            <div
                v-for="(etymon, eIdx) in group.etymons"
                :key="eIdx"
                :class="group.source ? 'pl-4' : ''"
                class="space-y-1 text-sm"
            >
                <div v-if="etymon.source_root || etymon.stem" class="flex items-baseline gap-2">
                    <span v-if="etymon.source_root">{{ etymon.source_root }}</span>
                    <span v-if="etymon.stem">{{ etymon.stem }}</span>
                </div>
                <p v-if="etymon.meaning" class="text-muted">
                    {{ etymon.meaning }}
                </p>
                <p v-if="etymon.reference" class="text-xs text-muted">
                    Ref: {{ etymon.reference }}
                </p>
                <p v-if="etymon.raw" class="text-muted italic">
                    {{ etymon.raw }}
                </p>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import type { Etymology, Etymon } from '~/types/verb'

const props = defineProps<{
    etymology: Etymology | null | undefined
}>()

const groupedEtymons = computed(() => {
    if (!props.etymology?.etymons) return []

    const groups = new Map<string | undefined, Etymon[]>()
    for (const etymon of props.etymology.etymons) {
        const source = etymon.source || undefined
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
</script>
