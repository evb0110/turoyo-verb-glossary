<script lang="ts" setup>
import type { IStructuredExample } from '~/types/IStructuredExample'

defineProps<{
    structured: IStructuredExample
}>()
</script>

<template>
    <UCard :ui="{ body: 'space-y-3' }" class="border-l-4 border-primary/40" variant="soft">
        <div class="text-lg leading-relaxed">
            <div v-if="structured && structured.items && structured.items.length">
                <div v-if="structured.number" class="text-xl text-bold">
                    {{ structured.number }}
                </div>
                <div
                    v-for="(item, idx) in structured.items"
                    :key="idx"
                    class="[:not(:last-child)]:mb-4"
                >
                    <div class="turoyo-text">
                        {{ item.turoyo }}
                    </div>
                    <div v-if="item.translation" class="text-foreground">
                        {{ item.translation }}
                    </div>
                    <div v-if="item.references && item.references.length" class="text-sm align-middle">
                        {{ item.references.join('; ') }}
                    </div>
                </div>
            </div>
            <template v-else>
                <span class="turoyo-text">—</span>
            </template>
        </div>
    </UCard>
</template>

<style scoped lang="scss">
.structured-item:not(:first-child):not(:last-child) {
    //margin-bottom: 16px;
}
</style>
