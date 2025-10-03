<template>
  <div class="min-h-screen bg-background text-foreground pb-6">
    <header class="sticky top-0 z-40 border-b border-gray-200/60 bg-white/70 backdrop-blur dark:border-gray-800/60 dark:bg-gray-950/70">
      <UContainer class="flex items-center justify-between gap-4 py-4">
        <NuxtLink to="/" class="flex items-center gap-2 font-semibold text-lg">
          <UIcon name="i-heroicons-book-open" class="h-6 w-6 text-primary" />
          <span>Turoyo Verb Glossary</span>
        </NuxtLink>

        <ColorScheme>
          <template #default="{ toggle, icon }">
            <UButton variant="ghost" :icon="icon" @click="toggle" />
          </template>
        </ColorScheme>
      </UContainer>
    </header>

    <main class="pb-6">
      <UContainer>
        <slot />
      </UContainer>
    </main>
  </div>
</template>


