<template>
    <div v-if="translations?.length" class="space-y-1 text-sm">
        <ul class="list-disc space-y-1 pl-4">
            <li v-for="(translation, index) in translations" :key="index">
                {{ translation }}
            </li>
        </ul>
    </div>
</template>

<script lang="ts" setup>
/**
 * Displays a list of translations for a verb example
 */
defineProps<{
    translations: string[]
}>()
</script>
