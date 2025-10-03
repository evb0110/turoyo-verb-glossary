<template>
  <div class="space-y-6 p-6">
    <div class="flex justify-end">
            <UButton to="/" variant="ghost" icon="i-heroicons-arrow-left-circle">
              Back to verb list
            </UButton>
          </div>
    <UCard>
      <template #header>
        <div class="flex flex-col gap-4">

          <div class="flex flex-wrap items-start justify-between gap-4">
            <div class="space-y-1">
              <h1 class="text-3xl font-semibold tracking-tight turoyo-text">
                {{ verb?.root }}
              </h1>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <UBadge v-if="verb?.uncertain" variant="soft">
                Uncertain
              </UBadge>
              <UBadge v-if="verb?.cross_reference" variant="soft">
                Cross-reference
              </UBadge>
            </div>
          </div>

          <div v-if="verb?.cross_reference" class="rounded-lg border px-4 py-3 text-sm">
            See related entry
            <NuxtLink :to="`/verbs/${rootToSlug(verb.cross_reference)}`" class="font-medium">
              {{ verb.cross_reference }}
            </NuxtLink>
          </div>
        </div>
      </template>

      <div v-if="hasEtymologyDetails || etymologyText" class="space-y-2">
        <div class="space-y-2 text-sm">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-muted">
            Etymology
          </h2>
          <p v-if="etymologyText">
            {{ etymologyText }}
          </p>
          <template v-else>
            <p v-if="verb?.etymology?.source">
              <span class="font-medium">Source:</span>
              {{ verb?.etymology?.source }}
            </p>
            <p v-if="verb?.etymology?.source_root">
              <span class="font-medium">Source root:</span>
              {{ verb?.etymology?.source_root }}
            </p>
            <p v-if="verb?.etymology?.reference">
              <span class="font-medium">Reference:</span>
              {{ verb?.etymology?.reference }}
            </p>
          </template>
        </div>
      </div>
    </UCard>

    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold">Stems</h2>
      </div>

      <div class="space-y-4">
        <UCard
          v-for="item in stemItems"
          :key="item.stem"
          class="border border-transparent transition hover:border-primary/40"
          :ui="{ body: 'space-y-4' }"
        >
          <template v-if="item.label_gloss_tokens?.length || item.label_raw">
            <div class="prose max-w-none text-sm">
              <div class="font-semibold">
                {{ `${item.stem}: ${item.forms?.length ? item.forms.join('/') : 'No recorded forms'}` }}
              </div>
              <div v-if="item.label_gloss_tokens?.length">
                <span
                  v-for="(t, i) in item.glossTokens"
                  :key="i"
                  :class="{ italic: t.italic }"
                >
                  {{ t.text }}
                </span>
              </div>
              <div v-else-if="item.label_raw" v-html="item.label_raw"></div>
            </div>
          </template>
          <template v-else>
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 class="text-lg font-semibold">Stem {{ item.stem }}</h3>
                <p class="text-sm text-muted">
                  {{ item.forms.join(', ') || 'No recorded forms' }}
                </p>
              </div>
            </div>
          </template>

          <div v-if="item.conjugationGroups.length" class="space-y-4">
            <div
              v-for="group in item.conjugationGroups"
              :key="group.name"
              class="space-y-3"
            >
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-book-open" class="h-4 w-4" />
                <h4 class="font-medium">{{ group.name }}</h4>
              </div>

              <div class="grid gap-3">
                <UCard
                  v-for="(example, index) in group.examples"
                  :key="`${group.name}-${index}`"
                  variant="soft"
                  class="border-l-4 border-primary/40"
                  :ui="{ body: 'space-y-3' }"
                >
                  <div class="text-lg font-medium turoyo-text">
                    {{ example.turoyo || '—' }}
                  </div>

                  <div v-if="example.translations?.length" class="space-y-1 text-sm">
                    <ul class="list-disc space-y-1 pl-4">
                      <li v-for="(translation, tIndex) in example.translations" :key="tIndex">
                        {{ translation }}
                      </li>
                    </ul>
                  </div>

                  <div v-if="example.references?.length" class="space-y-1 text-xs">
                    <div class="flex flex-wrap gap-1">
                      <UBadge v-for="(ref, rIndex) in example.references.filter(r => r && r.trim().length)" :key="rIndex" variant="soft">
                        {{ ref }}
                      </UBadge>
                    </div>
                  </div>
                </UCard>
              </div>
            </div>
          </div>
          <p v-else class="text-sm text-muted">No examples available.</p>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { getVerbWithCrossRef, slugToRoot, rootToSlug } = useVerbs()

const root = computed(() => route.params.root as string)

const { data: verb, error } = await useAsyncData(
  `verb-${root.value}`,
  () => getVerbWithCrossRef(root.value)
)

if (error.value) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Verb not found'
  })
}

const hasEtymologyDetails = computed(() => {
  const e = verb.value?.etymology as any
  return !!e && !!(e.source || e.source_root || e.reference || e.meaning || e.raw)
})

const etymologyText = computed(() => {
  const e: any = verb.value?.etymology
  if (e?.raw) return e.raw
  const tokens: any[] = (verb.value as any)?.lemma_header_tokens || []
  if (Array.isArray(tokens) && tokens.length) {
    const joined = tokens.map(t => t.text).join('')
    const start = joined.indexOf('(')
    if (start !== -1) {
      let depth = 0
      let end = -1
      for (let i = start; i < joined.length; i++) {
        const ch = joined[i]
        if (ch === '(') depth++
        else if (ch === ')') {
          depth--
          if (depth === 0) { end = i; break }
        }
      }
      const inner = end !== -1 ? joined.slice(start + 1, end).trim() : joined.slice(start + 1).trim()
      if (inner) return `(${inner})`
    }
  }
  if (e && (e.source || e.source_root || e.reference || e.meaning)) {
    const parts = [
      e.source,
      e.source_root,
      e.reference ? `cf. ${e.reference}` : undefined,
    ].filter(Boolean)
    const head = parts.filter(Boolean).join(' ')
    return head + (e.meaning ? `: ${e.meaning}` : '')
  }
  return ''
})

const totalExamples = computed(() => {
  if (!verb.value) return 0
  return verb.value.stems.reduce((sum, stem) => {
    return sum + Object.values(stem.conjugations || {}).reduce((count, examples) => count + examples.length, 0)
  }, 0)
})

const totalForms = computed(() => {
  if (!verb.value) return 0
  return verb.value.stems.reduce((sum, stem) => sum + (stem.forms?.length || 0), 0)
})

const stemItems = computed(() => {
  if (!verb.value) return []

  return verb.value.stems.map(stem => {
    const conjugationGroups = Object.entries(stem.conjugations || {}).map(([name, examples]) => ({
      name,
      examples
    }))

    return {
      ...stem,
      exampleCount: conjugationGroups.reduce((count, group) => count + group.examples.length, 0),
      conjugationGroups,
      glossTokens: Array.isArray((stem as any).label_gloss_tokens)
        ? (stem as any).label_gloss_tokens.filter((t: any, idx: number, arr: any[]) => {
            const first = arr[0]?.text?.trim?.() || ''
            if (idx === 0 && /^[IVX]+\s*:/.test(first)) return false
            return true
          })
        : []
    }
  })
})

useHead({
  title: () => (verb.value ? `${verb.value.root} · Turoyo Verb Glossary` : 'Turoyo Verb Glossary'),
  meta: [
    {
      name: 'description',
      content: verb.value?.etymology?.meaning || 'Detailed view of a Turoyo verb'
    }
  ]
})
</script>
