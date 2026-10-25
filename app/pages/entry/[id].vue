<template>
    <div v-if="data">
        <NuxtLink to="/glossary" class="back-link">← Glossary</NuxtLink>
        <header class="entry-heading stack">
            <h1>{{ rootLabel }}</h1>
            <p v-if="entry" class="entry-head serif">
                {{ entry.head }}
            </p>
            <p v-else class="muted">
                Suggested new verb. This entry is not in the glossary yet.
            </p>
            <div v-if="entry?.crossRefs.length" class="row">
                <span>See also</span><NuxtLink
                    v-for="ref in entry.crossRefs"
                    :key="ref"
                    :to="entryHref(ref)"
                >{{ ref.replaceAll("-", " ") }}</NuxtLink>
            </div>
        </header>
        <label
            v-if="data.proposals.length"
            class="suggestion-switch"
        ><input v-model="showSuggestions" type="checkbox" role="switch"/> Show
            machine suggestions ({{ data.proposals.length }})</label>
        <p v-if="reviewError" role="alert" class="error">
            {{ reviewError }}
        </p>
        <EntryStem
            v-for="stem in stems"
            :key="stem.id"
            :stem="stem"
            :proposals="
                visibleProposals.filter(
                    (item) => proposalStem(item) === stem.id && !isIdiom(item)
                )
            "
        />
        <section
            v-if="entry?.idioms.length || idiomProposals.length"
            class="rule-section"
        >
            <h2>Idiomatic phrases</h2>
            <div v-for="idiom in entry?.idioms" :key="idiom.id">
                <GlossaryIdiom :idiom="idiom" :text-ids="data.textIds"/><ProposalNote
                    v-for="proposal in idiomProposals.filter(
                        (item) => item.target.exampleId === idiom.id
                    )"
                    :key="proposal.id"
                    :proposal="proposal"
                />
            </div>
            <ProposalNote
                v-for="proposal in idiomProposals.filter(
                    (item) =>
                        !entry?.idioms.some((idiom) => idiom.id === item.target.exampleId)
                )"
                :key="proposal.id"
                :proposal="proposal"
            />
        </section>
        <section
            v-if="entryNotes.length || entryProposals.length"
            class="rule-section stack"
        >
            <h2>Notes</h2>
            <p v-for="(note, n) in entryNotes" :key="n" class="serif">
                {{ note }}
            </p>
            <ProposalNote
                v-for="proposal in entryProposals"
                :key="proposal.id"
                :proposal="proposal"
            />
        </section>
        <nav
            class="root-navigation rule-section"
            aria-label="Previous and next root"
        >
            <NuxtLink
                v-if="previous"
                :to="entryHref(previous.id)"
            >← {{ previous.root
            }}<span class="caption">Previous root</span></NuxtLink><NuxtLink
                v-if="next"
                :to="entryHref(next.id)"
            >{{ next.root }} →<span class="caption">Next root</span></NuxtLink>
        </nav>
    </div>
</template>

<script setup lang="ts">
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import type { IStem } from '#shared/types/IStem'
import { entryHref } from '#shared/utils/entryHref'

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
        statusMessage: 'Entry could not be loaded.',
    })
const entry = computed<IEntry | null>(() => data.value?.entry || null)
provide('glossary-entry', entry)
const rootLabel = computed(
    () =>
        entry.value?.root
        || String(
            data.value?.proposals.find(item => item.kind === 'new-root')?.data
                .root || id.value
        )
)
const { isApproved } = useAuth()
const showSuggestions = ref(isApproved.value)
const {
    load,
    error: reviewError,
} = useProposalReviews()
await load()
const visibleProposals = computed(() =>
    showSuggestions.value ? data.value?.proposals || [] : []
)
const entryNotes = computed(() =>
    (entry.value?.notes || []).filter(
        note => !/^idiomatic phrases\s*[:.]?$/iu.test(note.trim())
    )
)
const stems = computed(() => {
    const items: IStem[] = [...(entry.value?.stems || [])]
    for (const proposal of visibleProposals.value)
        if (
            proposal.kind === 'new-stem'
            && proposal.target.stemId
            && !items.some(stem => stem.id === proposal.target.stemId)
        )
            items.push({
                id: proposal.target.stemId,
                stem: String(
                    proposal.data.stem || proposal.target.stemId.split('.').at(-1)
                ),
                forms: '',
                senses: [],
                sensesRaw: '',
                detransitiveSenses: [],
                detransitiveSensesRaw: null,
                boxes: [],
                notes: [],
            })
    return items
})
function proposalStem(proposal: IProposal) {
    return stems.value.find(
        stem =>
            proposal.target.stemId === stem.id
            || proposal.target.boxId?.startsWith(`${stem.id}.`)
            || proposal.target.exampleId?.startsWith(`${stem.id}.`)
    )?.id
}
function isIdiom(proposal: IProposal) {
    return (
        proposal.kind === 'new-idiom'
        || !!entry.value?.idioms.some(
            item => item.id === proposal.target.exampleId
        )
        || !!proposal.target.exampleId?.includes('.idiom.')
    )
}
const idiomProposals = computed(() => visibleProposals.value.filter(isIdiom))
const entryProposals = computed(() =>
    visibleProposals.value.filter(
        item => !isIdiom(item) && !proposalStem(item)
    )
)
const { data: index } = await useFetch('/api/glossary/roots')
const position = computed(
    () => index.value?.findIndex(item => item.id === id.value) ?? -1
)
const previous = computed(() =>
    position.value > 0 ? index.value?.[position.value - 1] : null
)
const next = computed(() =>
    position.value >= 0 ? index.value?.[position.value + 1] : null
)
useHead({ title: rootLabel })
</script>

<style scoped>
.back-link {
  display: inline-flex;
  align-items: center;
  min-height: 48px;
  margin-bottom: 1rem;
}
.entry-heading h1 {
  font-size: 4rem;
}
.entry-head {
  font-size: 1.3rem;
}
.entry-heading .row a {
  min-height: 48px;
  display: inline-flex;
  align-items: center;
}
.suggestion-switch {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  min-height: 56px;
  margin-top: 1.5rem;
  border-top: 1px solid var(--rule);
  padding: 1rem 0;
}
.root-navigation {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}
.root-navigation a {
  display: grid;
  gap: 0.3rem;
  min-height: 48px;
  font-family: var(--font-serif);
  font-size: 1.5rem;
}
.root-navigation .caption {
  font-family: var(--font-sans);
}
</style>
