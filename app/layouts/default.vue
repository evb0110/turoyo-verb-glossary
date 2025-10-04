<template>
  <div class="min-h-screen bg-background text-foreground pb-6">
    <header class="sticky top-0 z-40 border-b border-gray-200/60 bg-white/70 backdrop-blur dark:border-gray-800/60 dark:bg-gray-950/70">
      <UContainer class="flex items-center justify-between gap-4 py-4 max-w-5xl mx-auto ">
        <NuxtLink to="/" class="flex items-center gap-2 font-semibold text-lg whitespace-nowrap">
          <UIcon name="i-heroicons-book-open" class="h-6 w-6 text-primary" />
          <span>Turoyo Verb Glossary</span>
        </NuxtLink>
        <div v-if="stats" class="flex gap-3 text-xs text-muted whitespace-nowrap">
          <span>{{ stats.total_verbs }} verbs</span>
          <span>•</span>
          <span>{{ stats.total_stems }} stems</span>
          <span>•</span>
          <span>{{ stats.total_examples }} examples</span>
        </div>
      </UContainer>
    </header>

    <main class="pb-6">
      <UContainer>
        <slot />
      </UContainer>
    </main>
  </div>
</template>


<script setup lang="ts">
const { loadIndex, loadStatistics } = useVerbs()

const { data: stats } = await useAsyncData('layout-stats', async () => {
  await loadIndex()
  return await loadStatistics()
})
</script>