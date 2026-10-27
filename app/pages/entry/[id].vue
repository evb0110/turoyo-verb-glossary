<template>
    <div v-if="data" class="entry">
        <DefineTocCount v-slot="{ count }">
            <span v-if="count" class="num">{{ count }}<span class="sr-only"> undecided</span></span>
        </DefineTocCount>
        <BackLink/>
        <header class="entry-head">
            <div class="entry-title">
                <h1 class="serif">
                    {{ rootLabel }}
                </h1>
                <nav class="root-nav small" aria-label="Previous and next root">
                    <NuxtLink v-if="previous" :to="entryHref(previous.id)" rel="prev">
                        ← {{ previous.root }}
                    </NuxtLink>
                    <NuxtLink v-if="next" :to="entryHref(next.id)" rel="next">
                        {{ next.root }} →
                    </NuxtLink>
                </nav>
            </div>
            <p v-if="entry" class="serif head">
                {{ entry.head }}
            </p>
            <p v-else class="muted">
                Suggested new verb. This entry is not in the glossary yet.
            </p>
            <p v-if="entry?.crossRefs.length" class="small cross-refs">
                See also
                <NuxtLink
                    v-for="ref in entry.crossRefs"
                    :key="ref"
                    :to="entryHref(ref)"
                >
                    <span v-text="ref.replaceAll('-', ' ')"></span>
                </NuxtLink>
            </p>
        </header>
        <div class="entry-grid">
            <aside class="entry-side">
                <fieldset v-if="data.proposals.length" class="filter">
                    <legend>Machine suggestions</legend>
                    <p class="counts">
                        {{ data.proposals.length }} in this entry, {{ openCount }} undecided
                    </p>
                    <label><input v-model="mode" type="radio" value="all"/> Show all</label>
                    <label><input v-model="mode" type="radio" value="open"/> Show only undecided</label>
                    <label><input v-model="mode" type="radio" value="off"/> Hide all</label>
                </fieldset>
                <nav v-if="hasContents" class="toc small" aria-labelledby="toc-title">
                    <p class="toc-head">
                        <span id="toc-title">Contents</span>
                        <span v-if="counting" aria-hidden="true">undecided</span>
                    </p>
                    <ul>
                        <li v-for="layout in layouts" :key="layout.stem.id">
                            <a
                                :href="`#${encodeURIComponent(layout.stem.id)}`"
                                class="toc-stem"
                            >Stem {{ layout.stem.stem }}</a>
                            <ul>
                                <li v-for="sense in layout.senses" :key="sense.key">
                                    <a :href="`#${encodeURIComponent(sense.id)}`">
                                        <span class="toc-n">{{ sense.key }}</span>
                                        <span v-if="sense.proposed" v-overflow-title class="toc-gloss">
                                            <span class="toc-new">new</span> {{ suggestedGloss(sense.lead) }}
                                        </span>
                                        <span v-else v-overflow-title class="toc-gloss">{{ sense.gloss }}</span>
                                        <TocCount :count="openIn(sense.all)"/>
                                    </a>
                                </li>
                                <li v-if="layout.remaining.length">
                                    <a :href="`#${encodeURIComponent(`${layout.stem.id}-other`)}`">
                                        <span class="toc-gloss">Other suggestions</span>
                                        <TocCount :count="openIn(layout.remaining)"/>
                                    </a>
                                </li>
                            </ul>
                        </li>
                        <li v-if="entry?.idioms.length || idiomProposals.length">
                            <a href="#idioms">
                                <span class="toc-gloss">Idiomatic phrases</span>
                                <TocCount :count="openIn(idiomProposals)"/>
                            </a>
                        </li>
                        <li v-if="entryNotes.length || entryProposals.length">
                            <a href="#notes">
                                <span class="toc-gloss">Notes and questions</span>
                                <TocCount :count="openIn(entryProposals)"/>
                            </a>
                        </li>
                    </ul>
                </nav>
                <div class="export small">
                    <DocumentDownload :href="exportHref" label="Download"/>
                    <label v-if="data.proposals.length">
                        <input v-model="withSuggestions" type="checkbox"/> with suggestions and decisions
                    </label>
                </div>
            </aside>
            <div class="entry-main">
                <p v-if="reviewError" role="alert" class="error">
                    {{ reviewError }}
                </p>
                <EntryStem
                    v-for="layout in layouts"
                    :key="layout.stem.id"
                    :layout="layout"
                    :entry="entry"
                />
                <section v-if="entry?.idioms.length || idiomProposals.length" id="idioms" class="block">
                    <h2>Idiomatic phrases</h2>
                    <div v-for="idiom in entry?.idioms" :key="idiom.id">
                        <GlossaryIdiom :idiom="idiom" :text-ids="data.textIds"/>
                        <ProposalCard
                            v-for="proposal in idiomProposals.filter((item) => item.target.exampleId === idiom.id)"
                            :key="proposal.id"
                            :proposal="proposal"
                            :entry="entry"
                            placement="example"
                        />
                    </div>
                    <ProposalCard
                        v-for="proposal in unplacedIdiomProposals"
                        :key="proposal.id"
                        :proposal="proposal"
                        :entry="entry"
                    />
                </section>
                <section v-if="entryNotes.length || entryProposals.length" id="notes" class="block">
                    <h2>Notes and questions for the editors</h2>
                    <p v-for="(note, n) in entryNotes" :key="n" class="serif">
                        {{ note }}
                    </p>
                    <ProposalCard
                        v-for="proposal in entryProposals"
                        :key="proposal.id"
                        :proposal="proposal"
                        :entry="entry"
                    />
                </section>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { createReusableTemplate } from '@vueuse/core'
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import { entryHref } from '#shared/utils/entryHref'
import { entryLayout } from '#shared/utils/entryLayout'

const route = useRoute()
const id = computed(() => String(route.params.id))
const {
    data,
    error,
} = await useFetch(() => `/api/glossary/entries/${encodeURIComponent(id.value)}`)
if (error.value)
    throw createError({
        statusCode: error.value.statusCode || 500,
        statusMessage: 'Entry could not be loaded.',
    })
const entry = computed<IEntry | null>(() => data.value?.entry || null)
const rootLabel = computed(() =>
    entry.value?.root
    || String(data.value?.proposals.find(item => item.kind === 'new-root')?.data.root || id.value)
)
const {
    load,
    status,
    error: reviewError,
} = useProposalReviews()
await load()
const modeCookie = useCookie<string>('entry-suggestions', {
    default: () => 'all',
    sameSite: 'lax',
    maxAge: 31536000,
})
const mode = computed({
    get: () => (['all', 'open', 'off'].includes(modeCookie.value) ? modeCookie.value : 'all'),
    set: (value: string) => {
        modeCookie.value = value
    },
})
const proposals = computed(() => data.value?.proposals || [])
const openCount = computed(() => proposals.value.filter(item => status(item.id) === 'open').length)
function openIn(items: IProposal[]) {
    return items.filter(item => status(item.id) === 'open').length
}
const [DefineTocCount, TocCount] = createReusableTemplate<{ count: number }>()
// The contents count undecided suggestions while suggestions are shown.
const counting = computed(() => mode.value !== 'off' && proposals.value.length > 0)
// A meaning that exists only as a suggestion is listed with the wording the machine suggests for it.
function suggestedGloss(lead: IProposal[]) {
    const gloss = lead.find(item => item.kind === 'new-sense')?.data.gloss
    return typeof gloss === 'string' && gloss ? gloss : 'meaning'
}
// "Undecided" keeps the suggestions that were undecided when it was chosen, so a card
// does not vanish while it is being decided.
const undecidedAtSwitch = ref<Set<string>>(new Set())
watch([mode, proposals], () => {
    if (mode.value === 'open')
        undecidedAtSwitch.value = new Set(proposals.value.filter(item => status(item.id) === 'open').map(item => item.id))
}, { immediate: true })
const visibleProposals = computed(() =>
    mode.value === 'off'
        ? []
        : mode.value === 'open'
            ? proposals.value.filter(item => undecidedAtSwitch.value.has(item.id))
            : proposals.value
)
// The download includes the suggestions, with the team's decisions, when the page shows them.
const withSuggestions = ref(mode.value !== 'off')
const exportHref = computed(() => `/api/glossary/export/entry/${encodeURIComponent(id.value)}${
    withSuggestions.value && proposals.value.length ? '?suggestions=1' : ''}`)
const placement = computed(() => entryLayout(entry.value, visibleProposals.value))
const layouts = computed(() => placement.value.layouts)
const idiomProposals = computed(() => placement.value.idiomProposals)
const unplacedIdiomProposals = computed(() => placement.value.unplacedIdiomProposals)
const entryProposals = computed(() => placement.value.entryProposals)
const entryNotes = computed(() => placement.value.notes)
// Cross-reference entries such as ʔkl → ʔxl have nothing to list.
const hasContents = computed(() => !!(layouts.value.length || entry.value?.idioms.length
    || idiomProposals.value.length || entryNotes.value.length || entryProposals.value.length))
const previous = computed(() => data.value?.previous || null)
const next = computed(() => data.value?.next || null)
useHead({ title: rootLabel })
</script>

<style scoped>
.entry-head {
  display: grid;
  gap: 0.3rem;
  margin-bottom: 1rem;
}
.entry-title {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.25rem 1.5rem;
}
.entry-title h1 {
  font-size: 2rem;
  font-weight: 700;
}
.root-nav {
  display: flex;
  gap: 1rem;
  margin-left: auto;
  font-family: var(--font-serif);
}
.cross-refs a + a::before {
  display: inline-block;
  margin-right: 0.3em;
  color: var(--ink);
  content: ",";
}
.head {
  max-width: 75rem;
  font-size: 1.125rem;
}
.entry-grid {
  display: grid;
  grid-template-columns: 15rem minmax(0, 1fr);
  gap: 2rem;
  align-items: start;
}
.entry-side {
  position: sticky;
  top: 0.75rem;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.9rem;
  max-height: calc(100vh - 1.5rem);
  overflow-y: auto;
  padding-right: 0.25rem;
}
.filter {
  display: grid;
  gap: 0.15rem;
  margin: 0;
  padding: 0;
  border: 0;
  font-size: 0.875rem;
}
.filter legend {
  margin-bottom: 0.2rem;
  font-weight: 600;
}
.filter label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.export {
  display: grid;
  gap: 0.1rem;
}
.export label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.counts {
  margin-bottom: 0.15rem;
  color: var(--muted);
}
.toc-head {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.15rem;
  color: var(--muted);
}
.toc-head span:first-child {
  color: var(--ink);
  font-weight: 600;
}
.toc ul {
  margin: 0;
  padding: 0;
  list-style: none;
}
.toc ul ul {
  margin-bottom: 0.4rem;
}
.toc a {
  display: flex;
  gap: 0.4rem;
  padding: 0.05rem 0;
  color: var(--ink);
  text-decoration: none;
}
.toc a:hover {
  color: var(--accent);
  text-decoration: underline;
}
.toc .toc-stem {
  font-weight: 600;
}
.toc-n {
  min-width: 1.75rem;
  color: var(--accent);
  font-weight: 600;
}
.toc-gloss {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.toc .num {
  color: var(--muted);
}
.toc-new {
  color: var(--addition);
  font-weight: 600;
}
.block {
  margin-bottom: 1.5rem;
}
.block > h2 {
  padding-bottom: 0.25rem;
  border-bottom: 2px solid var(--ink);
}
.block > p {
  margin-top: 0.3rem;
}
@media (max-width: 900px) {
  .entry-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 0.75rem;
  }
  .entry-side {
    position: static;
    max-height: none;
    overflow: visible;
  }
  .filter {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem 1rem;
  }
  .filter legend,
  .counts {
    width: 100%;
  }
  .toc {
    display: none;
  }
}
</style>
