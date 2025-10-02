<template>
  <div class="space-y-6">
    <UCard>
      <template #header>
        <div class="flex flex-col gap-3">
          <div class="flex items-center justify-between gap-4">
            <div>
              <h1 class="text-3xl font-semibold tracking-tight">
                {{ verb?.root }}
              </h1>
              <p v-if="verb?.etymology?.meaning" class="text-muted">
                {{ verb.etymology.meaning }}
              </p>
            </div>

            <div class="flex items-center gap-2">
              <UBadge v-if="verb?.uncertain" color="amber" variant="soft">
                Uncertain
              </UBadge>
              <UBadge v-if="verb?.cross_reference" color="primary" variant="soft">
                Cross-reference
              </UBadge>
            </div>
          </div>

          <div v-if="verb?.cross_reference" class="rounded-lg border px-4 py-3 bg-muted/10">
            <p class="text-sm text-muted">
              See related entry:
              <NuxtLink :to="`/verbs/${verb.cross_reference}`" class="font-medium text-primary">
                {{ verb.cross_reference }}
              </NuxtLink>
            </p>
          </div>
        </div>
      </template>

      <div v-if="verb?.etymology" class="grid gap-6 md:grid-cols-2">
        <div class="space-y-2">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-muted">
            Etymology
          </h2>
          <div class="space-y-2 text-sm">
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
        </div>

        <div class="space-y-2">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-muted">
            Summary
          </h2>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="rounded-lg border px-3 py-2">
              <p class="text-muted">Binyanim</p>
              <p class="text-lg font-semibold">
                {{ verb?.stems.length || 0 }}
              </p>
            </div>
            <div class="rounded-lg border px-3 py-2">
              <p class="text-muted">Examples</p>
              <p class="text-lg font-semibold">
                {{ totalExamples }}
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

      <UAccordion :items="stemItems" multiple>
        <template #default="{ item }">
          <UCard class="border border-transparent hover:border-primary/50 transition" :ui="{ body: 'space-y-4' }">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-semibold">
                  Binyan {{ item.binyan }}
                </h3>
                <p class="text-sm text-muted">{{ item.forms.join(', ') || 'No recorded forms' }}</p>
              </div>
              <UBadge color="gray" variant="soft">
                {{ item.exampleCount }} examples
              </UBadge>
            </div>

            <div v-for="(examples, group) in item.conjugations" :key="group" class="space-y-3">
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-chevron-right" class="h-4 w-4 text-primary" />
                <h4 class="font-medium">{{ group }}</h4>
              </div>

              <div class="space-y-3">
                <UCard
                  v-for="(example, index) in examples"
                  :key="`${group}-${index}`"
                  variant="ghost"
                  class="border-l-4 border-primary/40"
                  :ui="{ body: 'space-y-2' }"
                >
                  <div class="text-lg font-medium font-[\'SBL BibLit\',serif]">
                    {{ example.turoyo || '—' }}
                  </div>

                  <div v-if="example.translations?.length" class="space-y-1">
                    <p class="text-xs font-semibold uppercase text-muted">Translations</p>
                    <ul class="text-sm list-disc list-inside space-y-1">
                      <li v-for="(translation, tIndex) in example.translations" :key="tIndex">
                        {{ translation }}
                      </li>
                    </ul>
                  </div>

                  <div v-if="example.references?.length" class="space-y-1">
                    <p class="text-xs font-semibold uppercase text-muted">References</p>
                    <div class="flex flex-wrap gap-1">
                      <UBadge v-for="(reference, rIndex) in example.references" :key="rIndex" variant="soft">
                        {{ reference }}
                      </UBadge>
                    </div>
                  </div>
                </UCard>
              </div>
            </div>
          </UCard>
        </template>
      </UAccordion>
    </div>

    <div class="flex justify-end">
      <UButton to="/" variant="ghost" icon="i-heroicons-arrow-left-circle">
        Back to verb list
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Verb } from '~/composables/useVerbs'

const route = useRoute()
const { getVerbWithCrossRef } = useVerbs()

const root = computed(() => route.params.root as string)

const { data: verb, pending, error } = await useAsyncData(
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
    return sum + Object.values(stem.conjugations || {}).reduce((inner, examples) => inner + examples.length, 0)
  }, 0)
})

const stemItems = computed(() => {
  if (!verb.value) return []

  return verb.value.stems.map(stem => ({
    ...stem,
    exampleCount: Object.values(stem.conjugations || {}).reduce((count, examples) => count + examples.length, 0)
  }))
})

useHead({
  title: () => verb.value ? `${verb.value.root} · Turoyo Verb Glossary` : 'Turoyo Verb Glossary',
  meta: [
    {
      name: 'description',
      content: verb.value?.etymology?.meaning || 'Detailed view of a Turoyo verb'
    }
  ]
})
</script>

<style scoped>
.verb-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #dc2626;
}

.verb-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.root {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.badge.uncertain {
  background-color: #fef3c7;
  color: #92400e;
}

.cross-reference {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #eff6ff;
  border-left: 4px solid #3b82f6;
  border-radius: 0.375rem;
}

.cross-reference a {
  color: #2563eb;
  font-weight: 600;
  text-decoration: none;
}

.cross-reference a:hover {
  text-decoration: underline;
}

.etymology {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
}

.etymology h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #374151;
}

.etymology dl {
  display: grid;
  gap: 0.75rem;
}

.etymology dl > div {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 1rem;
}

.etymology dt {
  font-weight: 600;
  color: #6b7280;
}

.etymology dd {
  color: #1f2937;
}

.stems {
  margin-bottom: 2rem;
}

.stems > h2 {
  font-size: 1.75rem;
  margin-bottom: 1.5rem;
  color: #111827;
}

.stem {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

.binyan {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #4f46e5;
}

.forms {
  margin-bottom: 1.5rem;
}

.forms h4 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #374151;
}

.forms ul {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  list-style: none;
  padding: 0;
}

.forms li {
  padding: 0.25rem 0.75rem;
  background-color: #f3f4f6;
  border-radius: 0.375rem;
  font-family: 'SBL BibLit', serif;
  font-size: 1.1rem;
}

.conjugations {
  margin-top: 1.5rem;
}

.conjugation-type {
  margin-bottom: 1.5rem;
}

.conjugation-type h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1f2937;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.example {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #fafafa;
  border-left: 3px solid #8b5cf6;
  border-radius: 0.25rem;
}

.turoyo {
  font-family: 'SBL BibLit', serif;
  font-size: 1.25rem;
  line-height: 1.6;
  margin-bottom: 0.75rem;
  color: #111827;
}

.translations, .references {
  margin-top: 0.75rem;
}

.translations strong, .references strong {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.translations ul, .references ul {
  list-style: disc;
  padding-left: 1.5rem;
}

.translations li, .references li {
  margin-bottom: 0.25rem;
  color: #374151;
  line-height: 1.5;
}

.verb-nav {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.verb-nav a {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}

.verb-nav a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .verb-detail {
    padding: 1rem;
  }

  .root {
    font-size: 2rem;
  }

  .etymology dl > div {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }
}
</style>
