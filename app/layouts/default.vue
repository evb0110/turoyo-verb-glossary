<template>
    <div class="min-h-screen bg-background text-foreground pb-6">
        <header
            class="sticky top-0 z-40 border-b border-gray-200/60 bg-white/70 backdrop-blur dark:border-gray-800/60 dark:bg-gray-950/70">
            <UContainer class="flex items-center justify-between gap-4 py-4 max-w-5xl mx-auto ">
                <NuxtLink to="/" class="flex items-center gap-2 font-semibold text-lg whitespace-nowrap">
                    <UIcon name="i-heroicons-book-open" class="h-6 w-6 text-primary"/>
                    <span>Turoyo Verb Glossary</span>
                </NuxtLink>
                <div class="flex gap-3 text-xs text-muted whitespace-nowrap">
                    <span>{{ displayStats.total_verbs }} verbs</span>
                    <span>•</span>
                    <span>{{ displayStats.total_stems }} stems</span>
                    <span>•</span>
                    <span>{{ displayStats.total_examples }} examples</span>
                </div>
            </UContainer>
        </header>
        
        <main class="pb-6">
            <UContainer>
                <slot/>
            </UContainer>
        </main>
    </div>
</template>


<script setup lang="ts">
const { loadIndex, loadStatistics } = useVerbs()

const { data: stats } = await useAsyncData('layout-stats', async () => {
  if (process.server && process.env.VERCEL_URL) {
    try {
      const origin = `https://${process.env.VERCEL_URL}`
      const s = await $fetch(`${origin}/appdata/api/statistics.json`)
      if (process.server) console.info('[layout] SSR stats from VERCEL_URL statistics.json')
      return s
    } catch (e) {
      try {
        const origin = `https://${process.env.VERCEL_URL}`
        const idx: any = await $fetch(`${origin}/appdata/api/index.json`)
        const roots: any[] = idx?.roots || []
        const computed = {
          total_verbs: idx?.total_verbs ?? roots.length,
          total_stems: roots.reduce((sum, r) => sum + ((r.stems || []).length), 0),
          total_examples: roots.reduce((sum, r) => sum + (r.example_count || 0), 0)
        }
        if (process.server) console.info('[layout] SSR stats computed from VERCEL_URL index.json')
        return computed
      } catch {}
    }
  }
  try {
    const s = await loadStatistics()
    if (process.server) console.info('[layout] SSR stats from statistics.json', s)
    return s
  } catch (e) {
    if (process.server) console.warn('[layout] SSR stats fallback from index.json', e)
    const idx: any = await loadIndex()
    const roots: any[] = idx?.roots || []
    const computed = {
      total_verbs: idx?.total_verbs ?? roots.length,
      total_stems: roots.reduce((sum, r) => sum + ((r.stems || []).length), 0),
      total_examples: roots.reduce((sum, r) => sum + (r.example_count || 0), 0)
    }
    if (process.server) console.info('[layout] SSR stats computed', computed)
    return computed
  }
})

const displayStats = computed(() => {
    const s: any = stats.value || { total_verbs: '—', total_stems: '—', total_examples: '—' };
    return s;
});

// No client-time mutation to avoid hydration mismatches; SSR must provide stats
</script>