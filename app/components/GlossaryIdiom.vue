<template>
    <article :id="idiom.id" class="idiom">
        <p class="idiom-text serif">
            <template v-for="(token, i) in tokens" :key="i">
                <strong
                    v-if="token.kind === 'headword'"
                    class="idiom-headword"
                >{{ token.text }}
                </strong>
                <button
                    v-else-if="token.kind === 'ref'"
                    class="verse-ref"
                    @click="open(token.textId!, token.verse!, token.text)"
                >
                    {{ token.text }}
                </button>
                <span v-else :class="token.kind">{{ token.text }}</span>
            </template>
        </p>
        <details class="idiom-raw">
            <summary>Original text</summary>
            <p>{{ idiom.raw }}</p>
        </details>
    </article>
</template>

<script setup lang="ts">
import { idiomTokens } from '~/utils/idiomTokens'
import type { IIdiom } from '#shared/types/IIdiom'

const props = defineProps<{ idiom: IIdiom
    textIds: string[] }>()
const tokens = computed(() => idiomTokens(props.idiom.raw, new Set(props.textIds)))
const { open } = useEvidence()
</script>

<style scoped>
.idiom {
    margin: 1.3rem 0;
}
.idiom-text {
    font-size: 1.2rem;
    line-height: 1.8;
    white-space: pre-wrap;
}
.idiom-headword {
    font-style: italic;
    font-weight: 600;
}
.turoyo {
    font-size: inherit;
}
.translation,
.annotation {
    font-style: normal;
}
.annotation {
    color: var(--muted);
}
.verse-ref {
    color: var(--accent);
    text-decoration: underline;
    font-size: 1rem;
    font-family: var(--font-sans);
}
.idiom-raw {
    color: var(--muted);
    font-size: .889rem;
    margin-top: 0.3rem;
}
.idiom-raw summary {
    cursor: pointer;
}
.idiom-raw p {
    white-space: pre-wrap;
    margin-top: 0.4rem;
}
</style>
