<template>
    <article :id="`verse-${verse.v}`" class="verse" :class="{ 'verse-selected': selected }">
        <NuxtLink :to="`?v=${verse.v}`" class="verse-number" :aria-label="`Verse ${verse.v}`">
            {{ verse.v }}
        </NuxtLink>
        <div class="verse-turoyo turoyo">
            <template v-for="(segment, i) in segments" :key="i">
                <span
                    v-if="segment.occurrence"
                    class="occurrence-wrap"
                    :class="{ 'occurrence-open': expanded === i }"
                    @mouseenter="!touch && (expanded = i)"
                    @focusin="!touch && (expanded = i)"
                >
                    <NuxtLink
                        v-if="segment.occurrence.entryId"
                        :to="
                            entryHref(
                                segment.occurrence.entryId,
                                `${segment.occurrence.entryId}.${segment.occurrence.stem}`,
                                segment.occurrence.sense
                            )
                        "
                        class="occurrence"
                        :class="{
                            suggested: segment.occurrence.decision === 'add',
                            proposed: segment.occurrence.proposalIds.length > 0
                        }"
                        :aria-describedby="`occ-${verse.v}-${i}`"
                        @click.capture="onToken($event, i)"
                    >
                        {{ segment.text }}
                    </NuxtLink>
                    <button
                        v-else
                        class="occurrence"
                        :class="{
                            suggested: segment.occurrence.decision === 'add',
                            proposed: segment.occurrence.proposalIds.length > 0
                        }"
                        :aria-expanded="expanded === i"
                        @click="expanded = expanded === i ? -1 : i"
                    >
                        {{ segment.text }}
                    </button>
                    <span :id="`occ-${verse.v}-${i}`" class="occurrence-tooltip">
                        <strong>
                            {{ segment.occurrence.root }} · Stem
                            {{ segment.occurrence.stem }}
                        </strong>
                        <span>
                            {{ segment.occurrence.detransitive ? 'Detransitive · ' : ''
                            }}{{ segment.occurrence.box }} · Sense
                            {{ segment.occurrence.sense }}
                        </span>
                        <span>{{ segment.occurrence.meaning }}</span>
                        <span
                            v-if="segment.occurrence.decision === 'add'"
                            class="suggestion-label"
                        >Reader suggested adding this occurrence.</span>
                        <span v-if="segment.occurrence.note">
                            <strong>Reader note:</strong> {{ segment.occurrence.note }}
                        </span>
                        <span v-if="segment.occurrence.newSenseGloss"><strong>New sense:</strong>
                            {{ segment.occurrence.newSenseGloss }}</span>
                        <span v-if="segment.occurrence.newSenseType"><strong>Sense type:</strong>
                            {{ segment.occurrence.newSenseType }}</span>
                        <span v-if="segment.occurrence.observations">{{
                            segment.occurrence.observations
                        }}</span>
                        <NuxtLink
                            v-for="proposalId in segment.occurrence.proposalIds"
                            :key="proposalId"
                            :to="`/review?proposal=${encodeURIComponent(proposalId)}`"
                        >Open proposal {{ proposalId }} ↗</NuxtLink>
                        <NuxtLink
                            v-if="segment.occurrence.entryId"
                            :to="
                                entryHref(
                                    segment.occurrence.entryId,
                                    `${segment.occurrence.entryId}.${segment.occurrence.stem}`,
                                    segment.occurrence.sense
                                )
                            "
                        >
                            Open entry ↗
                        </NuxtLink>
                        <button class="quiet" @click="expanded = -1">Close</button>
                    </span>
                </span>
                <template v-else>
                    {{ segment.text }}
                </template>
            </template>
        </div>
        <p class="verse-translation" :class="{ muted: !verse.tr }">
            {{ verse.tr || 'No translation available.' }}
        </p>
        <div v-for="(flag, i) in flags" :key="i" class="alignment-flag">
            <span class="pill">Alignment · {{ flag.status }}</span>
            {{ flag.note }}
        </div>
    </article>
</template>

<script setup lang="ts">
import { useMediaQuery } from '@vueuse/core'
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
const route = useRoute()
const activeOccurrence = useState('reader-active-occurrence', () => '')
const occurrenceKey = computed(() => `${String(route.params.id)}:${props.verse.v}:`)
const expanded = computed({
    get: () => activeOccurrence.value.startsWith(occurrenceKey.value)
        ? Number(activeOccurrence.value.slice(occurrenceKey.value.length))
        : -1,
    set: (index: number) => { activeOccurrence.value = index < 0 ? '' : `${occurrenceKey.value}${index}` },
})
const touch = useMediaQuery('(hover: none)')
function onToken(event: MouseEvent, i: number) {
    if (touch.value && expanded.value !== i) {
        event.preventDefault()
        expanded.value = i
    }
}
</script>

<style scoped>
.verse {
    display: grid;
    grid-template-columns: 2rem minmax(0, 1fr) minmax(0, 1fr);
    gap: 1.5rem;
    padding: 1.5rem 1rem;
    border-bottom: 1px solid var(--rule);
}
.verse-selected {
    background: var(--panel);
    box-shadow: inset 3px 0 var(--accent);
}
.verse-number {
    color: var(--muted);
    font-size: 0.7rem;
    font-family: var(--font-sans);
    text-decoration: none;
}
.verse-turoyo {
    font-size: 1.3rem;
    line-height: 1.8;
    overflow-wrap: anywhere;
}
.verse-translation {
    font-family: var(--font-serif);
    font-size: 1.15rem;
    line-height: 1.8;
    overflow-wrap: anywhere;
}
.occurrence-wrap {
    position: relative;
}
.occurrence {
    color: var(--accent);
    background: color-mix(in srgb, var(--accent) 10%, transparent);
    border-bottom: 1px solid var(--accent);
    text-decoration: none;
}
.occurrence.suggested {
    color: var(--correction);
    background: color-mix(in srgb, var(--correction) 10%, transparent);
    border-bottom: 1px dashed var(--correction);
}
.occurrence.proposed {
    color: var(--note);
    background: color-mix(in srgb, var(--note) 10%, transparent);
    border-bottom: 3px double var(--note);
}
.occurrence-tooltip {
    display: none;
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    width: min(350px, calc(100vw - 2rem));
    max-height: 55vh;
    overflow: auto;
    z-index: 12;
    background: var(--paper);
    color: var(--ink);
    padding: 0.8rem;
    border: 1px solid var(--rule);
    box-shadow: 0 5px 24px #0002;
    font-family: var(--font-sans);
    font-size: 0.72rem;
    font-style: normal;
    line-height: 1.6;
}
.occurrence-open .occurrence-tooltip {
    display: grid;
    gap: 0.3rem;
}
.alignment-flag {
    grid-column: 2 / -1;
    font-size: 0.7rem;
    color: var(--correction);
}
@media (max-width: 680px) {
    .verse {
        grid-template-columns: 1.4rem minmax(0, 1fr);
        gap: 0.5rem 0.7rem;
        padding: 1.2rem 0.5rem;
    }
    .verse-translation {
        grid-column: 2;
        padding-top: 0.5rem;
        color: var(--muted);
    }
}
</style>
