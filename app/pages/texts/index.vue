<template>
    <div>
        <div class="page-head">
            <h1>Texts</h1>
            <label for="text-filter" class="sr-only">Filter texts</label>
            <input
                id="text-filter"
                v-model="filter"
                type="search"
                class="filter"
                placeholder="Filter by title, speaker, place, collection or number"
                autocomplete="off"
            />
            <span class="small muted" role="status">{{ countLabel }}</span>
        </div>
        <nav v-if="collections.length > 1" class="collections small" aria-label="Collections">
            <a
                v-for="[collection, items] in collections"
                :key="collection"
                :href="`#${collectionId(collection)}`"
            >{{ collection }} <span class="muted">({{ items.length }})</span></a>
        </nav>
        <p v-if="error" class="error">
            Texts could not be loaded. Please try again.
        </p>
        <table v-if="collections.length" class="texts">
            <thead>
                <tr>
                    <th scope="col" class="cite">
                        No.
                    </th>
                    <th scope="col">
                        Title
                    </th>
                    <th scope="col" class="speaker">
                        Speaker/place
                    </th>
                    <th scope="col" class="num verses">
                        Verses
                    </th>
                    <th scope="col" class="translation">
                        Translation
                    </th>
                    <th scope="col" class="verbs">
                        Verbs
                    </th>
                </tr>
            </thead>
            <tbody v-for="[collection, items] in collections" :id="collectionId(collection)" :key="collection">
                <tr class="collection-row">
                    <th colspan="6" scope="colgroup">
                        {{ collection }}
                        <DocumentDownload
                            class="collection-export"
                            :href="`/api/glossary/export/collection?collection=${encodeURIComponent(collection)}`"
                            :label="`All ${collectionSize(collection)} texts`"
                        />
                    </th>
                </tr>
                <tr v-for="text in items" :key="text.id">
                    <td class="cite">
                        {{ text.cite }}
                    </td>
                    <td class="title">
                        <NuxtLink :to="`/texts/${encodeURIComponent(text.id)}`">
                            <span v-text="text.title || `Text ${text.cite}`"></span>
                        </NuxtLink>
                    </td>
                    <td class="speaker">
                        {{ text.speakerPlace }}
                    </td>
                    <td class="num verses">
                        {{ text.verses }}
                    </td>
                    <td class="translation" :class="{ machine: text.translationSource === 'machine' }">
                        {{ translation(text) }}
                    </td>
                    <td class="verbs" :class="text.reading">
                        {{ text.reading === "read" ? "analysed" : text.reading === "partial" ? "partly" : "not yet" }}
                    </td>
                </tr>
            </tbody>
        </table>
        <p v-else-if="!error" class="empty">
            No matching texts.
        </p>
    </div>
</template>

<script setup lang="ts">
import type { ITextIndex } from '#shared/types/ITextIndex'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

const route = useRoute()
const router = useRouter()
const {
    data,
    error,
} = await useFetch('/api/glossary/texts')
const texts = computed(() => data.value || [])
const filter = ref(String(route.query.q || ''))
// Keep the filter in the URL, so Back from a text returns to the same list.
watch(filter, value => router.replace({ query: value ? { q: value } : {} }))
const searchable = computed(() => new Map(texts.value.map(text => [
    text.id,
    normalizeTuroyo(`${text.title} ${text.speakerPlace || ''} ${text.collection} ${text.id} ${text.cite}`),
])))
const collections = computed(() => {
    const query = normalizeTuroyo(filter.value.trim())
    const groups = new Map<string, ITextIndex[]>()
    for (const text of texts.value) {
        if (query && !searchable.value.get(text.id)?.includes(query)) continue
        groups.set(text.collection, [...(groups.get(text.collection) || []), text])
    }
    return [...groups.entries()]
})
const countLabel = computed(() => {
    const shown = collections.value.reduce((sum, [, items]) => sum + items.length, 0)
    return shown === texts.value.length ? `${shown} texts` : `${shown} of ${texts.value.length} texts`
})
function collectionSize(collection: string) {
    return texts.value.filter(text => text.collection === collection).length
}
function collectionId(collection: string) {
    return `collection-${collection.replace(/\W+/gu, '-')}`
}
function translation(text: ITextIndex) {
    const language = text.lang === 'GERMAN' ? 'German' : text.lang === 'ENGLISH' ? 'English' : ''
    if (!language) return 'none'
    return text.translationSource === 'machine' ? `${language}, machine` : language
}
useHead({ title: 'Texts' })
</script>

<style scoped>
.filter {
  flex: 1;
  max-width: 32rem;
}
.collections {
  display: flex;
  flex-wrap: wrap;
  gap: 0.1rem 1rem;
  margin-bottom: 0.75rem;
}
.texts {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  font-size: 0.9375rem;
}
.texts th,
.texts td {
  padding: 0.15rem 0.6rem 0.15rem 0;
  border-bottom: 1px solid var(--rule);
  text-align: left;
  vertical-align: baseline;
}
.texts thead th {
  color: var(--muted);
  font-size: 0.8125rem;
  font-weight: 600;
}
.texts thead th.num,
.texts td.num {
  text-align: right;
}
.collection-row th {
  padding-top: 0.9rem;
  border-bottom: 2px solid var(--ink);
  font-size: 1rem;
  font-weight: 600;
}
.collection-export {
  margin-left: 1rem;
}
.cite {
  width: 6rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
.speaker {
  width: 11rem;
  color: var(--muted);
}
.verses {
  width: 4.5rem;
}
.translation {
  width: 9rem;
}
.verbs {
  width: 6rem;
}
.title {
  overflow-wrap: anywhere;
}
.title a {
  text-decoration: none;
}
.title a:hover {
  text-decoration: underline;
}
td.machine {
  color: var(--correction);
}
td.unread,
td.partial {
  color: var(--muted);
}
tbody tr:not(.collection-row):hover {
  background: var(--bg-soft);
}
@media (max-width: 760px) {
  /* Zero width rather than display: none, which would leave the collection rows' extra columns. */
  .texts .speaker,
  .texts .verses,
  .texts .translation {
    width: 0;
    padding: 0;
    overflow: hidden;
    font-size: 0;
    visibility: hidden;
  }
  .cite {
    width: 3.5rem;
  }
  .verbs {
    width: 4.5rem;
  }
}
</style>
