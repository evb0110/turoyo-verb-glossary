<template>
  <div class="space-y-6 p-6">
    <UCard>
      <template #header>
        <div class="flex flex-col gap-4">
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div class="space-y-1">
              <h1 class="text-3xl font-semibold tracking-tight">
                {{ verb?.root }}
              </h1>
              <p v-if="verb?.etymology?.meaning" class="text-sm text-muted">
                {{ verb.etymology.meaning }}
              </p>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <UBadge v-if="verb?.uncertain" color="amber" variant="soft">
                Uncertain
              </UBadge>
              <UBadge v-if="verb?.cross_reference" color="primary" variant="soft">
                Cross-reference
              </UBadge>
              <UBadge color="gray" variant="soft">
                {{ totalExamples }} examples
              </UBadge>
            </div>
          </div>

          <div v-if="verb?.cross_reference" class="rounded-lg border border-primary/30 bg-primary/5 px-4 py-3 text-sm">
            See related entry
            <NuxtLink :to="`/verbs/${verb.cross_reference}`" class="font-medium text-primary">
              {{ verb.cross_reference }}
            </NuxtLink>
          </div>
        </div>
      </template>

      <div v-if="verb?.etymology" class="grid gap-6 md:grid-cols-2">
        <div class="space-y-2 text-sm">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-muted">
            Etymology
          </h2>
          <p v-if="verb.etymology.source">
            <span class="font-medium">Source:</span>
            {{ verb.etymology.source }}
          </p>
          <p v-if="verb.etymology.source_root">
            <span class="font-medium">Source root:</span>
            {{ verb.etymology.source_root }}
          </p>
          <p v-if="verb.etymology.reference">
            <span class="font-medium">Reference:</span>
            {{ verb.etymology.reference }}
          </p>
        </div>

        <div class="space-y-2 text-sm">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-muted">
            Overview
          </h2>
          <div class="grid gap-3 md:grid-cols-2">
            <div class="rounded-lg border px-3 py-2">
              <p class="text-muted">Stems</p>
              <p class="text-lg font-semibold">
                {{ verb?.stems.length || 0 }}
              </p>
            </div>
            <div class="rounded-lg border px-3 py-2">
              <p class="text-muted">Forms</p>
              <p class="text-lg font-semibold">
                {{ totalForms }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </UCard>

    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold">Stems</h2>
        <UBadge variant="soft">{{ verb?.stems.length || 0 }} entries</UBadge>
      </div>

      <div class="space-y-4">
        <UCard
          v-for="item in stemItems"
          :key="item.stem"
          class="border border-transparent transition hover:border-primary/40"
          :ui="{ body: 'space-y-4' }"
        >
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 class="text-lg font-semibold">Stem {{ item.stem }}</h3>
              <p class="text-sm text-muted">
                {{ item.forms.join(', ') || 'No recorded forms' }}
              </p>
            </div>

            <UBadge color="gray" variant="soft">
              {{ item.exampleCount }} examples
            </UBadge>
          </div>

          <div v-if="item.conjugationGroups.length" class="space-y-4">
            <div
              v-for="group in item.conjugationGroups"
              :key="group.name"
              class="space-y-3"
            >
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-book-open" class="h-4 w-4 text-primary" />
                <h4 class="font-medium">{{ group.name }}</h4>
              </div>

              <div class="grid gap-3">
                <UCard
                  v-for="(example, index) in group.examples"
                  :key="`${group.name}-${index}`"
                  variant="ghost"
                  class="border-l-4 border-primary/40"
                  :ui="{ body: 'space-y-3' }"
                >
                  <div class="text-lg font-medium font-['SBL BibLit',serif]">
                    {{ example.turoyo || '—' }}
                  </div>

                  <div v-if="example.translations?.length" class="space-y-1 text-sm">
                    <p class="text-xs font-semibold uppercase text-muted">Translations</p>
                    <ul class="list-disc space-y-1 pl-4">
                      <li v-for="(translation, tIndex) in example.translations" :key="tIndex">
                        {{ translation }}
                      </li>
                    </ul>
                  </div>

                  <div v-if="example.references?.length" class="space-y-1 text-xs">
                    <p class="font-semibold uppercase text-muted">References</p>
                    <div class="flex flex-wrap gap-1">
                      <UBadge v-for="(ref, rIndex) in example.references" :key="rIndex" variant="soft">
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

    <div class="flex justify-end">
      <UButton to="/" variant="ghost" icon="i-heroicons-arrow-left-circle">
        Back to verb list
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { getVerbWithCrossRef } = useVerbs()

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
      conjugationGroups
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
