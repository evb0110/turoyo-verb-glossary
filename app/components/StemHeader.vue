<script lang="ts" setup>
import type { ITransformedStem } from '~/types/ITransformedStem'

defineProps<{
    stem: ITransformedStem
}>()
</script>

<template>
    <template v-if="stem.hasGlossInfo">
        <StemGlossInfo :stem="stem"/>
    </template>
    <template v-else>
        <div class="flex flex-wrap items-baseline gap-5">
            <h3 class="text-lg font-semibold">
                Stem {{ stem.stem }}
            </h3>
            <p>
                {{ stem.formsListDisplay }}
            </p>
        </div>
    </template>
</template>
