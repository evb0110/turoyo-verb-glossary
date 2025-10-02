<template>
  <div class="p-6 space-y-6">
    <UCard>
      <template #header>
        <h1 class="text-2xl font-semibold">{{ verb?.root }}</h1>
      </template>

      <p v-if="!verb">Loading…</p>
      <div v-else class="space-y-4">
        <div v-if="verb.etymology" class="text-sm">
          <p><strong>Source:</strong> {{ verb.etymology.source }}</p>
          <p v-if="verb.etymology.meaning"><strong>Meaning:</strong> {{ verb.etymology.meaning }}</p>
        </div>

        <UAccordion :items="stemItems" multiple>
          <template #default="{ item }">
            <UCard :ui="{ body: 'space-y-2' }">
              <h3 class="font-semibold">Binyan {{ item.binyan }}</h3>
              <p class="text-sm text-muted">{{ item.forms.join(', ') }}</p>
            </UCard>
          </template>
        </UAccordion>
      </div>
    </UCard>

    <div>
      <UButton to="/" variant="ghost" icon="i-heroicons-arrow-left-circle">Back</UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { getVerbWithCrossRef } = useVerbs()

const root = computed(() => route.params.root as string)
const { data: verb } = await useAsyncData(`verb-${root.value}`, () => getVerbWithCrossRef(root.value))

const stemItems = computed(() => {
  if (!verb.value) return []
  return verb.value.stems.map(s => ({ ...s }))
})
</script>

