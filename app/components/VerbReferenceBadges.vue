<template>
    <div v-if="references?.length" class="space-y-1 text-xs">
        <div class="flex flex-wrap gap-1">
            <UBadge
                v-for="(ref, index) in filteredReferences"
                :key="index"
                variant="soft"
            >
                {{ ref }}
            </UBadge>
        </div>
    </div>
</template>

<script lang="ts" setup>
/**
 * Displays reference badges for a verb example
 * Filters out empty or whitespace-only references
 */
const props = defineProps<{
    references: string[]
}>()

const filteredReferences = computed(() =>
    props.references.filter(r => r && r.trim().length)
)
</script>
