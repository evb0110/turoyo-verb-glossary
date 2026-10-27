<template>
    <p :id="idiom.id" class="idiom serif">
        <template v-for="(token, i) in tokens" :key="i">
            <strong v-if="token.kind === 'headword'" class="headword">{{ token.text }}</strong>
            <NuxtLink
                v-else-if="token.kind === 'ref'"
                class="ref"
                :to="verseHref(token.textId!, token.verse!)"
            >{{ token.text }}</NuxtLink>
            <span v-else :class="token.kind">{{ token.text }}</span>
        </template>
    </p>
</template>

<script setup lang="ts">
import { verseHref } from '~/utils/verseHref'
import type { IIdiom } from '#shared/types/IIdiom'
import { idiomTokens } from '#shared/utils/idiomTokens'

const props = defineProps<{ idiom: IIdiom
    textIds: string[] }>()
const tokens = computed(() => idiomTokens(props.idiom.raw, new Set(props.textIds)))
</script>

<style scoped>
.idiom {
  padding: 0.3rem 0;
  border-top: 1px solid var(--rule);
  font-size: 1.0625rem;
  white-space: pre-wrap;
}
.headword,
.turoyo {
  font-style: italic;
}
.headword {
  font-weight: 700;
}
.annotation {
  color: var(--muted);
}
.ref {
  font-family: var(--font-sans);
  font-size: 0.875rem;
}
</style>
