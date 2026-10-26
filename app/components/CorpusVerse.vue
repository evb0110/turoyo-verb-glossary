<template>
    <div :id="`verse-${verse.v}`" class="verse" :class="{ target: selected }">
        <NuxtLink
            :to="{ query: { v: verse.v } }"
            replace
            class="verse-n"
            :aria-label="`Verse ${verse.v}`"
            :aria-current="selected ? 'location' : undefined"
        >
            <span v-text="verse.v"></span>
        </NuxtLink>
        <p class="tur verse-tur">
            <template v-for="(segment, i) in segments" :key="i">
                <button
                    v-if="segment.occurrence"
                    type="button"
                    class="verb"
                    :aria-expanded="active?.token === token(i)"
                    :aria-controls="`verb-${verse.v}`"
                    @click="toggle(i, segment.occurrence)"
                    v-text="segment.text"
                ></button>
                <span v-else v-text="segment.text"></span>
            </template>
        </p>
        <div class="verse-tr">
            <p v-if="verse.tr">
                {{ verse.tr }}
            </p>
            <p v-else class="muted small">
                No translation.
            </p>
            <p v-for="(flag, i) in flags" :key="i" class="small muted">
                Translation note: {{ flag.note }}
            </p>
        </div>
        <div
            v-if="verb"
            :id="`verb-${verse.v}`"
            class="verb-panel"
            role="region"
            :aria-label="`Analysis of ${verb.form}`"
        >
            <p>
                <span class="tur">{{ verb.form }}</span>
                <strong class="serif root">{{ verb.root }}</strong>
                <span class="muted">
                    Stem {{ verb.stem }}{{ verb.detransitive ? ", detransitive" : "" }} · {{ verb.box }} ·
                    meaning {{ verb.sense }}
                </span>
            </p>
            <p>{{ verb.meaning }}</p>
            <p v-if="verb.arguments" class="small muted">
                {{ verb.arguments }}
            </p>
            <p v-if="verb.note" class="small muted">
                {{ verb.note }}
            </p>
            <p class="verb-links small">
                <NuxtLink
                    v-if="verb.entryId"
                    :to="entryHref(verb.entryId, `${verb.entryId}.${verb.stem}`, verb.sense)"
                >
                    Open the entry {{ verb.root }}
                </NuxtLink>
                <span v-else class="muted">This verb is not in the glossary yet.</span>
                <span v-if="verb.proposalIds.length" class="suggestions">
                    {{ verb.proposalIds.length === 1 ? "Suggestion from this verse:" : "Suggestions from this verse:" }}
                    <NuxtLink
                        v-for="(id, n) in verb.proposalIds"
                        :key="id"
                        :to="{ path: '/review', query: { proposal: id } }"
                        :aria-label="`Review suggestion ${n + 1} from this verse`"
                    >
                        <span v-text="verb.proposalIds.length === 1 ? 'review' : n + 1"></span>
                    </NuxtLink>
                </span>
                <button type="button" class="btn-link" @click="active = null">
                    Close
                </button>
            </p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { occurrenceSegments } from '~/utils/occurrenceSegments'
import type { IAlignment } from '#shared/types/IAlignment'
import type { IOccurrence } from '#shared/types/IOccurrence'
import type { IVerse } from '#shared/types/IVerse'
import { entryHref } from '#shared/utils/entryHref'

const props = defineProps<{
    verse: IVerse
    occurrences: IOccurrence[]
    flags: IAlignment[]
    selected: boolean
}>()
const segments = computed(() => occurrenceSegments(props.verse.tur, props.occurrences))
const { selected: active } = useReaderVerb()
function token(i: number) {
    return `${props.verse.v}-${i}`
}
const verb = computed(() => (active.value?.token.startsWith(`${props.verse.v}-`) ? active.value.verb : null))
function toggle(i: number, occurrence: IOccurrence) {
    active.value = active.value?.token === token(i)
        ? null
        : {
                verb: occurrence,
                token: token(i),
            }
}
</script>

<style scoped>
.verse {
  display: grid;
  grid-template-columns: 3rem minmax(0, 1.1fr) minmax(0, 1fr);
  gap: 0 1.5rem;
  padding: 0.3rem 0.5rem 0.3rem 0;
  border-top: 1px solid var(--rule);
}
.target {
  background: var(--target);
  box-shadow: inset 3px 0 var(--accent);
}
.verse-n {
  padding-top: 0.15rem;
  color: var(--muted);
  font-size: 0.8125rem;
  font-variant-numeric: tabular-nums;
  text-align: right;
  text-decoration: none;
}
.verse-n:hover,
.target .verse-n {
  color: var(--accent);
  text-decoration: underline;
}
.verse-tr {
  font-size: 0.9375rem;
}
.verb {
  color: var(--accent);
  text-decoration: underline dotted;
  text-decoration-thickness: 1px;
  text-underline-offset: 0.2em;
}
.verb:hover,
.verb[aria-expanded="true"] {
  text-decoration-style: solid;
}
.verb[aria-expanded="true"] {
  background: color-mix(in srgb, var(--accent) 15%, transparent);
}
.verb-panel {
  display: grid;
  grid-column: 2 / -1;
  gap: 0.15rem;
  margin: 0.35rem 0 0.2rem;
  padding: 0.4rem 0.75rem;
  border-left: 3px solid var(--accent);
  background: var(--bg-soft);
}
.verb-panel .root {
  margin: 0 0.5rem;
}
.suggestions {
  display: inline-flex;
  gap: 0.5rem;
}
.verb-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0 1rem;
}
@media (max-width: 760px) {
  .verse {
    grid-template-columns: 2rem minmax(0, 1fr);
    gap: 0 0.6rem;
  }
  .verse-tr,
  .verb-panel {
    grid-column: 2;
  }
}
</style>
