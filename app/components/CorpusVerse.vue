<template>
    <article
        :id="`verse-${verse.v}`"
        class="verse"
        :class="{ 'verse-selected': selected }"
    >
        <NuxtLink
            :to="`?v=${verse.v}`"
            class="verse-number"
            :aria-label="`Verse ${verse.v}`"
        >{{ verse.v }}</NuxtLink>
        <div class="verse-text stack">
            <p class="verse-turoyo turoyo">
                <template v-for="(segment, i) in segments" :key="i">
                    <button
                        v-if="segment.occurrence"
                        class="analysed-verb"
                        :aria-expanded="selectedVerb?.token === `${verse.v}-${i}`"
                        aria-haspopup="dialog"
                        @click="
                            selectedVerb = {
                                verb: segment.occurrence,
                                token: `${verse.v}-${i}`
                            }
                        "
                    >
                        {{ segment.text }}
                    </button><template v-else>
                        {{ segment.text }}
                    </template>
                </template>
            </p>
            <p class="verse-translation serif">
                {{ verse.tr || "No translation available." }}
            </p>
            <details v-if="flags.length" class="translation-note">
                <summary>Note on this translation</summary>
                <p v-for="(flag, i) in flags" :key="i">
                    {{ flag.note }}
                </p>
            </details>
        </div>
    </article>
</template>

<script setup lang="ts">
import { occurrenceSegments } from '~/utils/occurrenceSegments'
import type { IAlignment } from '#shared/types/IAlignment'
import type { IOccurrence } from '#shared/types/IOccurrence'
import type { IVerse } from '#shared/types/IVerse'

const props = defineProps<{
    verse: IVerse
    occurrences: IOccurrence[]
    flags: IAlignment[]
    selected: boolean
}>()
const segments = computed(() =>
    occurrenceSegments(props.verse.tur, props.occurrences)
)
const { selected: selectedVerb } = useReaderVerb()
</script>

<style scoped>
.verse {
  display: grid;
  grid-template-columns: 2rem minmax(0, 1fr);
  gap: 0.7rem;
  padding: 1.5rem 0.4rem;
  border-bottom: 1px solid var(--rule);
}
.verse-selected {
  background: var(--panel);
  box-shadow: inset 3px 0 var(--accent);
}
.verse-number {
  font-size: 0.889rem;
  min-height: 48px;
  display: flex;
  align-items: center;
  text-decoration: none;
}
.verse-text {
  gap: 0.6rem;
}
.verse-turoyo {
  font-size: 1.4rem;
  line-height: 1.8;
}
.verse-translation {
  font-size: 1.2rem;
}
.analysed-verb {
  display: inline-block;
  min-width: 48px;
  min-height: 48px;
  color: var(--accent);
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 0.18em;
  font: inherit;
  padding: 0 0.1rem;
}
.analysed-verb[aria-expanded="true"] {
  background: var(--panel);
}
.translation-note {
  color: var(--muted);
}
</style>
