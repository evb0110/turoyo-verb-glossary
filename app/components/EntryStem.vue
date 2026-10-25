<template>
    <section :id="stem.id" class="stem-section">
        <header class="stem-header">
            <div>
                <p class="eyebrow">
                    Stem {{ stem.stem }}
                </p>
                <h2 class="turoyo">
                    {{ stem.forms || 'Proposed stem' }}
                </h2>
            </div>
            <span class="muted stem-count">
                {{ stem.boxes.reduce((n, box) => n + box.examples.length, 0) }} examples
            </span>
        </header>
        <details
            v-if="layer !== 'proposals' && stem.boxes.length"
            class="matrix-wrap"
            :open="matrixOpen"
            @toggle="matrixOpen = ($event.target as HTMLDetailsElement).open"
        >
            <summary>
                Examples by sense and form: {{ matrixSenses.length }}
                {{ matrixSenses.length === 1 ? 'sense' : 'senses' }} × {{ stem.boxes.length }}
                {{ stem.boxes.length === 1 ? 'form' : 'forms' }}<template v-if="thinCells">
                    · {{ thinCells }} {{ thinCells === 1 ? 'cell' : 'cells' }} with three examples or
                    fewer
                </template>
            </summary>
            <div class="matrix-scroll">
                <table class="coverage-matrix">
                    <thead>
                        <tr>
                            <th scope="col" class="sense-col">
                                Sense
                            </th>
                            <th v-for="box in stem.boxes" :key="box.id" scope="col">
                                {{ box.detransitive ? 'D · ' : '' }}{{ box.label }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="sense in matrixSenses" :key="sense.key">
                            <th scope="row" class="sense-col" :title="sense.gloss">
                                <span class="matrix-key">{{ sense.key === '?' ? '—' : sense.key }}</span>
                                <span class="matrix-gloss">{{ sense.gloss || 'Unnumbered examples' }}</span>
                            </th>
                            <td v-for="box in stem.boxes" :key="box.id">
                                <button
                                    v-if="count(box, sense.key)"
                                    :class="{
                                        thin: count(box, sense.key) <= 3,
                                        chosen: focus?.box === box.id && focus.sense === sense.key
                                    }"
                                    :aria-label="cellLabel(box, sense.key)"
                                    :title="cellLabel(box, sense.key)"
                                    @click="jump(sense.key, box.id)"
                                >
                                    {{ count(box, sense.key) }}
                                </button>
                                <span v-else class="empty" aria-hidden="true">·</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </details>
        <template v-if="view === 'sense'">
            <section
                v-for="sense in visibleSenses"
                :id="`${stem.id}-sense-${sense.key}`"
                :key="sense.key"
                class="sense-section"
            >
                <div v-if="layer !== 'proposals' && !sense.proposed" class="sense-heading">
                    <span class="sense-label">
                        {{ sense.key === '?' ? '—' : sense.key }}
                    </span>
                    <h3>{{ sense.gloss }}</h3>
                </div>
                <template v-if="layer !== 'glossary'">
                    <ProposalCard
                        v-for="proposal in senseProposals(sense.key)"
                        :key="proposal.id"
                        :proposal="proposal"
                    />
                </template>
                <template v-for="box in stem.boxes" :key="box.id">
                    <div
                        v-if="
                            examples(box, sense.key).length
                                || boxProposals(box.id, sense.key).length
                        "
                        :id="cellId(sense.key, box.id)"
                        class="example-box"
                        :class="{
                            focused: focus?.box === box.id && focus.sense === sense.key
                        }"
                    >
                        <p
                            v-if="layer !== 'proposals' || boxHasProposals(box, sense.key)"
                            class="box-label"
                        >
                            {{ box.detransitive ? 'Detransitive · ' : '' }}{{ box.label }}
                        </p>
                        <GlossaryExample
                            v-for="example in examples(box, sense.key)"
                            :key="example.id"
                            :example="example"
                            :proposals="exampleProposals(example.id)"
                        />
                        <template v-if="layer !== 'glossary'">
                            <ProposalCard
                                v-for="proposal in boxProposals(box.id, sense.key)"
                                :key="proposal.id"
                                :proposal="proposal"
                            />
                        </template>
                    </div>
                </template>
            </section>
        </template>
        <template v-else>
            <div
                v-for="sense in visibleSenses"
                :id="`${stem.id}-sense-${sense.key}`"
                :key="sense.key"
                class="box-sense-heading"
            >
                <div v-if="layer !== 'proposals' && !sense.proposed" class="sense-heading">
                    <span class="sense-label">
                        {{ sense.key === '?' ? '—' : sense.key }}
                    </span>
                    <h3>{{ sense.gloss }}</h3>
                </div>
                <template v-if="layer !== 'glossary'">
                    <ProposalCard
                        v-for="proposal in senseProposals(sense.key)"
                        :key="proposal.id"
                        :proposal="proposal"
                    />
                </template>
            </div>
            <section
                v-for="box in stem.boxes"
                :id="box.id"
                :key="box.id"
                class="glossary-box"
                :class="{ focused: focus?.box === box.id }"
            >
                <h3>{{ box.detransitive ? 'Detransitive · ' : '' }}{{ box.label }}</h3>
                <GlossaryExample
                    v-for="example in box.examples"
                    :key="example.id"
                    :example="example"
                    :proposals="exampleProposals(example.id)"
                    numbered
                />
                <template v-if="layer !== 'glossary'">
                    <ProposalCard
                        v-for="proposal in boxProposals(box.id)"
                        :key="proposal.id"
                        :proposal="proposal"
                    />
                </template>
            </section>
        </template>
        <template v-if="layer !== 'glossary'">
            <ProposalCard v-for="proposal in remaining" :key="proposal.id" :proposal="proposal"/>
        </template>
        <aside
            v-if="stem.notes.length || (layer !== 'glossary' && notes.length)"
            :id="`${stem.id}-notes`"
            class="stem-notes"
        >
            <h3>Notes & questions</h3>
            <template v-if="layer !== 'proposals'">
                <p v-for="(note, i) in stem.notes" :key="i" class="serif">
                    {{ note }}
                </p>
            </template>
            <template v-if="layer !== 'glossary'">
                <ProposalCard v-for="proposal in notes" :key="proposal.id" :proposal="proposal"/>
            </template>
        </aside>
    </section>
</template>

<script setup lang="ts">
import type { IBox } from '#shared/types/IBox'
import type { IProposal } from '#shared/types/IProposal'
import type { IStem } from '#shared/types/IStem'
import { glossarySenses } from '#shared/utils/glossarySenses'

const props = defineProps<{ stem: IStem
    proposals: IProposal[] }>()
const {
    view,
    layer,
} = useGlossaryPreferences()
const focus = ref<{ sense: string
    box: string } | null>(null)
const noteKinds = ['note', 'question']
const notes = computed(() => props.proposals.filter(item => noteKinds.includes(item.kind)))
const changes = computed(() => props.proposals.filter(item => !noteKinds.includes(item.kind)))
const knownExamples = computed(
    () => new Set(props.stem.boxes.flatMap(box => box.examples.map(example => example.id)))
)
const knownBoxes = computed(() => new Set(props.stem.boxes.map(box => box.id)))
function isExample(item: IProposal) {
    return !!item.target.exampleId && knownExamples.value.has(item.target.exampleId)
}
function isSense(item: IProposal) {
    return (
        !isExample(item) && ['new-sense', 'gloss-change'].includes(item.kind) && !!item.target.sense
    )
}
function isBox(item: IProposal) {
    return (
        !isExample(item)
        && !isSense(item)
        && !!item.target.boxId
        && knownBoxes.value.has(item.target.boxId)
    )
}
const allSenses = computed(() => {
    const rows = glossarySenses(props.stem).map(sense => ({
        ...sense,
        proposed: false,
    }))
    for (const item of changes.value)
        if (isSense(item) || isBox(item)) {
            const key = item.target.sense || '?'
            if (!rows.some(row => row.key === key))
                rows.push({
                    n: key,
                    key,
                    gloss: '',
                    proposed: true,
                })
        }
    return rows
})
const matrixSenses = computed(() => allSenses.value.filter(sense => !sense.proposed))
const matrixOpen = ref(matrixSenses.value.length <= 8 && props.stem.boxes.length <= 6)
const thinCells = computed(() =>
    matrixSenses.value.reduce(
        (total, sense) =>
            total
            + props.stem.boxes.filter(
                box => count(box, sense.key) > 0 && count(box, sense.key) <= 3
            ).length,
        0
    )
)
const visibleSenses = computed(() =>
    allSenses.value.filter(
        sense =>
            (layer.value !== 'glossary' || !sense.proposed)
            && (layer.value !== 'proposals'
                || senseProposals(sense.key).length
                || props.stem.boxes.some(box => boxHasProposals(box, sense.key)))
    )
)
function examples(box: IBox, key: string) {
    return box.examples.filter(
        example =>
            (example.sense ? `${box.detransitive ? 'D' : ''}${example.sense}` : '?') === key
    )
}
function cellLabel(box: IBox, key: string) {
    const label = `${box.detransitive ? 'detransitive ' : ''}${box.label}`
    return `Sense ${key}, ${label}: ${count(box, key)} examples`
}
function count(box: IBox, key: string) {
    return examples(box, key).length
}
function exampleProposals(id: string) {
    return changes.value.filter(item => isExample(item) && item.target.exampleId === id)
}
function senseProposals(key: string) {
    return changes.value.filter(item => isSense(item) && item.target.sense === key)
}
function boxProposals(id: string, key?: string) {
    return changes.value.filter(
        item =>
            isBox(item)
            && item.target.boxId === id
            && (key === undefined || (item.target.sense || '?') === key)
    )
}
function boxHasProposals(box: IBox, key: string) {
    return (
        boxProposals(box.id, key).length > 0
        || examples(box, key).some(example => exampleProposals(example.id).length)
    )
}
const remaining = computed(() =>
    changes.value.filter(item => !isExample(item) && !isSense(item) && !isBox(item))
)
function cellId(key: string, box: string) {
    return `${props.stem.id}-cell-${key}-${box}`
}
function jump(sense: string, box: string) {
    focus.value = {
        sense,
        box,
    }
    nextTick(() =>
        document.getElementById(view.value === 'sense' ? cellId(sense, box) : box)?.scrollIntoView({
            behavior: 'smooth',
            block: 'center',
        })
    )
}
</script>

<style scoped>
.stem-section {
    margin-top: 2rem;
    padding-top: 1.8rem;
    border-top: 2px solid var(--ink);
}
.stem-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}
.stem-header h2 {
    font-size: 2.4rem;
    margin-top: 0.3rem;
}
.stem-count {
    font-size: 0.7rem;
}
.matrix-wrap {
    margin: 1.5rem 0 2rem;
}
.matrix-wrap > summary {
    cursor: pointer;
    color: var(--muted);
    font-size: 0.75rem;
    padding: 0.5rem 0;
}
.matrix-scroll {
    overflow-x: auto;
}
.coverage-matrix {
    border-collapse: collapse;
    font-size: 0.75rem;
}
th {
    font-weight: 400;
    color: var(--muted);
    white-space: nowrap;
    text-align: center;
    padding: 0.3rem 0.6rem;
    border-bottom: 1px solid var(--rule);
}
td {
    text-align: center;
    padding: 0.2rem 0.6rem;
    border-bottom: 1px solid var(--rule);
}
.sense-col {
    position: sticky;
    left: 0;
    z-index: 1;
    background: var(--paper);
    text-align: left;
    max-width: 16rem;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-left: 0;
}
.matrix-key {
    display: inline-block;
    min-width: 1.6rem;
    color: var(--ink);
}
.matrix-gloss {
    color: var(--muted);
}
td button {
    min-width: 2rem;
    border: 0;
    border-radius: 3px;
    padding: 0.15rem 0.4rem;
    color: var(--accent);
    background: color-mix(in srgb, var(--accent) 12%, transparent);
    cursor: pointer;
}
td button:hover {
    background: color-mix(in srgb, var(--accent) 24%, transparent);
}
td .thin {
    color: var(--correction);
    background: color-mix(in srgb, var(--correction) 10%, transparent);
}
td .chosen {
    background: var(--accent);
    color: var(--paper);
}
.empty {
    color: var(--rule);
}
.sense-section {
    margin: 1.7rem 0;
}
.sense-heading {
    display: flex;
    align-items: baseline;
    gap: 1rem;
    margin: 1rem 0;
}
.sense-heading h3 {
    font-size: 1.5rem;
}
.sense-label {
    font-family: var(--font-serif);
    font-size: 1.5rem;
    color: var(--accent);
    min-width: 1.3rem;
}
.example-box {
    margin: 1rem 0 1.2rem 2.3rem;
    padding: 0.1rem 0.7rem;
    border-left: 1px solid var(--rule);
}
.box-label {
    color: var(--muted);
    font-size: 0.65rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.focused {
    background: var(--panel);
    outline: 1px solid var(--rule);
}
.glossary-box {
    border: 1px solid var(--rule);
    margin: 1rem 0;
    padding: 1rem 1.2rem;
}
.glossary-box h3 {
    font-size: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--rule);
}
.stem-notes {
    border-top: 1px solid var(--rule);
    padding-top: 1rem;
    margin-top: 2rem;
}
.stem-notes p {
    margin-top: 0.7rem;
}
@media (max-width: 600px) {
    .example-box {
        margin-left: 0.4rem;
    }
    .stem-header h2 {
        font-size: 2rem;
    }
    .sense-heading h3 {
        font-size: 1.3rem;
    }
}
</style>
