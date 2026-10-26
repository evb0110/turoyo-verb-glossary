<template>
    <section :id="stem.id" class="stem">
        <header class="stem-head">
            <h2>Stem {{ stem.stem }}</h2>
            <span v-if="stem.forms" class="tur">{{ stem.forms }}</span>
        </header>
        <div v-if="stem.boxes.length > 1 && matrix.length" class="matrix-wrap">
            <table class="matrix">
                <caption class="sr-only">
                    Number of examples for each meaning and form in Stem {{ stem.stem }}
                </caption>
                <thead>
                    <tr>
                        <th scope="col">
                            Meaning
                        </th>
                        <th v-for="box in stem.boxes" :key="box.id" scope="col">
                            {{ box.detransitive ? "Detr. " : "" }}{{ box.label }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="row in matrix" :key="row.key">
                        <th scope="row" :title="row.gloss">
                            {{ row.key === "?" ? "" : `${row.key}.` }} {{ row.gloss }}
                        </th>
                        <td v-for="cell in row.cells" :key="cell.box">
                            <a
                                v-if="cell.count"
                                :href="`#${encodeURIComponent(cell.id)}`"
                                :aria-label="`${cell.count} examples, meaning ${row.key}, ${cell.box}`"
                            >{{ cell.count }}</a>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <section
            v-for="sense in layout.senses"
            :id="sense.id"
            :key="sense.key"
            class="sense"
        >
            <h3 class="sense-head">
                <span class="sense-n">{{ sense.key === "?" ? "" : `${sense.key}.` }}</span>
                <span v-if="sense.proposed" class="muted">Suggested meaning, not in the glossary yet</span>
                <span v-else class="serif">{{ sense.gloss }}</span>
            </h3>
            <ProposalCard
                v-for="proposal in sense.lead"
                :key="proposal.id"
                :proposal="proposal"
                :entry="entry"
            />
            <div
                v-for="group in sense.groups"
                :id="group.id"
                :key="group.id"
                class="form-group"
            >
                <h4 class="form-label">
                    {{ group.box.detransitive ? "Detransitive · " : "" }}{{ group.box.label }}
                </h4>
                <GlossaryExample
                    v-for="item in group.examples"
                    :key="item.example.id"
                    :example="item.example"
                    :proposals="item.proposals"
                    :entry="entry"
                />
                <ProposalCard
                    v-for="proposal in group.proposals"
                    :key="proposal.id"
                    :proposal="proposal"
                    :entry="entry"
                />
            </div>
            <ProposalCard
                v-for="proposal in sense.trail"
                :key="proposal.id"
                :proposal="proposal"
                :entry="entry"
            />
        </section>
        <section v-if="layout.remaining.length" :id="`${stem.id}-other`" class="sense">
            <h3 class="sense-head">
                Other suggestions for Stem {{ stem.stem }}
            </h3>
            <ProposalCard
                v-for="proposal in layout.remaining"
                :key="proposal.id"
                :proposal="proposal"
                :entry="entry"
            />
        </section>
        <section v-if="stem.notes.length" :id="`${stem.id}-notes`" class="sense">
            <h3 class="sense-head">
                Notes
            </h3>
            <p v-for="(note, i) in stem.notes" :key="i" class="serif">
                {{ note }}
            </p>
        </section>
    </section>
</template>

<script setup lang="ts">
import type { stemLayout } from '~/utils/stemLayout'
import type { IEntry } from '#shared/types/IEntry'

const props = defineProps<{ layout: ReturnType<typeof stemLayout>
    entry: IEntry | null }>()
const stem = computed(() => props.layout.stem)
// Examples per meaning and form; each count links to its group below.
const matrix = computed(() => props.layout.senses.filter(sense => !sense.proposed).map(sense => ({
    key: sense.key,
    gloss: sense.gloss,
    cells: stem.value.boxes.map((box) => {
        const group = sense.groups.find(item => item.box.id === box.id)
        return {
            box: box.label,
            id: group?.id || '',
            count: group?.examples.length || 0,
        }
    }),
})))
</script>

<style scoped>
.stem {
  margin-bottom: 1.5rem;
}
.stem-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0 1rem;
  padding-bottom: 0.25rem;
  border-bottom: 2px solid var(--ink);
}
.stem-head .tur {
  font-size: 1.25rem;
}
.matrix-wrap {
  margin: 0.5rem 0 0.75rem;
  overflow-x: auto;
}
.matrix {
  border-collapse: collapse;
  font-size: 0.8125rem;
}
.matrix th,
.matrix td {
  padding: 0.1rem 0.45rem;
  border: 1px solid var(--rule);
  font-weight: 400;
  text-align: left;
  white-space: nowrap;
}
.matrix thead th {
  color: var(--muted);
}
.matrix tbody th {
  max-width: 22rem;
  overflow: hidden;
  text-overflow: ellipsis;
}
.matrix td {
  min-width: 2.5rem;
  text-align: center;
}
.sense {
  margin-top: 0.9rem;
}
.sense-head {
  display: flex;
  gap: 0.5rem;
  font-weight: 400;
}
.sense-head .serif {
  font-size: 1.125rem;
  line-height: 1.35;
}
.sense-n {
  min-width: 1.75rem;
  color: var(--accent);
  font-weight: 700;
}
.form-group {
  margin: 0.35rem 0 0 2.25rem;
}
.form-label {
  margin-top: 0.4rem;
  color: var(--muted);
  font-size: 0.8125rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.sense > .proposal,
.sense > p {
  margin-left: 2.25rem;
}
@media (max-width: 760px) {
  .form-group,
  .sense > .proposal,
  .sense > p {
    margin-left: 0;
  }
}
</style>
