<template>
    <div>
        <div class="page-head">
            <h1>Glossary</h1>
            <span class="small muted">{{ roots.length.toLocaleString("en") }} roots</span>
            <span class="glossary-export small">
                <label for="glossary-part" class="sr-only">Part of the glossary to download</label>
                <select id="glossary-part" v-model="part">
                    <option value="">
                        Whole glossary
                    </option>
                    <optgroup label="Volumes">
                        <option v-for="volume in volumes" :key="volume.value" :value="volume.value">
                            {{ volume.label }}
                        </option>
                    </optgroup>
                    <optgroup label="Letters">
                        <option v-for="letter in letters" :key="letter" :value="`letter=${encodeURIComponent(letter)}`">
                            Letter {{ letter }}
                        </option>
                    </optgroup>
                </select>
                <DocumentDownload :href="`/api/glossary/export/glossary${part ? `?${part}` : ''}`"/>
            </span>
        </div>
        <SearchExplorer v-model="query"/>
        <template v-if="!query.trim()">
            <nav class="letters serif" aria-label="Jump to a letter">
                <a
                    v-for="[letter] in groups"
                    :key="letter"
                    :href="`#${encodeURIComponent(`letter-${letter}`)}`"
                >{{ letter }}</a>
            </nav>
            <table class="roots">
                <thead>
                    <tr>
                        <th scope="col" class="root">
                            Root
                        </th>
                        <th scope="col" class="stems">
                            Stems and forms
                        </th>
                        <th scope="col">
                            First meaning
                        </th>
                        <th scope="col" class="num examples">
                            Examples
                        </th>
                        <th scope="col" class="num suggestions">
                            Suggestions
                        </th>
                        <th scope="col" class="num open">
                            Undecided
                        </th>
                    </tr>
                </thead>
                <tbody v-for="[letter, items] in groups" :id="`letter-${letter}`" :key="letter">
                    <tr class="letter-row">
                        <th colspan="6" scope="colgroup" class="serif">
                            {{ letter }}
                        </th>
                    </tr>
                    <tr v-for="root in items" :key="root.id">
                        <td class="root serif">
                            <NuxtLink :to="entryHref(root.id)">
                                <span v-text="root.root"></span>
                            </NuxtLink>
                        </td>
                        <td class="stems" :title="stemsLabel(root)">
                            {{ stemsLabel(root) }}
                        </td>
                        <td class="gloss" :title="root.glossPreview">
                            <span v-if="root.proposed" class="new">Suggested new verb.</span>
                            {{ root.glossPreview }}
                        </td>
                        <td class="num examples">
                            {{ root.exampleCount || "" }}
                        </td>
                        <td class="num suggestions">
                            {{ root.proposalCount || "" }}
                        </td>
                        <td class="num open">
                            {{ undecided(root) || "" }}
                        </td>
                    </tr>
                </tbody>
            </table>
        </template>
        <p v-if="error" class="error">
            The glossary could not be loaded. Please try again.
        </p>
    </div>
</template>

<script setup lang="ts">
import type { IRootIndexRow } from '#shared/types/IRootIndexRow'
import { entryHref } from '#shared/utils/entryHref'
import { rootLetter } from '#shared/utils/rootLetter'
import { volumeLabel } from '#shared/utils/volumeLabel'

const route = useRoute()
const router = useRouter()
const query = ref(String(route.query.q || ''))
watch(query, value => router.replace({ query: value ? { q: value } : {} }))
watch(() => route.query.q, (value) => {
    query.value = String(value || '')
})
const {
    data,
    error,
} = await useFetch('/api/glossary/roots')
const roots = computed(() => data.value || [])
// Counted on the server, which ignores decisions on suggestions no longer in the data.
const { data: undecidedByEntry } = await useFetch('/api/glossary/proposals/undecided')
function undecided(root: IRootIndexRow) {
    return undecidedByEntry.value?.[root.id] || 0
}
function stemsLabel(root: IRootIndexRow) {
    return root.stems.map(stem => `${stem.stem} ${stem.forms}`.trim()).join(' · ')
}
// Downloads: the whole glossary, one of the team's Word volumes or one letter, without suggestions.
const part = ref('')
const volumes = computed(() => [...new Set(roots.value.filter(root => !root.proposed).map(root => root.volume))]
    .map(volume => ({
        value: `volume=${/^\d+/u.exec(volume)?.[0] || ''}`,
        label: volumeLabel(volume),
    })))
const letters = computed(() => [...new Set(roots.value.filter(root => !root.proposed)
    .map(root => rootLetter(root.root)))])
const groups = computed(() => {
    const map = new Map<string, IRootIndexRow[]>()
    for (const root of roots.value) {
        const letter = rootLetter(root.root)
        map.set(letter, [...(map.get(letter) || []), root])
    }
    return [...map.entries()]
})
useHead({ title: 'Glossary' })
</script>

<style scoped>
.glossary-export {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.25rem 0.6rem;
  margin-left: auto;
}
.glossary-export select {
  padding: 0.1rem 0.4rem;
}
.letters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.1rem 0.75rem;
  margin: 0.75rem 0;
  font-size: 1.125rem;
}
.letters a {
  text-decoration: none;
}
.letters a:hover {
  text-decoration: underline;
}
.roots {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  font-size: 0.9375rem;
}
.roots th,
.roots td {
  overflow: hidden;
  padding: 0.12rem 0.75rem 0.12rem 0;
  border-bottom: 1px solid var(--rule);
  text-align: left;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: baseline;
}
.roots thead th {
  color: var(--muted);
  font-size: 0.8125rem;
  font-weight: 600;
}
.roots .num {
  text-align: right;
}
.letter-row th {
  padding-top: 0.75rem;
  border-bottom: 2px solid var(--ink);
  font-size: 1.25rem;
  font-weight: 700;
}
.root {
  width: 8rem;
}
td.root {
  font-size: 1.0625rem;
}
td.root a {
  text-decoration: none;
}
td.root a:hover {
  text-decoration: underline;
}
.stems {
  width: 24%;
}
td.stems {
  font-family: var(--font-serif);
  font-style: italic;
  font-size: 1rem;
}
.examples,
.suggestions,
.open {
  width: 6.5rem;
}
td.suggestions {
  color: var(--muted);
}
td.open {
  font-weight: 600;
}
.new {
  color: var(--addition);
  font-weight: 600;
}
tbody tr:not(.letter-row):hover {
  background: var(--bg-soft);
}
@media (max-width: 760px) {
  /* Zero width rather than display: none, which would misalign the fixed layout's letter rows. */
  .roots .stems,
  .roots .examples,
  .roots .suggestions {
    width: 0;
    padding: 0;
    visibility: hidden;
  }
  .root {
    width: 5.5rem;
  }
  .open {
    width: 5.75rem;
  }
}
</style>
