<template>
    <div v-if="data" class="entry-page">
        <div class="entry-crumb">
            <NuxtLink to="/">Glossary</NuxtLink>
            <span>/</span>
            <span>{{ rootLabel }}</span>
            <span class="muted source">
                {{ entry?.source.volume || 'Proposed entry' }}
            </span>
        </div>
        <header class="entry-heading">
            <p class="eyebrow">
                {{ entry ? 'Dictionary entry' : 'Proposed new root' }}
            </p>
            <h1>{{ rootLabel }}</h1>
            <p v-if="entry" class="entry-head serif">
                {{ entry.head }}
            </p>
            <div v-if="entry?.crossRefs.length" class="row cross-refs">
                <span class="eyebrow">See also</span>
                <NuxtLink v-for="ref in entry.crossRefs" :key="ref" :to="entryHref(ref)">
                    {{ ref.replaceAll('-', ' ') }} ↗
                </NuxtLink>
            </div>
        </header>
        <div v-if="entry" class="entry-controls">
            <div>
                <p class="eyebrow control-label">
                    Layers
                </p>
                <div class="segmented">
                    <button
                        v-for="item in layers"
                        :key="item.value"
                        :aria-pressed="layer === item.value"
                        @click="layer = item.value"
                    >
                        {{ item.label }}
                    </button>
                </div>
            </div>
            <div>
                <p class="eyebrow control-label">
                    Examples
                </p>
                <div class="segmented">
                    <button :aria-pressed="view === 'sense'" @click="view = 'sense'">
                        By sense
                    </button>
                    <button :aria-pressed="view === 'box'" @click="view = 'box'">
                        As in the glossary
                    </button>
                </div>
            </div>
        </div>
        <p v-if="reviewError" class="error" role="alert">
            {{ reviewError }}
        </p>
        <div v-if="layer !== 'glossary'" class="proposal-legend">
            <span class="addition">● Additions</span>
            <span class="correction">● Corrections</span>
            <span class="note">● Notes & questions</span>
            <span>
                {{ data.proposals.length }} proposals · accepting records a decision; source text
                stays visible
            </span>
        </div>
        <p v-if="!entry" class="proposed-root-note">
            This root is absent from the glossary. Review the proposals and their evidence below.
        </p>
        <div class="entry-body">
            <EntryOutline :items="outline"/>
            <div class="entry-content">
                <EntryStem
                    v-for="stem in stems"
                    :key="stem.id"
                    :stem="stem"
                    :proposals="stemProposals(stem.id)"
                />
                <section
                    v-if="
                        (layer !== 'proposals' && entry?.idioms.length)
                            || (layer !== 'glossary' && idiomProposals.length)
                    "
                    id="entry-idioms"
                    class="rule-section"
                >
                    <h2>Idiomatic phrases</h2>
                    <template v-if="layer !== 'proposals'">
                        <GlossaryIdiom
                            v-for="idiom in entry?.idioms"
                            :key="idiom.id"
                            :idiom="idiom"
                            :text-ids="data.textIds"
                        />
                    </template>
                    <template v-if="layer !== 'glossary'">
                        <ProposalCard
                            v-for="proposal in idiomProposals"
                            :key="proposal.id"
                            :proposal="proposal"
                        />
                    </template>
                </section>
                <section
                    v-if="
                        (layer !== 'proposals' && entryNotes.length)
                            || (layer !== 'glossary' && entryProposals.length)
                    "
                    id="entry-notes"
                    class="rule-section"
                >
                    <h2>Notes & proposals</h2>
                    <template v-if="layer !== 'proposals'">
                        <p v-for="(note, n) in entryNotes" :key="n" class="entry-note serif">
                            {{ note }}
                        </p>
                    </template>
                    <ProposalCard
                        v-for="proposal in layer === 'glossary' ? [] : entryProposals"
                        :key="proposal.id"
                        :proposal="proposal"
                    />
                </section>
                <p v-if="layer === 'proposals' && !data.proposals.length" class="empty">
                    No machine proposals for this entry yet.
                </p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { IStem } from '#shared/types/IStem'
import { entryHref } from '#shared/utils/entryHref'
import { glossarySenses } from '#shared/utils/glossarySenses'

const route = useRoute()
const id = computed(() => String(route.params.id))
const {
    data,
    error,
} = await useFetch(
    () => `/api/glossary/entries/${encodeURIComponent(id.value)}`
)
if (error.value)
    throw createError({
        statusCode: error.value.statusCode || 500,
        statusMessage: error.value.data?.message || 'Entry could not be loaded.',
    })
const entry = computed(() => data.value?.entry)
const rootLabel = computed(
    () =>
        entry.value?.root
        || String(
            data.value?.proposals.find(proposal => proposal.kind === 'new-root')?.data.root
            || id.value
        )
)
const preferences = useGlossaryPreferences()
const { view } = preferences
const layer = computed({
    get: () => (entry.value ? preferences.layer.value : 'with'),
    set: (value) => {
        preferences.layer.value = value
    },
})
const entryNotes = computed(() =>
    (entry.value?.notes || []).filter(note => !/^idiomatic phrases\s*[:.]?$/iu.test(note.trim()))
)
const {
    load,
    error: reviewError,
} = useProposalReviews()
await load()
useHead({ title: rootLabel })
const layers = [
    {
        value: 'glossary',
        label: 'Glossary only',
    },
    {
        value: 'with',
        label: 'With proposals',
    },
    {
        value: 'proposals',
        label: 'Proposals only',
    },
] as const
const stems = computed(() => {
    const items: IStem[] = [...(entry.value?.stems || [])]
    for (const proposal of layer.value === 'glossary' ? [] : data.value?.proposals || []) {
        if (
            proposal.kind !== 'new-stem'
            || !proposal.target.stemId
            || items.some(stem => stem.id === proposal.target.stemId)
        )
            continue
        items.push({
            id: proposal.target.stemId,
            stem: String(proposal.data.stem || proposal.target.stemId.split('.').at(-1)),
            forms: String(proposal.data.forms || ''),
            senses: [],
            sensesRaw: '',
            detransitiveSenses: [],
            detransitiveSensesRaw: null,
            boxes: [],
            notes: [],
        })
    }
    return items
})
function proposalStem(proposal: NonNullable<typeof data.value>['proposals'][number]) {
    return stems.value.find(
        stem =>
            proposal.target.stemId === stem.id
            || proposal.target.boxId?.startsWith(`${stem.id}.`)
            || proposal.target.exampleId?.startsWith(`${stem.id}.`)
    )?.id
}
function stemProposals(stemId: string) {
    return (data.value?.proposals || []).filter(
        proposal => proposal.kind !== 'new-idiom' && proposalStem(proposal) === stemId
    )
}
const idiomProposals = computed(() =>
    (data.value?.proposals || []).filter(proposal => proposal.kind === 'new-idiom')
)
const entryProposals = computed(() =>
    (data.value?.proposals || []).filter(
        proposal => proposal.kind !== 'new-idiom' && !proposalStem(proposal)
    )
)
const outline = computed(() => {
    const items: { id: string
        label: string
        depth?: number }[] = []
    for (const stem of stems.value) {
        items.push({
            id: stem.id,
            label: `Stem ${stem.stem}`,
        })
        for (const sense of glossarySenses(stem))
            if (layer.value !== 'proposals')
                items.push({
                    id: `${stem.id}-sense-${sense.key}`,
                    label: `${sense.key} · ${sense.gloss}`,
                    depth: 1,
                })
        if (
            (layer.value !== 'proposals' && stem.notes.length)
            || (layer.value !== 'glossary'
                && stemProposals(stem.id).some(p => ['note', 'question'].includes(p.kind)))
        )
            items.push({
                id: `${stem.id}-notes`,
                label: 'Notes',
                depth: 1,
            })
    }
    if (
        (layer.value !== 'proposals' && entry.value?.idioms.length)
        || (layer.value !== 'glossary' && idiomProposals.value.length)
    )
        items.push({
            id: 'entry-idioms',
            label: 'Idiomatic phrases',
        })
    if (
        (layer.value !== 'proposals' && entryNotes.value.length)
        || (layer.value !== 'glossary' && entryProposals.value.length)
    )
        items.push({
            id: 'entry-notes',
            label: 'Notes & proposals',
        })
    return items
})
</script>

<style scoped>
.entry-body {
    min-width: 0;
}
.entry-content {
    min-width: 0;
}
.entry-content :deep([id]) {
    scroll-margin-top: 24px;
}
@media (max-width: 1279px) {
    .entry-content :deep([id]) {
        scroll-margin-top: 60px;
    }
}
@media (max-width: 780px) {
    .entry-content :deep([id]) {
        scroll-margin-top: 95px;
    }
}
.proposed-root-note {
    color: var(--muted);
    margin: 1.5rem 0;
}
@media (min-width: 1280px) {
    .entry-body {
        display: grid;
        grid-template-columns: minmax(0, 1fr) 175px;
        gap: 2rem;
    }
    .entry-content {
        grid-column: 1;
        grid-row: 1;
    }
}

.entry-crumb {
    display: flex;
    gap: 0.7rem;
    align-items: center;
    font-size: 0.7rem;
    color: var(--muted);
    margin: 0.2rem 0 2rem;
}
.source {
    margin-left: auto;
    font-size: 0.6rem;
}
.entry-heading h1 {
    font-size: clamp(3.5rem, 7vw, 5.4rem);
    margin: 0.3rem 0 0.9rem;
}
.entry-head {
    font-size: 1.25rem;
    max-width: 52rem;
    line-height: 1.65;
}
.cross-refs {
    margin-top: 0.8rem;
    font-size: 0.9rem;
}
.entry-controls {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 1rem;
    margin: 2rem 0 1rem;
    padding: 1.2rem 0;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
}
.control-label {
    margin-bottom: 0.4rem;
    font-size: 0.6rem;
}
.proposal-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.65rem;
    color: var(--muted);
    margin-bottom: 1.5rem;
}
.addition {
    color: var(--addition);
}
.correction {
    color: var(--correction);
}
.note {
    color: var(--note);
}
.entry-note {
    margin: 0.7rem 0;
    color: var(--muted);
    font-size: 1.1rem;
}
.idiom {
    margin: 1rem 0;
    font-size: 1.2rem;
}
</style>
