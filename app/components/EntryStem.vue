<template>
    <section :id="stem.id" class="stem-section">
        <header class="stem-header stack">
            <h2>Stem {{ stem.stem }}</h2>
            <p v-if="stem.forms" class="turoyo forms">
                {{ stem.forms }}
            </p>
        </header>
        <details v-if="stem.boxes.length" class="example-table">
            <summary>Show table of examples by meaning and form</summary>
            <table>
                <caption class="sr-only">
                    Number of examples for each meaning and form in Stem
                    {{
                        stem.stem
                    }}
                </caption>
                <thead>
                    <tr>
                        <th scope="col">
                            Meaning
                        </th>
                        <th v-for="box in stem.boxes" :key="box.id" scope="col">
                            {{ box.detransitive ? "Detransitive · " : "" }}{{ box.label }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr
                        v-for="sense in senses.filter((item) => !item.proposed)"
                        :key="sense.key"
                    >
                        <th scope="row">
                            {{ sense.key }}. {{ sense.gloss }}
                        </th>
                        <td
                            v-for="box in stem.boxes"
                            :key="box.id"
                            :data-form="`${box.detransitive ? 'Detransitive · ' : ''}${box.label}`"
                        >
                            <a
                                v-if="examples(box, sense.key).length"
                                :href="`#${encodeURIComponent(cellId(sense.key, box.id))}`"
                            >{{ examples(box, sense.key).length
                            }}<span class="sr-only">
                                examples for meaning {{ sense.key }} · {{ box.label }}</span></a><span v-else>—</span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </details>
        <section
            v-for="sense in senses"
            :id="`${stem.id}-sense-${sense.key}`"
            :key="sense.key"
            class="sense-section"
        >
            <h3 v-if="!sense.proposed">
                <span class="sense-number">{{
                    sense.key === "?" ? "" : `${sense.key}.`
                }}</span>
                {{ sense.gloss }}
            </h3>
            <ProposalNote
                v-for="proposal in senseProposals(sense.key)"
                :key="proposal.id"
                :proposal="proposal"
            />
            <template v-for="box in stem.boxes" :key="box.id">
                <div
                    v-if="
                        examples(box, sense.key).length
                            || boxProposals(box.id, sense.key).length
                    "
                    :id="cellId(sense.key, box.id)"
                    class="example-group"
                >
                    <p class="form-label">
                        {{ box.detransitive ? "Detransitive · " : "" }}{{ box.label }}
                    </p>
                    <GlossaryExample
                        v-for="example in examples(box, sense.key)"
                        :key="example.id"
                        :example="example"
                        :proposals="exampleProposals(example.id)"
                    />
                    <ProposalNote
                        v-for="proposal in boxProposals(box.id, sense.key)"
                        :key="proposal.id"
                        :proposal="proposal"
                    />
                </div>
            </template>
        </section>
        <ProposalNote
            v-for="proposal in remaining"
            :key="proposal.id"
            :proposal="proposal"
        />
        <aside
            v-if="stem.notes.length"
            :id="`${stem.id}-notes`"
            class="stem-notes stack"
        >
            <h3>Notes</h3>
            <p v-for="(note, i) in stem.notes" :key="i" class="serif">
                {{ note }}
            </p>
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
const knownExamples = computed(
    () =>
        new Set(
            props.stem.boxes.flatMap(box =>
                box.examples.map(example => example.id)
            )
        )
)
const knownBoxes = computed(
    () => new Set(props.stem.boxes.map(box => box.id))
)
function isExample(item: IProposal) {
    return (
        !!item.target.exampleId && knownExamples.value.has(item.target.exampleId)
    )
}
function isSense(item: IProposal) {
    return !isExample(item) && !!item.target.sense && !item.target.boxId
}
function isBox(item: IProposal) {
    return (
        !isExample(item)
        && !isSense(item)
        && !!item.target.boxId
        && knownBoxes.value.has(item.target.boxId)
    )
}
const senses = computed(() => {
    const rows = glossarySenses(props.stem).map(sense => ({
        ...sense,
        proposed: false,
    }))
    for (const item of props.proposals)
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
function examples(box: IBox, key: string) {
    return box.examples.filter(
        example =>
            (example.sense
                ? `${box.detransitive ? 'D' : ''}${example.sense}`
                : '?') === key
    )
}
function exampleProposals(id: string) {
    return props.proposals.filter(
        item => isExample(item) && item.target.exampleId === id
    )
}
function senseProposals(key: string) {
    return props.proposals.filter(
        item => isSense(item) && item.target.sense === key
    )
}
function boxProposals(id: string, key: string) {
    return props.proposals.filter(
        item =>
            isBox(item)
            && item.target.boxId === id
            && (item.target.sense || '?') === key
    )
}
const remaining = computed(() =>
    props.proposals.filter(
        item => !isExample(item) && !isSense(item) && !isBox(item)
    )
)
function cellId(key: string, box: string) {
    return `${props.stem.id}-cell-${key}-${box}`
}
</script>

<style scoped>
.stem-section {
  margin-top: 2.5rem;
  border-top: 2px solid var(--ink);
  padding-top: 1.4rem;
}
.stem-header {
  gap: 0.4rem;
}
.forms {
  font-size: 1.8rem;
}
.example-table {
  margin: 1rem 0 1.5rem;
}
table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  font-size: 0.889rem;
}
th,
td {
  padding: 0.6rem 0.4rem;
  border: 1px solid var(--rule);
  text-align: left;
  font-weight: 400;
  overflow-wrap: anywhere;
}
td a {
  display: grid;
  place-content: center;
  min-height: 48px;
}
.sense-section {
  margin: 1.8rem 0;
}
.sense-section h3 {
  font-size: 1.5rem;
}
.sense-number {
  color: var(--accent);
}
.example-group {
  padding: 0.5rem 0 0 1rem;
  margin-top: 1rem;
  border-left: 1px solid var(--rule);
}
.form-label {
  font-size: 0.889rem;
  color: var(--muted);
}
.stem-notes {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--rule);
}
@media (max-width: 760px) {
  table,
  tbody,
  tr {
    display: block;
  }
  thead {
    display: none;
  }
  tr {
    margin-bottom: 1rem;
  }
  th {
    display: block;
    background: var(--panel);
  }
  td {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  td::before {
    content: attr(data-form);
  }
  td a {
    min-width: 48px;
  }
  .example-group {
    padding-left: 0.6rem;
  }
}
</style>
