<template>
    <div v-if="data" class="entry">
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
                    <label><input v-model="mode" type="radio" value="all"/> All ({{ data.proposals.length }})</label>
                    <label><input v-model="mode" type="radio" value="open"/> Undecided ({{ openCount }})</label>
                    <label><input v-model="mode" type="radio" value="off"/> Hide</label>
                </fieldset>
                <nav class="toc small" aria-label="Contents of this entry">
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
                                        <span class="toc-gloss" :title="sense.gloss">
                                            {{ sense.proposed ? "suggested" : sense.gloss }}
                                        </span>
                                        <span v-if="openIn(sense.all)" class="num">{{
                                            openIn(sense.all)
                                        }}</span>
                                    </a>
                                </li>
                                <li v-if="layout.remaining.length">
                                    <a :href="`#${encodeURIComponent(`${layout.stem.id}-other`)}`">
                                        <span class="toc-gloss">Other suggestions</span>
                                        <span v-if="openIn(layout.remaining)" class="num">{{
                                            openIn(layout.remaining)
                                        }}</span>
                                    </a>
                                </li>
                            </ul>
                        </li>
                        <li v-if="entry?.idioms.length || idiomProposals.length">
                            <a href="#idioms">
                                <span class="toc-gloss">Idiomatic phrases</span>
                                <span v-if="openIn(idiomProposals)" class="num">{{ openIn(idiomProposals) }}</span>
                            </a>
                        </li>
                        <li v-if="entryNotes.length || entryProposals.length">
                            <a href="#notes">
                                <span class="toc-gloss">Notes and questions</span>
                                <span v-if="openIn(entryProposals)" class="num">{{ openIn(entryProposals) }}</span>
                            </a>
                        </li>
                    </ul>
                    <p v-if="mode !== 'off' && data.proposals.length" class="muted">
                        Numbers count undecided suggestions.
                    </p>
                </nav>
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
import { stemLayout } from '~/utils/stemLayout'
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import type { IStem } from '#shared/types/IStem'
import { entryHref } from '#shared/utils/entryHref'

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
const entryNotes = computed(() =>
    (entry.value?.notes || []).filter(note => !/^idiomatic phrases\s*[:.]?$/iu.test(note.trim()))
)
const stems = computed(() => {
    const items: IStem[] = [...(entry.value?.stems || [])]
    for (const proposal of visibleProposals.value)
        if (proposal.kind === 'new-stem' && proposal.target.stemId
            && !items.some(stem => stem.id === proposal.target.stemId))
            items.push({
                id: proposal.target.stemId,
                stem: String(proposal.data.stem || proposal.target.stemId.split('.').at(-1)),
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
    return stems.value.find(stem =>
        proposal.target.stemId === stem.id
        || proposal.target.boxId?.startsWith(`${stem.id}.`)
        || proposal.target.exampleId?.startsWith(`${stem.id}.`)
    )?.id
}
function isIdiom(proposal: IProposal) {
    return proposal.kind === 'new-idiom'
        || !!entry.value?.idioms.some(item => item.id === proposal.target.exampleId)
        || !!proposal.target.exampleId?.includes('.idiom.')
}
const layouts = computed(() => stems.value.map(stem => stemLayout(
    stem,
    visibleProposals.value.filter(item => !isIdiom(item) && proposalStem(item) === stem.id)
)))
const idiomProposals = computed(() => visibleProposals.value.filter(isIdiom))
const unplacedIdiomProposals = computed(() => idiomProposals.value
    .filter(item => !entry.value?.idioms.some(idiom => idiom.id === item.target.exampleId)))
const entryProposals = computed(() => visibleProposals.value.filter(item => !isIdiom(item) && !proposalStem(item)))
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
.toc p {
  margin-top: 0.4rem;
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
  .filter legend {
    width: 100%;
  }
  .toc {
    display: none;
  }
}
</style>
